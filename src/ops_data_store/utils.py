from pathlib import Path
from shutil import rmtree


def empty_dir(path: Path) -> None:
    """Remove all files and directories in a directory."""
    for item in path.iterdir():
        if item.is_dir():
            rmtree(item)
        else:
            item.unlink()
