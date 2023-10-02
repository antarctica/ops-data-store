from importlib.metadata import version
from io import StringIO
from pprint import pprint

from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCli:
    """Tests for `config` Typer CLI group."""

    def test_show(self, fx_cli_runner: CliRunner) -> None:
        """The `show` command returns app config."""
        result = fx_cli_runner.invoke(app=cli, args=["config", "show"])

        # can't use `str(dict)` as output is formatted by pprint in CLI
        output = StringIO()
        pprint({"VERSION": version("ops-data-store")}, stream=output)
        expected = output.getvalue()

        assert result.exit_code == 0
        assert expected in result.output
