from unittest.mock import Mock

import pytest
from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCliAuthCheck:
    """Tests for `auth check` CLI command."""

    def test_ok(
        self,
        caplog: pytest.LogCaptureFixture,
        fx_cli_runner: CliRunner,
        fx_mock_msal_confidential_client_application: Mock,
        fx_mock_ldap: Mock,
    ) -> None:
        """Succeeds when Azure and LDAP are reachable."""
        expected_token = "x"  # noqa: S105

        fx_mock_msal_confidential_client_application.return_value.acquire_token_silent.return_value = {
            "access_token": expected_token
        }
        fx_mock_ldap.return_value.verify_bind.return_value = None

        result = fx_cli_runner.invoke(app=cli, args=["auth", "check"])

        assert "Checking Azure connectivity." in caplog.text
        assert f"Access token: {expected_token}" in caplog.text
        assert "Azure connectivity ok." in caplog.text
        assert "Checking LDAP connectivity." in caplog.text
        assert "LDAP connectivity ok." in caplog.text

        assert result.exit_code == 0
        assert "Ok. Auth connection successful." in result.output
