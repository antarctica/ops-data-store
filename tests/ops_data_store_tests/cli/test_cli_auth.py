from unittest.mock import patch

import pytest
from pytest_mock import MockFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli


class TestCliAuthCheck:
    """Tests for `auth check` CLI command."""

    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, mocker: MockFixture) -> None:
        """Succeeds when Azure and LDAP are reachable."""
        mocker.patch("ops_data_store.cli.auth.AzureClient", autospec=True)
        mocker.patch("ops_data_store.cli.auth.LDAPClient", autospec=True)

        result = fx_cli_runner.invoke(app=cli, args=["auth", "check"])

        assert "Checking Azure connectivity." in caplog.text
        assert "Azure connectivity ok." in caplog.text
        assert "Checking LDAP connectivity." in caplog.text
        assert "LDAP connectivity ok." in caplog.text

        assert result.exit_code == 0
        assert "Ok. Auth connection successful." in result.output


class TestCliAuthSync:
    """Tests for `auth sync`."""

    def test_sync_cancelled(
        self,
        mocker: MockFixture,
        fx_cli_runner: CliRunner,
        fx_mock_ssc_azure_group_id: str,
        fx_mock_ssc_ldap_group_id: str,
        fx_mock_ssc_eval_result: dict[str, list[str]],
    ) -> None:
        """
        Sync aborts if cancelled by user.

        This test really checks whether the results of the evaluation are handled correctly, so is a partial success.
        """
        mocker.patch("ops_data_store.cli.auth.AzureClient", autospec=True)
        mocker.patch("ops_data_store.cli.auth.LDAPClient", autospec=True)
        with patch("ops_data_store.cli.auth.SimpleSyncClient") as mock_client:
            mock_instance = mock_client.return_value
            mock_instance.evaluate.return_value = fx_mock_ssc_eval_result

            result = fx_cli_runner.invoke(
                app=cli,
                args=["auth", "sync", "-ag", fx_mock_ssc_azure_group_id, "-lg", fx_mock_ssc_ldap_group_id],
                input="n",
            )

        assert result.exit_code == 1
        assert "=== Sync Evaluation ===" in result.output
        assert "Ok. Sync aborted." in result.output

    def test_sync_ok(
        self,
        mocker: MockFixture,
        fx_cli_runner: CliRunner,
        fx_mock_ssc_azure_group_id: str,
        fx_mock_ssc_ldap_group_id: str,
    ):
        """Sync succeeds."""
        mocker.patch("ops_data_store.cli.auth.SimpleSyncClient", autospec=True)

        result = fx_cli_runner.invoke(
            app=cli,
            args=["auth", "sync", "-ag", fx_mock_ssc_azure_group_id, "-lg", fx_mock_ssc_ldap_group_id],
            input="y",
        )

        assert result.exit_code == 0
        assert "Ok. Sync completed." in result.output

    def test_sync_fails(
        self,
        mocker: MockFixture,
        fx_cli_runner: CliRunner,
        fx_mock_ssc_azure_group_id: str,
        fx_mock_ssc_ldap_group_id: str,
    ):
        """Sync fails when error occurs."""
        mocker.patch("ops_data_store.cli.auth.SimpleSyncClient", autospec=True)
        with patch("ops_data_store.cli.auth.SimpleSyncClient") as mock_client:
            mock_instance = mock_client.return_value
            mock_instance.sync.side_effect = RuntimeError("Sync Error.")

            result = fx_cli_runner.invoke(
                app=cli,
                args=["auth", "sync", "-ag", fx_mock_ssc_azure_group_id, "-lg", fx_mock_ssc_ldap_group_id],
                input="y",
            )

        assert result.exit_code == 1
        assert "No. Sync Error. Sync aborted" in result.output
