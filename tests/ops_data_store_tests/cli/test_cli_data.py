from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCliDBBackup:
    """Tests for `data backup`."""

    def test_ok(self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Can export datasets."""
        mocker.patch("ops_data_store.cli.data.DataClient.export", return_value=None)

        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)

            result = fx_cli_runner.invoke(app=cli, args=["data", "backup", "--output-path", tmp_file_path])

            assert "Managed datasets exported normally." in caplog.text

            assert result.exit_code == 0
            assert "Ok. Complete." in result.output

    def test_error(self, mocker: MockerFixture, fx_cli_runner: CliRunner) -> None:
        """Displays error when problem occurs."""
        mocker.patch("ops_data_store.cli.data.DataClient.export", side_effect=RuntimeError("Error"))

        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)

            result = fx_cli_runner.invoke(app=cli, args=["data", "backup", "--output-path", tmp_file_path])

            assert result.exit_code == 1
            assert "No. Error saving managed datasets." in result.output
