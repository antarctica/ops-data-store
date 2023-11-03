from typing import Callable
from unittest.mock import Mock

import ldap
import pytest
import requests_mock
from pytest_mock import MockFixture

from ops_data_store.auth import AzureClient, LDAPClient, SimpleSyncClient


class TestAzureClient:
    """Tests for app Azure client."""

    def test_init(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """Can be initialised."""
        client = AzureClient()

        assert "Creating Azure client." in caplog.text

        assert isinstance(client, AzureClient)

    def test_get_token_silent_ok(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """Can acquire access token using valid cache."""
        expected = "x"
        fx_mock_msal_cca.return_value.acquire_token_silent.return_value = {"access_token": expected}

        client = AzureClient()
        token = client._get_token()

        assert "Attempting to acquire access token silently (from cache)." in caplog.text
        assert f"Access token: {expected}" in caplog.text

        assert token == expected

    def test_get_token_fresh_ok(self, caplog: pytest.LogCaptureFixture, fx_mock_msal_cca: Mock) -> None:
        """Can acquire access token where cache empty."""
        expected = "x"
        fx_mock_msal_cca.return_value.acquire_token_silent.return_value = None
        fx_mock_msal_cca.return_value.acquire_token_for_client.return_value = {"access_token": expected}

        client = AzureClient()
        token = client._get_token()

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
            client._get_token()

        assert f"Error: {expected['error']}" in caplog.text
        assert f"Error description: {expected['error_description']}" in caplog.text
        assert f"Correlation ID: {expected['correlation_id']}" in caplog.text

        assert str(e.value) == "Failed to acquire Azure token."

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_get_token_mocked(self, fx_azure_client: AzureClient) -> None:
        """Can mock get token method."""
        expected = "x"
        assert fx_azure_client._get_token() == expected

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_check_token(self, fx_azure_client: AzureClient) -> None:
        """Can check token."""
        fx_azure_client.check_token()

        assert True

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_check_group_ok(self, caplog: pytest.LogCaptureFixture, fx_azure_client: AzureClient) -> None:
        """Can get group."""
        group_id = "123"

        mock_response = {
            "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#groups/$entity",
            "id": group_id,
        }
        with requests_mock.Mocker() as m:
            m.get(f"https://graph.microsoft.com/v1.0/groups/{group_id}", json=mock_response)

            fx_azure_client.check_group(group_id)

            assert f"Checking group ID: {group_id} exists." in caplog.text
            assert f"Group ID: {group_id} exists." in caplog.text

    @pytest.mark.usefixtures("_fx_mock_azure_client_get_token")
    def test_check_group_unknown(self, caplog: pytest.LogCaptureFixture, fx_azure_client: AzureClient) -> None:
        """Cannot get unknown group."""
        group_id = "unknown"

        mock_response = {"error": {"message": f"Invalid object identifier '{group_id}'."}}
        with requests_mock.Mocker() as m:
            m.get(f"https://graph.microsoft.com/v1.0/groups/{group_id}", json=mock_response, status_code=400)

            with pytest.raises(ValueError, match=f"Group ID: {group_id} does not exist."):
                fx_azure_client.check_group(group_id)

            assert f"Checking group ID: {group_id} exists." in caplog.text
            assert f"Group ID: {group_id} does not exist." in caplog.text

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

            assert f"Getting display name of group ID: {group_id}." in caplog.text
            assert f"group ID: {group_id} DisplayName is: {expected}" in caplog.text

            assert name == expected


class TestLDAPClient:
    """Tests for app LDAP client."""

    def test_init(self, caplog: pytest.LogCaptureFixture) -> None:
        """Can be initialised/destroyed."""
        client = LDAPClient()

        assert "Creating LDAP client." in caplog.text

        assert isinstance(client, LDAPClient)

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_bind_ok(self, caplog: pytest.LogCaptureFixture) -> None:
        """Can bind to server."""
        client = LDAPClient()

        assert client._is_bound is False

        client._bind()

        assert "Attempting to bind to LDAP server." in caplog.text
        assert "LDAP bind successful." in caplog.text

        assert client._is_bound is True

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_bind_when_bound(self, caplog: pytest.LogCaptureFixture) -> None:
        """Skips bind if already bound."""
        client = LDAPClient()
        client._bind()

        assert client._is_bound is True

        client._bind()

        assert "Skipping as already bound." in caplog.text

        assert client._is_bound is True

    def test_bind_error(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Cannot bind when error occurs."""
        mocker.patch.object(ldap.ldapobject.LDAPObject, "simple_bind_s", side_effect=ldap.LDAPError())

        client = LDAPClient()
        with pytest.raises(RuntimeError) as e:
            client._bind()

        assert "Attempting to bind to LDAP server." in caplog.text

        assert str(e.value) == "Failed to connect to LDAP server."
        assert client._is_bound is False

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_verify_bind_ok(self, caplog: pytest.LogCaptureFixture) -> None:
        """Can bind."""
        client = LDAPClient()
        client.verify_bind()

        assert True

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_check_users(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Can find matching users."""
        search = ["cn=foo", "cn=bar", "cn=unknown"]
        base = "ou=users,dc=example,dc=com"
        expected = [f"{user},{base}" for user in search[:-1]]
        results = [(f"{user},{base}", {}) for user in search[:-1]]

        mocker.patch.object(ldap.ldapobject.LDAPObject, "search_s", return_value=results)

        client = LDAPClient()
        missing_users = client.check_users(user_ids=search)

        assert "Attempting to bind to LDAP server." in caplog.text
        assert "LDAP bind successful." in caplog.text
        assert (
            f"Searching for: ['dn'] in: {base} with filter: (|{''.join([f'({user})' for user in search])})"
            in caplog.text
        )

        assert missing_users == expected

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_check_groups(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Can find matching groups."""
        search = ["cn=admin", "cn=guest", "cn=unknown"]
        base = "ou=groups,dc=example,dc=com"
        expected = [f"{group},{base}" for group in search[:-1]]
        results = [(f"{group},{base}", {}) for group in search[:-1]]

        mocker.patch.object(ldap.ldapobject.LDAPObject, "search_s", return_value=results)

        client = LDAPClient()
        missing_groups = client.check_groups(group_ids=search)

        assert "Attempting to bind to LDAP server." in caplog.text
        assert "LDAP bind successful." in caplog.text
        assert (
            f"Searching for: ['dn'] in: {base} with filter: (|{''.join([f'({group})' for group in search])})"
            in caplog.text
        )

        assert missing_groups == expected

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_get_group_members(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Can get group members."""
        base = "ou=groups,dc=example,dc=com"
        name = "cn=admin"
        search = f"{name},{base}"
        expected = ["cn=foo,ou=users,dc=example,dc=com", "cn=bar,ou=users,dc=example,dc=com"]
        results = [(f"{search}", {"member": [member.encode() for member in expected]})]

        mocker.patch.object(ldap.ldapobject.LDAPObject, "search_s", return_value=results)

        client = LDAPClient()
        members = client.get_group_members(group_dn=search)

        assert "Attempting to bind to LDAP server." in caplog.text
        assert "LDAP bind successful." in caplog.text
        assert f"Searching in: {base} with filter: ({name})" in caplog.text

        assert members == expected

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_add_to_group_ok(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Can add users to group."""
        base = "ou=groups,dc=example,dc=com"
        name = "cn=admin"
        group_dn = f"{name},{base}"
        user_dns = ["cn=foo,ou=users,dc=example,dc=com", "cn=bar,ou=users,dc=example,dc=com"]
        result = (103, [], 2, [])

        mocker.patch.object(ldap.ldapobject.LDAPObject, "modify_s", return_value=result)

        client = LDAPClient()
        client.add_to_group(group_dn=group_dn, user_dns=user_dns)

        assert "Attempting to bind to LDAP server." in caplog.text
        assert "LDAP bind successful." in caplog.text
        assert f"Group to add to: {group_dn}" in caplog.text
        assert f"Users to add: {user_dns}" in caplog.text

    def test_add_to_group_empty(self, caplog: pytest.LogCaptureFixture):
        """Skip adding when no users specified."""
        client = LDAPClient()
        client.add_to_group(group_dn="x", user_dns=[])

        assert "Skipping as no users specified." in caplog.text

    @pytest.mark.usefixtures("_fx_mock_ldap_object")
    def test_remove_from_group(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Can remove users from group."""
        base = "ou=groups,dc=example,dc=com"
        name = "cn=admin"
        group_dn = f"{name},{base}"
        user_dns = ["cn=bar,ou=users,dc=example,dc=com"]
        result = (103, [], 2, [])

        mocker.patch.object(ldap.ldapobject.LDAPObject, "modify_s", return_value=result)

        client = LDAPClient()
        client.remove_from_group(
            group_dn=group_dn,
            user_dns=user_dns,
        )

    def test_remove_from_group_empty(self, caplog: pytest.LogCaptureFixture):
        """Skip removing when no users specified."""
        client = LDAPClient()
        client.remove_from_group(group_dn="x", user_dns=[])

        assert "Skipping as no users specified." in caplog.text


class TestSimpleSyncClient:
    """Tests for simple sync client."""

    def test_init(
        self,
        caplog: pytest.LogCaptureFixture,
        mocker: MockFixture,
        fx_mock_ssc_azure_group_id: str,
        fx_mock_ssc_ldap_group_id: str,
    ) -> None:
        """Can be initialised."""
        mocker.patch("ops_data_store.auth.AzureClient", autospec=True)
        mocker.patch("ops_data_store.auth.LDAPClient", autospec=True)

        client = SimpleSyncClient(azure_group_id=fx_mock_ssc_azure_group_id, ldap_group_id=fx_mock_ssc_ldap_group_id)

        assert "Creating sync client." in caplog.text
        assert f"Azure group ID: {fx_mock_ssc_azure_group_id}" in caplog.text
        assert f"LDAP group ID: {fx_mock_ssc_ldap_group_id}" in caplog.text

        assert isinstance(client, SimpleSyncClient)

    def test_check_groups_exist_ok(self, mocker: MockFixture, fx_mock_ssc: SimpleSyncClient) -> None:
        """Gets LDAP group DN where groups exist."""
        expected = "cn=abc,ou=groups,dc=example,dc=com"

        mocker.patch.object(fx_mock_ssc.azure_client, "check_group", return_value=None)
        mocker.patch.object(fx_mock_ssc.ldap_client, "check_groups", return_value=[expected])

        result = fx_mock_ssc._check_groups_exist()

        assert result == expected

    def test_check_groups_exist_missing_azure(
        self, mocker: MockFixture, fx_mock_ssc_azure_group_id: str, fx_mock_ssc: SimpleSyncClient
    ) -> None:
        """Fails where Azure group missing."""
        mocker.patch.object(
            fx_mock_ssc.azure_client,
            "check_group",
            side_effect=ValueError(f"Group ID: {fx_mock_ssc_azure_group_id} does not exist."),
        )

        with pytest.raises(RuntimeError, match=f"Azure group {fx_mock_ssc._source_group_id} does not exist."):
            fx_mock_ssc._check_groups_exist()

    def test_check_groups_exist_missing_ldap(self, mocker: MockFixture, fx_mock_ssc: SimpleSyncClient) -> None:
        """Fails where LDAP group missing."""
        mocker.patch.object(fx_mock_ssc.ldap_client, "check_groups", return_value=[])

        with pytest.raises(RuntimeError, match=f"LDAP group {fx_mock_ssc._target_group_id} does not exist."):
            fx_mock_ssc._check_groups_exist()

    def test_check_target_users(
        self,
        mocker: MockFixture,
        fx_mock_ssc_eval_result: dict[str, list[str]],
        fx_se_mock_ldap_check_users: Callable,
        fx_mock_ssc: SimpleSyncClient,
    ) -> None:
        """
        Can identify users for syncing.

        Key to users:
        - alice: present (in target)
        - bob: missing (from target)
        - connie: unknown (in target)
        - darren: removed (not in source)
        """
        fx_mock_ssc._source_user_ids = fx_mock_ssc_eval_result["source"]
        fx_mock_ssc._target_user_ids = fx_mock_ssc_eval_result["target"]

        mocker.patch.object(fx_mock_ssc.ldap_client, "check_users", side_effect=fx_se_mock_ldap_check_users)

        fx_mock_ssc._check_target_users()

        assert fx_mock_ssc._user_ids_missing_in_target == fx_mock_ssc_eval_result["missing"]
        assert fx_mock_ssc._user_ids_unknown_in_target == fx_mock_ssc_eval_result["unknown"]
        assert fx_mock_ssc._target_dns_del == ["cn=darren,ou=users,dc=example,dc=com"]
        assert fx_mock_ssc._target_dns_add == ["cn=bob,ou=users,dc=example,dc=com"]

    def test_get_source_user_ids(
        self, mocker: MockFixture, fx_mock_ssc: SimpleSyncClient, fx_mock_ssc_eval_result: dict[str, list[str]]
    ) -> None:
        """Gets users from Azure as generic user IDs."""
        expected = fx_mock_ssc_eval_result["source"]

        mocker.patch.object(
            fx_mock_ssc.azure_client,
            "get_group_members",
            return_value=[f"{user}@example.com" for user in expected],
        )

        fx_mock_ssc._get_source_user_ids()

        assert fx_mock_ssc._source_user_ids == expected

    def test_get_target_user_ids(
        self, mocker: MockFixture, fx_mock_ssc: SimpleSyncClient, fx_mock_ssc_eval_result: dict[str, list[str]]
    ) -> None:
        """Gets users from LDAP as generic user IDs."""
        expected = fx_mock_ssc_eval_result["target"]

        mocker.patch.object(
            fx_mock_ssc.ldap_client,
            "get_group_members",
            return_value=[f"cn={user},ou=users,dc=example,dc=com" for user in expected],
        )

        fx_mock_ssc._get_target_user_ids()

        assert fx_mock_ssc._target_user_ids == expected

    def test_evaluate(
        self,
        caplog: pytest.LogCaptureFixture,
        mocker: MockFixture,
        fx_mock_ssc_eval_result: dict[str, list[str]],
        fx_mock_ssc: SimpleSyncClient,
    ) -> None:
        """Can evaluate sync."""
        fx_mock_ssc._source_user_ids = fx_mock_ssc_eval_result["source"]
        fx_mock_ssc._target_user_ids = fx_mock_ssc_eval_result["target"]
        fx_mock_ssc._user_ids_missing_in_target = fx_mock_ssc_eval_result["missing"]
        fx_mock_ssc._user_ids_unknown_in_target = fx_mock_ssc_eval_result["unknown"]

        mocker.patch.object(fx_mock_ssc, "_check_groups_exist", return_value=None)
        mocker.patch.object(fx_mock_ssc, "_get_source_user_ids", return_value=None)
        mocker.patch.object(fx_mock_ssc, "_get_target_user_ids", return_value=None)
        mocker.patch.object(fx_mock_ssc, "_check_target_users", return_value=None)

        assert fx_mock_ssc._evaluated is False

        result = fx_mock_ssc.evaluate()

        assert "Evaluating Azure to LDAP group sync." in caplog.text

        assert fx_mock_ssc._user_ids_already_in_target == fx_mock_ssc_eval_result["present"]
        assert fx_mock_ssc._user_ids_unknown_in_source == fx_mock_ssc_eval_result["remove"]
        assert fx_mock_ssc._evaluated is True
        assert result == fx_mock_ssc_eval_result

    def test_sync_ok(
        self, caplog: pytest.LogCaptureFixture, mocker: MockFixture, fx_mock_ssc: SimpleSyncClient
    ) -> None:
        """Sync succeeds."""
        mocker.patch.object(fx_mock_ssc.ldap_client, "remove_from_group", return_value=None)
        mocker.patch.object(fx_mock_ssc.ldap_client, "add_to_group", return_value=None)
        fx_mock_ssc._evaluated = True

        fx_mock_ssc.sync()

        assert "Syncing members of Azure group to LDAP." in caplog.text

    def test_sync_not_evaluated(
        self, caplog: pytest.LogCaptureFixture, mocker: MockFixture, fx_mock_ssc: SimpleSyncClient
    ) -> None:
        """Sync runs evaluation if needed."""
        mocker.patch.object(fx_mock_ssc.ldap_client, "remove_from_group", return_value=None)
        mocker.patch.object(fx_mock_ssc.ldap_client, "add_to_group", return_value=None)
        mocker.patch.object(fx_mock_ssc, "evaluate", return_value=None)
        fx_mock_ssc._evaluated = False

        fx_mock_ssc.sync()

        assert "Sync not yet evaluated, evaluating first." in caplog.text
        assert "Syncing members of Azure group to LDAP." in caplog.text
