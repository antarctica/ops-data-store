from __future__ import annotations

import contextlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha1
from pathlib import Path
from shutil import copyfile
from typing import Optional, Union

from ops_data_store.config import Config
from ops_data_store.data import DataClient
from ops_data_store.db import DBClient


@dataclass
class RollingFileStateMeta:
    """Rolling file state internal metadata."""

    max_iterations: int
    iterations: int
    newest_iteration_sha1sum: str
    schema_version: str = "1"
    updated_at: datetime = field(default_factory=lambda: datetime.now(tz=timezone.utc))


@dataclass
class RollingFileStateIteration:
    """Rolling file state iterations metadata."""

    sha1sum: str
    replaces_sha1sum: str
    created_at: datetime
    original_name: str
    sequence: int
    path: Path


@dataclass
class RollingFileState:
    """Metadata for a rolling file set."""

    meta: RollingFileStateMeta
    iterations: dict[str, RollingFileStateIteration] = field(default_factory=dict)
    _logger: logging.Logger = field(default_factory=lambda: logging.getLogger("app"))
    _schema_version: str = "1"

    @staticmethod
    def _encode_json(obj: object) -> Optional[Union[str, dict]]:
        """
        Encode data as JSON for serialisation.

        Most object types can be returned as-is or encoded as strings. Some types should be ignored, such as loggers.
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, logging.Logger):
            return None
        return obj.__dict__

    @staticmethod
    def _decode_json(data: dict) -> tuple[RollingFileStateMeta, dict[str, RollingFileStateIteration]]:
        """
        Decode serialised JSON.

        Converts data to rich types.
        """
        data["meta"]["updated_at"] = datetime.fromisoformat(data["meta"]["updated_at"])
        meta = RollingFileStateMeta(**data["meta"])
        iterations = {
            k: RollingFileStateIteration(
                sha1sum=v["sha1sum"],
                replaces_sha1sum=v["replaces_sha1sum"],
                created_at=datetime.fromisoformat(v["created_at"]),
                original_name=v["original_name"],
                sequence=v["sequence"],
                path=Path(v["path"]),
            )
            for k, v in data["iterations"].items()
        }
        return meta, iterations

    @staticmethod
    def _sha1_file(path: Path) -> str:
        """Calculate SHA1 sum of file at path."""
        with path.open(mode="rb") as file:
            data = file.read()
        return sha1(data).hexdigest()  # noqa: S324 - not used in cryptographic context

    @property
    def iteration_count(self) -> int:
        """Number of iterations."""
        return self.meta.iterations

    @property
    def oldest_iteration(self) -> RollingFileStateIteration:
        """
        Oldest iteration.

        This iteration won't have a replaces_sha1sum value as it's the oldest iteration.
        """
        for iteration in self.iterations.values():
            if iteration.replaces_sha1sum == "":
                return iteration

        msg = "Cannot identify oldest iteration (no interation has an empty replaces_sha1_sum value)."
        raise ValueError(msg)

    @property
    def next_oldest_iteration(self) -> RollingFileStateIteration:
        """
        Iteration before current oldest iteration.

        I.e. if the oldest iteration is abc and iteration def replaces this, return the def iteration.
        """
        for iteration in self.iterations.values():
            if iteration.replaces_sha1sum == self.oldest_iteration.sha1sum:
                return iteration

        msg = "Cannot identify next oldest iteration (no interation has `replaces_sha1_sum` matching oldest iteration)."
        raise ValueError(msg)

    @property
    def newest_iteration(self) -> RollingFileStateIteration:
        """Newest iteration."""
        try:
            return self.iterations[self.meta.newest_iteration_sha1sum]
        except KeyError as e:
            msg = "Cannot identify newest iteration (no interation has `sha1sum` matching newest iteration)."
            raise ValueError(msg) from e

    @property
    def at_max_iterations(self) -> bool:
        """Is the number of iterations equal or greater than the maximum allowed."""
        self._logger.info("Iterations: %s, Max: %s", self.meta.iterations, self.meta.max_iterations)
        return self.meta.iterations >= self.meta.max_iterations

    def remove_oldest_iteration(self) -> None:
        """
        Remove iteration from state.

        To ensure consistency, only the oldest iteration may be removed.

        Once removed, the next oldest iteration is marked as the next oldest and the iterations count updated.
        """
        # noinspection PyUnusedLocal
        next_oldest_sha1 = ""  # PyCharm incorrectly thinks this is unused
        with contextlib.suppress(ValueError):
            next_oldest_sha1 = self.next_oldest_iteration.sha1sum
            self.iterations[next_oldest_sha1].replaces_sha1sum = ""

        del self.iterations[self.oldest_iteration.sha1sum]
        self.meta.iterations = len(self.iterations)

    def add_new_iteration(self, original_path: Path, sequence: int, iteration_path: Path) -> None:
        """
        Add iteration to state.

        `original_path` is the path the original file, `iteration_path` is its location within the backup set.
        `sequence` is an incrementing value representing the order of the iteration in the backup set.
        """
        # noinspection PyUnusedLocal
        replaces_sha1sum = ""  # PyCharm incorrectly thinks this is unused
        with contextlib.suppress(ValueError):
            replaces_sha1sum = self.newest_iteration.sha1sum

        iteration = RollingFileStateIteration(
            sha1sum=self._sha1_file(path=original_path),
            replaces_sha1sum=replaces_sha1sum,
            created_at=datetime.fromtimestamp(original_path.stat().st_ctime, tz=timezone.utc),
            original_name=original_path.name,
            sequence=sequence,
            path=iteration_path,
        )
        self.iterations[iteration.sha1sum] = iteration
        self.meta.newest_iteration_sha1sum = iteration.sha1sum
        self.meta.iterations = len(self.iterations)

    def update_iteration(self, iteration: RollingFileStateIteration) -> None:
        """Update iteration metadata."""
        self.iterations[iteration.sha1sum] = iteration

    @classmethod
    def load(cls: RollingFileState, path: Path) -> RollingFileState:
        """Decode saved state from JSON file."""
        with path.open(mode="r") as file:
            data = json.load(file)

        if data["meta"]["schema_version"] != cls._schema_version:
            msg = f"Unsupported schema version: {data['meta']['schema_version']}"
            raise ValueError(msg)

        meta, iterations = cls._decode_json(data=data)
        return cls(meta, iterations)

    def dump(self, path: Path) -> None:
        """
        Encode state as JSON and save to file.

        This method is inelegant in that we have to postprocess the data to remove private attributes such as `_logger`.
        """
        self.meta.updated_at = datetime.now(tz=timezone.utc)
        data = json.loads(json.dumps(obj=self.__dict__, default=self._encode_json))
        del data["_logger"]
        del data["_schema_version"]

        with path.open(mode="w") as file:
            json.dump(obj=data, fp=file, indent=2)


class RollingFileSet:
    """
    A manager for keeping iterations of a file.

    Used to maintain a fixed maximum number of iterations of a file (e.g. 10). All iterations (versions) form a set,
    with newer iterations replacing older using generic file names (e.g. `file_1`, `file_2`, etc.). A state file records
    original filenames, checksums and timestamps of files in the set alongside internal metadata.

    Generic file names are used to support file system backups that are sensitive to file names, and may cause all
    iterations to be retained rather than a rolling window, with previous backups eventually being overwritten.

    E.g. The last 10 versions of `foo.text` need to be kept for audit or recovery purposes. This class will maintain
    a set of files (`foo_1.text`, `foo_2.text`, etc.), where `foo_1.text` is the oldest version. When a new file is
    added to the set, the oldest file is removed and remaining files renamed (e.g. `foo_2.text` becomes `foo_1.text`).

    Note: This class does not watch files for changes, it must be called manually to register a new iteration.

    Note: This class does check files are valid or monitor for changes over time (e.g. file rot).

    Note: This class does not provide tamper resistance, anyone able to modify the state file can rewrite history.
    """

    def __init__(self, workspace_path: Path, base_name: str, max_iterations: int) -> None:
        """
        Create instance.

        `workspace_path` is the path to where file iterations will be stored.
        `base_name` is the common, generic, name of file iterations in `name.extension` format.
        """
        self.logger = logging.getLogger("app")
        self.logger.info("Creating rolling file set.")

        self._workspace: Path = workspace_path
        self._base_name_stem: str = base_name.split(".")[0]
        self._base_name_ext: str = f".{base_name.split('.')[1]}"
        self._max_iterations: int = max_iterations
        self._state_file: Path = self._workspace.joinpath(f"_{base_name}.state.json")
        self._state_file_schema_version: str = "1"

        self.logger.info("Workspace: %s", self._workspace.resolve())
        self.logger.info("Base file name: %s", self._base_name_stem)
        self.logger.info("Base file extension: %s", self._base_name_ext)
        self.logger.info("Max iterations: %s", self._max_iterations)
        self.logger.info("State file: %s", self._state_file.resolve())
        self.logger.info("State file (schema version): %s", self._state_file_schema_version)

        self._state: RollingFileState = RollingFileState(
            meta=RollingFileStateMeta(
                max_iterations=self._max_iterations,
                iterations=0,
                newest_iteration_sha1sum="",
            )
        )

        self._init_workspace()
        self._init_state()

    @property
    def _oldest_iteration(self) -> RollingFileStateIteration:
        """Return oldest iteration metadata."""
        return self._state.oldest_iteration

    def _init_workspace(self) -> None:
        """Create workspace directory if needed."""
        if not self._workspace.exists():
            self.logger.info("Creating workspace directory.")
            self._workspace.mkdir(parents=True)

        if not self._workspace.is_dir():
            msg = "Workspace path must be a directory."
            self.logger.error(msg)
            raise ValueError(msg)

    def _init_state(self) -> None:
        """Create or load state file."""
        if not self._state_file.exists():
            self.logger.info("Creating state file.")
            self._state.dump(path=self._state_file)

        self.logger.info("Loading state file.")
        self._state = RollingFileState.load(self._state_file)

    def _create_iteration(self, path: Path) -> None:
        """Create a new file iteration."""
        sequence = self._state.iteration_count + 1
        iteration_name = f"{self._base_name_stem}_{sequence}{self._base_name_ext}"
        iteration_path = self._workspace.joinpath(iteration_name)

        self.logger.info("Copying file: %s to: %s", path.resolve(), iteration_path.resolve())
        copyfile(src=path, dst=iteration_path)

        self._state.add_new_iteration(original_path=path, sequence=sequence, iteration_path=iteration_path)
        self._state.dump(path=self._state_file)

    def _unlink_oldest_iteration(self) -> None:
        """Remove the oldest file iteration."""
        iteration = self._oldest_iteration
        self.logger.info("Removing iteration: %s at %s", iteration.sha1sum, iteration.path.resolve())
        iteration.path.unlink()
        self._state.remove_oldest_iteration()
        self._state.dump(path=self._state_file)

    def _decrement_iteration_paths(self) -> None:
        """Rename all iteration paths to use a lower iteration number."""
        self.logger.info("Decrementing iteration paths.")
        for iteration in self._state.iterations.values():
            new_sequence = iteration.sequence - 1
            new_name = f"{self._base_name_stem}_{new_sequence}{self._base_name_ext}"
            new_path = iteration.path.parent.joinpath(new_name)

            self.logger.info("Renaming iteration: %s to: %s", iteration.path.resolve(), new_path)
            iteration.path.rename(new_path)

            iteration.sequence = new_sequence
            iteration.path = new_path
            self._state.update_iteration(iteration=iteration)
        self._state.dump(path=self._state_file)

    def _prune_iterations(self) -> None:
        """Remove the oldest iteration if max iterations exceeded."""
        if not self._state.at_max_iterations:
            self.logger.info("Max iterations not exceeded, no pruning needed.")
            return

        self.logger.info("At or exceeding max iterations, removing oldest iteration.")
        self._unlink_oldest_iteration()
        self._decrement_iteration_paths()

    def add(self, path: Path) -> None:
        """Add iteration of file to set."""
        self.logger.info("File to add: %s", path.resolve())

        if not path.is_file():
            msg = "Path is not a file or does not exist."
            self.logger.error(msg)
            raise ValueError(msg)

        self._prune_iterations()
        self._create_iteration(path=path)


class BackupClient:
    """
    Application backup client.

    A high level manager class for maintaining rolling database and managed dataset backups.
    """

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating backup client.")

        self.db_client = DBClient()
        self.data_client = DataClient()

        self._max_iterations = self.config.BACKUPS_COUNT
        self._backups_path = self.config.BACKUPS_PATH
        self._db_backup_name = "db_backup.sql"
        self._data_backup_name = "managed_datasets_backup.gpkg"

        self._db_backups = RollingFileSet(
            workspace_path=self._backups_path, base_name=self._db_backup_name, max_iterations=self._max_iterations
        )
        self._data_backups = RollingFileSet(
            workspace_path=self._backups_path, base_name=self._data_backup_name, max_iterations=self._max_iterations
        )

    def backup(self) -> None:
        """Create backups and add to file sets."""
        self.logger.info("Creating database backup.")
        db_backup_path = self._backups_path.joinpath(self._db_backup_name)
        self.db_client.dump(path=db_backup_path)
        self._db_backups.add(path=db_backup_path)
        db_backup_path.unlink()
        self.logger.info("Created database backup.")

        self.logger.info("Creating managed dataset backup.")
        data_backup_path = self._backups_path.joinpath(self._data_backup_name)
        self.data_client.export(path=data_backup_path)
        self._data_backups.add(path=data_backup_path)
        data_backup_path.unlink()
        self.logger.info("Created managed dataset backup.")
