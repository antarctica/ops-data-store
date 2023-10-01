from importlib.metadata import version

from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCli:
    """Tests for core Typer CLI object."""

    def test_cli(self, fx_cli_runner: CliRunner) -> None:
        """Basic call to CLI exits ok."""
        result = fx_cli_runner.invoke(app=cli)

        assert result.exit_code == 0

    def test_help(self, fx_cli_runner: CliRunner) -> None:
        """The --help global option includes basic app details."""
        result = fx_cli_runner.invoke(app=cli, args=["--help"])

        assert result.exit_code == 0
        assert "Usage: ods-ctl" in result.output
        assert "BAS MAGIC Operations Data Store control CLI." in result.output

    def test_version(self, fx_cli_runner: CliRunner) -> None:
        """The --version global option returns the app package version."""
        result = fx_cli_runner.invoke(app=cli, args=["--version"])

        assert result.exit_code == 0
        assert result.output == f"{version('ops-data-store')}\n"
