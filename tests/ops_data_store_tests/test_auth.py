from unittest.mock import Mock

import ldap
import pytest

from ops_data_store.auth import AzureClient, LDAPClient


class TestAzureClient:
    """Tests for app Azure client class."""

    def test_init(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_confidential_client_application: Mock) -> None:
        """AzureClient can be initialised."""
        client = AzureClient()

        assert "Creating Azure client." in caplog.text

        assert isinstance(client, AzureClient)

    def test_get_token_silent_ok(
        self, caplog: pytest.LogCaptureFixture, fx_mock_msal_confidential_client_application: Mock
    ) -> None:
        """Can acquire access token using valid cache."""
        expected = "x"
        fx_mock_msal_confidential_client_application.return_value.acquire_token_silent.return_value = {
            "access_token": expected
        }

        client = AzureClient()
        token = client.get_token()

        assert "Attempting to acquire access token silently (from cache)." in caplog.text
        assert f"Access token: {expected}" in caplog.text

        assert token == expected

    def test_get_token_fresh_ok(
        self, caplog: pytest.LogCaptureFixture, fx_mock_msal_confidential_client_application: Mock
    ) -> None:
        """Can acquire access token where cache empty."""
        expected = "x"
        fx_mock_msal_confidential_client_application.return_value.acquire_token_silent.return_value = None
        fx_mock_msal_confidential_client_application.return_value.acquire_token_for_client.return_value = {
            "access_token": expected
        }

        client = AzureClient()
        token = client.get_token()

        assert "Attempting to acquire access token silently (from cache)." in caplog.text
        assert "Failed to acquire token silently, attempting to request fresh token." in caplog.text
        assert f"Access token: {expected}" in caplog.text

        assert token == expected

    def test_get_token_error(
        self, caplog: pytest.LogCaptureFixture, fx_mock_msal_confidential_client_application: Mock
    ) -> None:
        """Can acquire access token where cache empty."""
        expected = {"error": "x", "error_description": "y", "correlation_id": "z"}
        fx_mock_msal_confidential_client_application.return_value.acquire_token_silent.return_value = expected

        client = AzureClient()
        with pytest.raises(RuntimeError) as e:
            client.get_token()

        assert f"Error: {expected['error']}" in caplog.text
        assert f"Error description: {expected['error_description']}" in caplog.text
        assert f"Correlation ID: {expected['correlation_id']}" in caplog.text

        assert str(e.value) == "Failed to acquire Azure token."


class TestLDAPClient:
    """Tests for app LDAP client."""

    def test_init(self, caplog: pytest.LogCaptureFixture) -> None:
        """LDAPClient can be initialised."""
        client = LDAPClient()

        assert "Creating LDAP client." in caplog.text

        assert isinstance(client, LDAPClient)

    def test_verify_bind_ok(self, caplog: pytest.LogCaptureFixture, fx_mock_ldap: Mock) -> None:
        """Bind ok."""
        fx_mock_ldap.return_value.simple_bind_s.return_value = None

        client = LDAPClient()
        client.verify_bind()

        assert "Attempting to bind to LDAP server." in caplog.text
        assert "LDAP bind successful." in caplog.text

    def test_verify_bind_server_down(
        self, caplog: pytest.LogCaptureFixture, fx_mock_ldap_object: ldap.ldapobject.LDAPObject
    ) -> None:
        """Bind fails when server down."""
        fx_mock_ldap_object.simple_bind_s.side_effect = ldap.LDAPError()

        client = LDAPClient()
        with pytest.raises(RuntimeError) as e:
            client.verify_bind()

        assert "Attempting to bind to LDAP server." in caplog.text

        assert str(e.value) == "Failed to connect to LDAP server."
