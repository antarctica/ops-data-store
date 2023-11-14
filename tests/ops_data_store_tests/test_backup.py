import json
import logging
from copy import copy
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from pytest_mock import MockFixture

from ops_data_store.backup import (
    BackupClient,
    RollingFileSet,
    RollingFileState,
    RollingFileStateIteration,
    RollingFileStateMeta,
)


class TestRollingFileStateMeta:
    """Tests for internal metadata about rolling file set state."""

    def test_init(self, fx_rfs_max_iterations: int) -> None:
        """Can initialise with minimal fields."""
        iterations = 0
        newest_iteration_sha1 = "x"

        metadata = RollingFileStateMeta(
            max_iterations=fx_rfs_max_iterations, iterations=iterations, newest_iteration_sha1sum=newest_iteration_sha1
        )

        assert metadata.max_iterations == fx_rfs_max_iterations
        assert metadata.iterations == iterations
        assert metadata.newest_iteration_sha1sum == newest_iteration_sha1
        assert isinstance(metadata.updated_at, datetime)

    def test_existing_updated_at(self, fx_rfs_max_iterations: int) -> None:
        """Can initialise with existing datetime."""
        updated_at = datetime.now(tz=timezone.utc)

        metadata = RollingFileStateMeta(
            max_iterations=fx_rfs_max_iterations,
            iterations=0,
            newest_iteration_sha1sum="x",
            updated_at=updated_at,
        )

        assert metadata.updated_at == updated_at

    def test_schema_version(self, fx_rfs_meta: RollingFileStateMeta, fx_rfs_schema_version: str) -> None:
        """Can get fixed schema version."""
        assert fx_rfs_meta.schema_version == fx_rfs_schema_version


class TestRollingFileStateIteration:
    """Tests for state information for an iteration in a rolling file set."""

    def test_init(self) -> None:
        """Can initialise with minimal fields."""
        sha1sum = "y"
        replaces_sha1sum = "z"
        created_at = datetime.now(tz=timezone.utc)
        original_name = "o"
        sequence = 0
        path = Path("/foo_1.txt")

        iteration_state = RollingFileStateIteration(
            sha1sum=sha1sum,
            replaces_sha1sum=replaces_sha1sum,
            created_at=created_at,
            original_name=original_name,
            sequence=sequence,
            path=path,
        )

        assert iteration_state.sha1sum == sha1sum
        assert iteration_state.replaces_sha1sum == replaces_sha1sum
        assert iteration_state.created_at == created_at
        assert iteration_state.original_name == original_name
        assert iteration_state.sequence == sequence
        assert iteration_state.path == path


class TestRollingFileState:
    """Tests for rolling file set state information."""

    def test_init(self, fx_rfs_meta: RollingFileStateMeta, fx_rfs_schema_version: str) -> None:
        """Can initialise with minimal fields."""
        state = RollingFileState(meta=fx_rfs_meta)

        assert state._schema_version == fx_rfs_schema_version
        assert isinstance(state.iterations, dict)
        assert len(state.iterations) == 0

    def test_existing_logger(self, fx_rfs_meta: RollingFileStateMeta) -> None:
        """Can initialise with existing logger."""
        logger = logging.getLogger("test")
        state = RollingFileState(meta=fx_rfs_meta, _logger=logger)

        assert state._logger == logger

    def test_schema_version(self, fx_rfs_state: RollingFileState, fx_rfs_schema_version: str) -> None:
        """Can get fixed schema version."""
        assert fx_rfs_state._schema_version == fx_rfs_schema_version

    def test_encode_json_datetime(self, fx_rfs_state: RollingFileState) -> None:
        """Can encode datetime type as JSON."""
        obj = datetime(year=2022, month=4, day=24, hour=4, minute=40, second=1, tzinfo=timezone.utc)
        expected = "2022-04-24T04:40:01+00:00"

        result = fx_rfs_state._encode_json(obj)

        assert result == expected

    def test_encode_json_path(self, fx_rfs_state: RollingFileState) -> None:
        """Can encode Path type as JSON."""
        obj = Path("/foo.txt")
        expected = "/foo.txt"

        result = fx_rfs_state._encode_json(obj)

        assert result == expected

    def test_encode_json_dict(self, fx_rfs_state: RollingFileState) -> None:
        """Can encode dictionary type as JSON."""
        obj = {"foo": "bar"}

        result = fx_rfs_state._encode_json(obj)

        assert result == obj

    def test_decode_json(
        self,
        fx_rfs_state_json: str,
        fx_rfs_meta: RollingFileStateMeta,
        fx_rfs_first_iteration: RollingFileStateIteration,
        fx_rfs_second_iteration: RollingFileStateIteration,
    ) -> None:
        """Can decode JSON encoded state dict."""
        iterations = {
            fx_rfs_first_iteration.sha1sum: fx_rfs_first_iteration,
            fx_rfs_second_iteration.sha1sum: fx_rfs_second_iteration,
        }

        result = RollingFileState._decode_json(data=json.loads(fx_rfs_state_json))

        assert result[0] == fx_rfs_meta
        assert result[1] == iterations

    def test_sha1_file(self, fx_rfs_state: RollingFileState) -> None:
        """Can get SHA1 sum for file."""
        expected = "da39a3ee5e6b4b0d3255bfef95601890afd80709"

        with NamedTemporaryFile(mode="w+") as tmp_file:
            tmp_file.write("test")
            tmp_file_path = Path(tmp_file.name)

            result = fx_rfs_state._sha1_file(tmp_file_path)

        assert result == expected

    def test_iteration_count(self, fx_rfs_state: RollingFileState) -> None:
        """Can get iterations count."""
        assert fx_rfs_state.iteration_count == 2

    def test_oldest_iteration(
        self,
        fx_rfs_state: RollingFileState,
        fx_rfs_first_iteration: RollingFileStateIteration,
        fx_rfs_second_iteration: RollingFileStateIteration,
    ) -> None:
        """Can get oldest iteration."""
        # re-order iterations to ensure oldest is not first so conditional code path is triggered
        fx_rfs_state.iterations = {
            fx_rfs_second_iteration.sha1sum: fx_rfs_second_iteration,
            fx_rfs_first_iteration.sha1sum: fx_rfs_first_iteration,
        }

        assert fx_rfs_state.oldest_iteration == fx_rfs_first_iteration

    def test_oldest_unknown_iteration(self, fx_rfs_meta: RollingFileStateMeta) -> None:
        """Errors when no iterations exist."""
        state = RollingFileState(meta=fx_rfs_meta)

        with pytest.raises(ValueError, match="Cannot identify oldest iteration"):
            # noinspection PyStatementEffect
            state.oldest_iteration  # noqa: B018

    def test_next_oldest_iteration(
        self, fx_rfs_state: RollingFileState, fx_rfs_second_iteration: RollingFileStateIteration
    ) -> None:
        """Can get next oldest iteration."""
        assert fx_rfs_state.next_oldest_iteration == fx_rfs_second_iteration

    def test_next_oldest_iteration_unknown(
        self, fx_rfs_state: RollingFileState, fx_rfs_second_iteration: RollingFileStateIteration
    ) -> None:
        """Errors when meta points to different iteration SHA1sum."""
        fx_rfs_state.iterations[fx_rfs_second_iteration.sha1sum].replaces_sha1sum = "x"

        with pytest.raises(ValueError, match="Cannot identify next oldest iteration"):
            # noinspection PyStatementEffect
            fx_rfs_state.next_oldest_iteration  # noqa: B018

    def test_newest_iteration(
        self, fx_rfs_state: RollingFileState, fx_rfs_second_iteration: RollingFileStateIteration
    ) -> None:
        """
        Can get the newest iteration.

        As this file set only contains 2 iterations, the newest iteration is the same as the next oldest iteration.
        """
        assert fx_rfs_state.newest_iteration == fx_rfs_second_iteration

    def test_newest_iteration_unknown(
        self, fx_rfs_state: RollingFileState, fx_rfs_second_iteration: RollingFileStateIteration
    ) -> None:
        """Errors when meta points to unknown SHA1sum."""
        fx_rfs_state.meta.newest_iteration_sha1sum = "x"

        with pytest.raises(ValueError, match="Cannot identify newest iteration"):
            # noinspection PyStatementEffect
            fx_rfs_state.newest_iteration  # noqa: B018

    def test_at_max_iterations(self, fx_rfs_state: RollingFileState) -> None:
        """Can determine if at max iterations."""
        assert fx_rfs_state.at_max_iterations is False

    def test_remove_oldest_iteration(
        self, fx_rfs_state: RollingFileState, fx_rfs_second_iteration: RollingFileStateIteration
    ) -> None:
        """Can remove oldest iteration."""
        fx_rfs_state.remove_oldest_iteration()

        assert fx_rfs_state.iteration_count == 1
        assert fx_rfs_state.oldest_iteration == fx_rfs_second_iteration

    def test_add_iteration(self, fx_rfs_state: RollingFileState) -> None:
        """Can add iteration."""
        contents = "connie"
        sha1sum = "41a53affe46e1521428fcd2dc4c1450c97605a57"
        sequence = 2
        iteration_path = Path("/foo_3.txt")

        with NamedTemporaryFile(mode="w+") as tmp_file:
            tmp_file.write(contents)
            tmp_file.seek(0)  # reset for reading
            tmp_file_path = Path(tmp_file.name)

            fx_rfs_state.add_new_iteration(
                original_path=tmp_file_path, sequence=sequence, iteration_path=iteration_path
            )

        assert fx_rfs_state.newest_iteration.sha1sum == sha1sum
        assert fx_rfs_state.meta.newest_iteration_sha1sum == sha1sum
        assert fx_rfs_state.iterations[sha1sum].sha1sum == sha1sum
        assert fx_rfs_state.iteration_count == 3

    def test_update_iteration(
        self, fx_rfs_state: RollingFileState, fx_rfs_first_iteration: RollingFileStateIteration
    ) -> None:
        """Can update iteration."""
        updated_iteration = copy(fx_rfs_first_iteration)
        updated_iteration.original_name = "updated.txt"

        fx_rfs_state.update_iteration(iteration=updated_iteration)

        assert fx_rfs_state.iterations[fx_rfs_first_iteration.sha1sum].original_name == updated_iteration.original_name

    def test_load(self, fx_rfs_state: RollingFileState, fx_rfs_state_json: str) -> None:
        """Can load state from JSON."""
        with NamedTemporaryFile(mode="w+") as tmp_file:
            tmp_file.write(fx_rfs_state_json)
            tmp_file.seek(0)  # reset for reading
            tmp_file_path = Path(tmp_file.name)

            state = RollingFileState.load(path=tmp_file_path)

            assert state == fx_rfs_state

    def test_load_wrong_schema_version(self, fx_rfs_state: RollingFileState, fx_rfs_state_json: str) -> None:
        """Errors when load state with wrong schema version."""
        state = json.loads(fx_rfs_state_json)
        state["meta"]["schema_version"] = "0"
        state = json.dumps(state)

        with NamedTemporaryFile(mode="w+") as tmp_file:
            tmp_file.write(state)
            tmp_file.seek(0)  # reset for reading
            tmp_file_path = Path(tmp_file.name)

            with pytest.raises(ValueError, match="Unsupported schema version: 0"):
                RollingFileState.load(path=tmp_file_path)

    def test_dump(self, fx_rfs_state: RollingFileState, fx_rfs_state_json: str) -> None:
        """Can dump state to JSON."""
        with NamedTemporaryFile(mode="w+") as out_file:
            out_file_path = Path(out_file.name)
            fx_rfs_state.dump(path=out_file_path)

            result = out_file.read()

            # hack around not being able to mock datetime.now() to give static time value
            result = json.loads(result)
            result["meta"]["updated_at"] = json.loads(fx_rfs_state_json)["meta"]["updated_at"]
            result = json.dumps(result, indent=2)

            assert result == fx_rfs_state_json


class TestRollingFile:
    """Tests for rolling file set state."""

    def test_init(self, fx_rfs_max_iterations: int, fx_rfs_schema_version: str) -> None:
        """Can initialise with minimal fields."""
        base_stem = "foo"
        base_ext = ".txt"
        base_name = f"{base_stem}{base_ext}"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)

            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )

            assert file_set._state_file.exists() is True

        assert isinstance(file_set, RollingFileSet)

        assert file_set._workspace == workspace_path
        assert file_set._base_name_stem == base_stem
        assert file_set._base_name_ext == base_ext
        assert file_set._max_iterations == fx_rfs_max_iterations
        assert file_set._state_file == workspace_path.joinpath(f"_{base_name}.state.json")
        assert file_set._state_file_schema_version == fx_rfs_schema_version

    def test_init_workspace_not_exist(self, fx_rfs_max_iterations: int) -> None:
        """Creates workspace directory if not present."""
        base_name = "foo.txt"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace).joinpath("foo")

            assert workspace_path.exists() is False

            RollingFileSet(workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations)

            assert workspace_path.exists() is True

    def test_init_workspace_not_dir(self, fx_rfs_max_iterations: int) -> None:
        """Errors if workspace directory is not a directory."""
        base_name = "foo.txt"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace).joinpath("foo.txt")
            workspace_path.touch()

            assert workspace_path.exists() is True
            assert workspace_path.is_file() is True

            with pytest.raises(ValueError, match="Workspace path must be a directory."):
                RollingFileSet(workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations)

    def test_in_state_exists(self, fx_rfs_max_iterations: int, fx_rfs_state_json: str) -> None:
        """Can get oldest iteration."""
        base_name = "foo.txt"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)

            # pre-populate state file
            with workspace_path.joinpath("_foo.txt.state.json").open(mode="w") as state_file:
                state_file.write(fx_rfs_state_json)

            RollingFileSet(workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations)

    def test_oldest_iteration(self, fx_rfs_max_iterations: int, fx_rfs_state_json: str) -> None:
        """Can get oldest iteration."""
        base_name = "foo.txt"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)

            # pre-populate state file
            with workspace_path.joinpath("_foo.txt.state.json").open(mode="w") as state_file:
                state_file.write(fx_rfs_state_json)

            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )

            assert file_set._oldest_iteration is not None

    def test_create_iteration(self, fx_rfs_max_iterations: int) -> None:
        """Can create a new iteration."""
        base_stem = "foo"
        base_ext = ".txt"
        base_name = f"{base_stem}{base_ext}"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            original_file = workspace_path.joinpath("original.txt")
            expected_file = workspace_path.joinpath(f"{base_stem}_1{base_ext}")

            with original_file.open(mode="w") as file:
                file.write("test")

            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )

            file_set._create_iteration(path=original_file)

            assert expected_file.exists() is True
            assert file_set._state.iteration_count == 1

    def test_unlink_oldest_iteration(self, fx_rfs_max_iterations: int):
        """Can remove the oldest iteration."""
        base_stem = "foo"
        base_ext = ".txt"
        base_name = f"{base_stem}{base_ext}"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)

            original_file = workspace_path.joinpath("original.txt")
            expected_file = workspace_path.joinpath(f"{base_stem}_1{base_ext}")

            with original_file.open(mode="w") as file:
                file.write("test")

            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )
            file_set._create_iteration(path=original_file)

            file_set._unlink_oldest_iteration()

            assert expected_file.exists() is False
            assert file_set._state.iteration_count == 0

    def test_decrement_iterations(self, fx_rfs_max_iterations: int) -> None:
        """Can decrement remaining iterations after removing oldest."""
        base_stem = "foo"
        base_ext = ".txt"
        base_name = f"{base_stem}{base_ext}"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )

            # populate with max (three) iterations
            for i in range(1, 4):
                path = workspace_path.joinpath(f"original_{i}.txt")
                with path.open(mode="w") as file:
                    file.write(f"test {i}.")
                file_set._create_iteration(path=path)

            assert workspace_path.joinpath(f"{base_stem}_1{base_ext}").exists() is True
            assert workspace_path.joinpath(f"{base_stem}_2{base_ext}").exists() is True
            assert workspace_path.joinpath(f"{base_stem}_3{base_ext}").exists() is True

            # remove the oldest iteration
            file_set._unlink_oldest_iteration()

            assert workspace_path.joinpath(f"{base_stem}_1{base_ext}").exists() is False
            assert workspace_path.joinpath(f"{base_stem}_2{base_ext}").exists() is True
            assert workspace_path.joinpath(f"{base_stem}_3{base_ext}").exists() is True

            # decrement remaining iterations
            file_set._decrement_iteration_paths()

            assert workspace_path.joinpath(f"{base_stem}_1{base_ext}").exists() is True
            assert workspace_path.joinpath(f"{base_stem}_2{base_ext}").exists() is True
            assert workspace_path.joinpath(f"{base_stem}_3{base_ext}").exists() is False

    def test_prune_iterations_under(self, fx_rfs_max_iterations: int, caplog: pytest.LogCaptureFixture) -> None:
        """Doesn't prune iterations when under max iterations."""
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name="foo.txt", max_iterations=fx_rfs_max_iterations
            )

            file_set._prune_iterations()

            assert "Max iterations not exceeded, no pruning needed." in caplog.text

    def test_prune_iterations_over(self, fx_rfs_max_iterations: int, caplog: pytest.LogCaptureFixture) -> None:
        """Can prune iterations when at maximum iterations."""
        base_stem = "foo"
        base_ext = ".txt"
        base_name = f"{base_stem}{base_ext}"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )

            # populate with max (three) iterations
            for i in range(1, 4):
                path = workspace_path.joinpath(f"original_{i}.txt")
                with path.open(mode="w") as file:
                    file.write(f"test {i}.")
                file_set._create_iteration(path=path)

            file_set._prune_iterations()

            assert "At or exceeding max iterations, removing oldest iteration." in caplog.text

            # with the oldest iteration removed, and file names decremented, the newest iteration should be removed
            assert workspace_path.joinpath(f"{base_stem}_3{base_ext}").exists() is False

    def test_add(self, fx_rfs_max_iterations: int) -> None:
        """Can add new file to file set."""
        base_stem = "foo"
        base_ext = ".txt"
        base_name = f"{base_stem}{base_ext}"
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            original_file = workspace_path.joinpath("original.txt")
            expected_file = workspace_path.joinpath(f"{base_stem}_1{base_ext}")

            with original_file.open(mode="w") as file:
                file.write("test")

            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name=base_name, max_iterations=fx_rfs_max_iterations
            )

            file_set.add(path=original_file)

            assert expected_file.exists() is True
            assert file_set._state.iteration_count == 1

    def test_add_not_file(self, fx_rfs_max_iterations: int) -> None:
        """Errors if not adding a file."""
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            file_set = RollingFileSet(
                workspace_path=workspace_path, base_name="foo.txt", max_iterations=fx_rfs_max_iterations
            )

            with pytest.raises(ValueError, match="Path is not a file or does not exist."):
                file_set.add(path=workspace_path)


class TestBackupClient:
    """Tests for app backups client."""

    def test_init(self, mocker: MockFixture, caplog: pytest.LogCaptureFixture) -> None:
        """Can be initialised."""
        mocker.patch("ops_data_store.backup.DataClient", autospec=True)
        mocker.patch("ops_data_store.backup.DBClient", autospec=True)
        mocker.patch("ops_data_store.backup.RollingFileSet", autospec=True)

        client = BackupClient()

        assert "Creating backup client." in caplog.text

        assert isinstance(client, BackupClient)

    def test_backup(self, mocker: MockFixture, caplog: pytest.LogCaptureFixture, fx_backup_client: BackupClient):
        """Can create backups."""
        with TemporaryDirectory() as workspace:
            fx_backup_client._backups_path = Path(workspace)
            db_backup_path = fx_backup_client._backups_path.joinpath(fx_backup_client._db_backup_name)
            data_backup_path = fx_backup_client._backups_path.joinpath(fx_backup_client._data_backup_name)
            db_backup_path.touch()
            data_backup_path.touch()

            fx_backup_client.backup()

            assert db_backup_path.exists() is False
            assert data_backup_path.exists() is False

        assert "Creating database backup." in caplog.text
        assert "Created database backup." in caplog.text
        assert "Creating managed dataset backup." in caplog.text
        assert "Created managed dataset backup." in caplog.text
