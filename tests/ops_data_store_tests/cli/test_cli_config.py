from io import StringIO
from pprint import pprint

from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCliConfigShow:
    """Tests for `config show` CLI command."""

    def test_ok(self, fx_cli_runner: CliRunner, fx_test_package_version: str, fx_test_db_dsn: str) -> None:
        """Returns app config."""
        result = fx_cli_runner.invoke(app=cli, args=["config", "show"])

        # Can't simply use `str(dict)` as output is formatted by pprint in CLI so will contain new lines etc.
        output = StringIO()
        pprint({"VERSION": fx_test_package_version, "DB_DSN": fx_test_db_dsn}, stream=output)
        expected = output.getvalue()

        assert result.exit_code == 0
        assert expected in result.output
