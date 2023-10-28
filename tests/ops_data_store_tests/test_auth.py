from unittest.mock import Mock

import ldap
import pytest
import requests_mock

from ops_data_store.auth import AzureClient, LDAPClient


class TestAzureClient:
    """Tests for app Azure client class."""

    def test_init(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """AzureClient can be initialised."""
        client = AzureClient()

        assert "Creating Azure client." in caplog.text

        assert isinstance(client, AzureClient)

    def test_get_token_silent_ok(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """Can acquire access token using valid cache."""
        expected = "x"
        fx_mock_msal_cca.return_value.acquire_token_silent.return_value = {"access_token": expected}

        client = AzureClient()
        token = client.get_token()

        assert "Attempting to acquire access token silently (from cache)." in caplog.text
        assert f"Access token: {expected}" in caplog.text

        assert token == expected

    def test_get_token_fresh_ok(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """Can acquire access token where cache empty."""
        expected = "x"
        fx_mock_msal_cca.return_value.acquire_token_silent.return_value = None
        fx_mock_msal_cca.return_value.acquire_token_for_client.return_value = {"access_token": expected}

        client = AzureClient()
        token = client.get_token()

        assert "Attempting to acquire access token silently (from cache)." in caplog.text
        assert "Failed to acquire token silently, attempting to request fresh token." in caplog.text
        assert f"Access token: {expected}" in caplog.text

        assert token == expected

    def test_get_token_error(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """Can acquire access token where cache empty."""
        expected = {"error": "x", "error_description": "y", "correlation_id": "z"}
        fx_mock_msal_cca.return_value.acquire_token_silent.return_value = expected

        client = AzureClient()
        with pytest.raises(RuntimeError) as e:
            client.get_token()

        assert f"Error: {expected['error']}" in caplog.text
        assert f"Error description: {expected['error_description']}" in caplog.text
        assert f"Correlation ID: {expected['correlation_id']}" in caplog.text

        assert str(e.value) == "Failed to acquire Azure token."

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_get_token_mocked(self, fx_azure_client: AzureClient) -> None:
        """Can mock get token method."""
        expected = "x"
        assert fx_azure_client.get_token() == expected

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_get_group_members_ok(self, caplog: pytest.LogCaptureFixture, fx_azure_client: AzureClient) -> None:
        """Can get group members."""
        group_id = "123"
        expected = ["foo@example.com", "bar@example.com"]

        mock_response = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#directoryObjects",
            "value": [{"@odata.type": "#microsoft.graph.user", "userPrincipalName": member} for member in expected],
        }
        with requests_mock.Mocker() as m:
            m.get(f"https://graph.microsoft.com/v1.0/groups/{group_id}/members", json=mock_response)

            members = fx_azure_client.get_group_members(group_id)

            assert f"Getting members of group ID: {group_id} from MS Graph API." in caplog.text
            assert f"Members ({len(expected)}): {', '.join(expected)}" in caplog.text

            assert members == expected

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_get_group_name_ok(self, caplog: pytest.LogCaptureFixture, fx_azure_client: AzureClient) -> None:
        """Can get group name."""
        group_id = "123"
        expected = "foo"

        mock_response = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#groups/$entity",
            "displayName": expected,
        }
        with requests_mock.Mocker() as m:
            m.get(f"https://graph.microsoft.com/v1.0/groups/{group_id}", json=mock_response)

            name = fx_azure_client.get_group_name(group_id)

            assert f"Getting display name of group ID: {group_id} from MS Graph API." in caplog.text
            assert f"displayName: {expected}" in caplog.text

            assert name == expected


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
