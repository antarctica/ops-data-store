import pytest
from pytest_mock import MockFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCliAuthCheck:
    """Tests for `auth check` CLI command."""

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, mocker: MockFixture) -> None:
        """Succeeds when Azure and LDAP are reachable."""
        mocker.patch("ops_data_store.auth.ConfidentialClientApplication", autospec=True)

        result = fx_cli_runner.invoke(app=cli, args=["auth", "check"])

        assert "Checking Azure connectivity." in caplog.text
        assert "Azure connectivity ok." in caplog.text
        assert "Checking LDAP connectivity." in caplog.text
        assert "LDAP connectivity ok." in caplog.text

        assert result.exit_code == 0
        assert "Ok. Auth connection successful." in result.output
