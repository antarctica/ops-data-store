from pathlib import Path
from tempfile import TemporaryDirectory

from ops_data_store.utils import empty_dir


class TestUtils:
    """Test for application utils."""

    def test_empty_dir(self):
        """Can remove files and directories."""
        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)

            workspace_path.joinpath("file.txt").touch()
            workspace_path.joinpath("subdir").mkdir()
            workspace_path.joinpath("subdir", "file.txt").touch()

            empty_dir(path=workspace_path)

            assert workspace_path.exists()
            assert len(list(workspace_path.glob("*/*"))) == 0
