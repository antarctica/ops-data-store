from io import StringIO
from pprint import pprint

import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli
from ops_data_store.config import Config


class TestCliConfigCheck:
    """Tests for `config check` CLI command."""

    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Returns ok message."""
        result = fx_cli_runner.invoke(app=cli, args=["config", "check"])

        assert "Checking app config." in caplog.text
        assert "App config ok." in caplog.text

        assert result.exit_code == 0
        assert "Ok. Configuration valid." in result.output

    def test_invalid(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, mocker: MockerFixture) -> None:
        """Returns error message."""
        mocker.patch.object(
            target=Config, attribute="validate", side_effect=RuntimeError("Required config option `DB_DSN` not set.")
        )

        result = fx_cli_runner.invoke(app=cli, args=["config", "check"])

        assert "Checking app config." in caplog.text
        assert "Required config option `DB_DSN` not set." in caplog.text

        assert result.exit_code == 1
        assert "Required config option `DB_DSN` not set." in result.output


class TestCliConfigShow:
    """Tests for `config show` CLI command."""

    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, fx_test_config_dict: dict) -> None:
        """Returns app config."""
        result = fx_cli_runner.invoke(app=cli, args=["config", "show"])

        # Can't simply use `str(dict)` as output is formatted by pprint in CLI so will contain new lines etc.
        output = StringIO()
        pprint(fx_test_config_dict, stream=output)
        expected = output.getvalue()

        assert "Checking app config." in caplog.text
        assert "App config ok." in caplog.text
        assert "Dumping app config." in caplog.text

        assert result.exit_code == 0
        assert expected in result.output

    def test_invalid_config(
        self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, mocker: MockerFixture
    ) -> None:
        """Returns error message where config is invalid."""
        mocker.patch.object(
            target=Config, attribute="validate", side_effect=RuntimeError("Required config option `DB_DSN` not set.")
        )

        result = fx_cli_runner.invoke(app=cli, args=["config", "show"])

        assert "Checking app config." in caplog.text
        assert "Required config option `DB_DSN` not set." in caplog.text

        assert result.exit_code == 1
        assert "No. Application config is invalid. Check with `ods-ctl config check`." in result.output
