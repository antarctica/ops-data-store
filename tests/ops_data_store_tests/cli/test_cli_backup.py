import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCliBackupNow:
    """Tests for `backup now`."""

    def test_ok(self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Can backup database and datasets."""
        mocker.patch("ops_data_store.cli.backup.BackupClient.backup", return_value=None)

        result = fx_cli_runner.invoke(app=cli, args=["backup", "now"])

        assert result.exit_code == 0
        assert "Ok. Complete." in result.output
