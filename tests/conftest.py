from importlib.metadata import version
from typing import Callable
from unittest.mock import Mock

import ldap
import pytest
from environs import Env
from pytest_mock import MockFixture
from typer.testing import CliRunner

from ops_data_store.auth import AzureClient, SimpleSyncClient
from ops_data_store.config import Config
from tests.mocks import test_check_target_users__ldap_check_users


@pytest.fixture()
def fx_test_env() -> Env:
    """Load environment variables configured in `.test.env`."""
    env = Env()
    env.read_env()
    env.read_env(".test.env", override=True)
    return env


@pytest.fixture()
def fx_test_package_version() -> str:
    """Package version configured in `pyproject.toml`."""
    return version("ops-data-store")


@pytest.fixture()
def fx_test_db_dsn(fx_test_env: Env) -> str:
    """DB Connection string."""
    return fx_test_env.str("APP_ODS_DB_DSN")


@pytest.fixture()
def fx_test_auth_azure_authority(fx_test_env: Env) -> str:
    """Azure authority URL."""
    return fx_test_env.str("APP_ODS_AUTH_AZURE_AUTHORITY")


@pytest.fixture()
def fx_test_auth_azure_client_id(fx_test_env: Env) -> str:
    """Azure app registration client ID."""
    return fx_test_env.str("APP_ODS_AUTH_AZURE_CLIENT_ID")


@pytest.fixture()
def fx_test_auth_azure_client_secret(fx_test_env: Env) -> str:
    """Azure app registration client secret."""
    return fx_test_env.str("APP_ODS_AUTH_AZURE_CLIENT_SECRET")


@pytest.fixture()
def fx_test_auth_azure_scopes() -> list[str]:
    """Scopes for Azure OAuth token."""
    return ["https://graph.microsoft.com/.default"]


@pytest.fixture()
def fx_test_auth_ms_graph_endpoint() -> str:
    """MS Graph API endpoint."""
    return "https://graph.microsoft.com/v1.0"


@pytest.fixture()
def fx_test_auth_ldap_url(fx_test_env: Env) -> str:
    """LDAP URL."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_URL")


@pytest.fixture()
def fx_test_auth_ldap_base_dn(fx_test_env: Env) -> str:
    """LDAP base DN."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_BASE_DN")


@pytest.fixture()
def fx_test_auth_ldap_bind_dn(fx_test_env: Env) -> str:
    """LDAP bind DN."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_BIND_DN")


@pytest.fixture()
def fx_test_auth_ldap_bind_password(fx_test_env: Env) -> str:
    """LDAP bind password."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_BIND_PASSWORD")


@pytest.fixture()
def fx_test_auth_ldap_ou_users(fx_test_env: Env) -> str:
    """LDAP users OU."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_OU_USERS")


@pytest.fixture()
def fx_test_auth_ldap_ou_groups(fx_test_env: Env) -> str:
    """LDAP groups OU."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_OU_GROUPS")


@pytest.fixture()
def fx_test_auth_ldap_name_context_users(fx_test_env: Env) -> str:
    """LDAP users name context."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_CXT_USERS")


@pytest.fixture()
def fx_test_auth_ldap_name_context_groups(fx_test_env: Env) -> str:
    """LDAP groups name context."""
    return fx_test_env.str("APP_ODS_AUTH_LDAP_CXT_GROUPS")


@pytest.fixture()
def fx_test_config() -> Config:
    """Provide access to app configuration."""
    return Config()


@pytest.fixture()
def fx_test_config_dict(
    fx_test_package_version: str,
    fx_test_db_dsn: str,
    fx_test_auth_azure_authority: str,
    fx_test_auth_azure_client_id: str,
    fx_test_auth_azure_client_secret: str,
    fx_test_auth_azure_scopes: str,
    fx_test_auth_ms_graph_endpoint: str,
    fx_test_auth_ldap_url: str,
    fx_test_auth_ldap_base_dn: str,
    fx_test_auth_ldap_bind_dn: str,
    fx_test_auth_ldap_bind_password: str,
    fx_test_auth_ldap_ou_users: str,
    fx_test_auth_ldap_ou_groups: str,
    fx_test_auth_ldap_name_context_users: str,
    fx_test_auth_ldap_name_context_groups: str,
) -> dict:
    """Config as dict."""
    return {
        "VERSION": fx_test_package_version,
        "DB_DSN": fx_test_db_dsn,
        "AUTH_AZURE_AUTHORITY": fx_test_auth_azure_authority,
        "AUTH_AZURE_CLIENT_ID": fx_test_auth_azure_client_id,
        "AUTH_AZURE_CLIENT_SECRET": fx_test_auth_azure_client_secret,
        "AUTH_AZURE_SCOPES": fx_test_auth_azure_scopes,
        "AUTH_MS_GRAPH_ENDPOINT": fx_test_auth_ms_graph_endpoint,
        "AUTH_LDAP_URL": fx_test_auth_ldap_url,
        "AUTH_LDAP_BASE_DN": fx_test_auth_ldap_base_dn,
        "AUTH_LDAP_BIND_DN": fx_test_auth_ldap_bind_dn,
        "AUTH_LDAP_BIND_PASSWORD": fx_test_auth_ldap_bind_password,
        "AUTH_LDAP_OU_USERS": fx_test_auth_ldap_ou_users,
        "AUTH_LDAP_OU_GROUPS": fx_test_auth_ldap_ou_groups,
        "AUTH_LDAP_NAME_CONTEXT_USERS": fx_test_auth_ldap_name_context_users,
        "AUTH_LDAP_NAME_CONTEXT_GROUPS": fx_test_auth_ldap_name_context_groups,
    }


@pytest.fixture()
def fx_cli_runner() -> CliRunner:
    """CLI testing fixture."""
    return CliRunner()


@pytest.fixture()
def fx_mock_msal_cca(mocker: MockFixture) -> Mock:
    """Mock MSAL ConfidentialClientApplication."""
    return mocker.patch("ops_data_store.auth.ConfidentialClientApplication", autospec=True)


@pytest.fixture()
def fx_azure_client(fx_mock_msal_cca: Mock) -> AzureClient:
    """App Azure client."""
    return AzureClient()


@pytest.fixture()
def _fx_mock_azure_client_get_token(mocker: MockFixture) -> None:
    """Mock app Azure client to avoid requesting real access tokens."""
    mocker.patch.object(AzureClient, "_get_token", return_value="x")


@pytest.fixture()
def _fx_mock_ldap_object(mocker: MockFixture) -> None:
    """Mock LDAP object to avoid binding."""
    mocker.patch.object(ldap.ldapobject.LDAPObject, "simple_bind_s", autospec=True)


@pytest.fixture()
def fx_mock_ssc_azure_group_id() -> str:
    """Mock Azure group ID."""
    return "123"


@pytest.fixture()
def fx_mock_ssc_ldap_group_id() -> str:
    """Mock LDAP group ID."""
    return "abc"


@pytest.fixture()
def fx_mock_ssc_eval_result() -> dict[str, list[str]]:
    """Mock result of Simple Sync Client evaluation."""
    return {
        "source": ["alice", "bob", "connie"],
        "target": ["alice", "darren"],
        "present": ["alice"],
        "missing": ["bob"],
        "unknown": ["connie"],
        "remove": ["darren"],
    }


@pytest.fixture()
def fx_mock_ssc(
    mocker: MockFixture, fx_mock_ssc_azure_group_id: str, fx_mock_ssc_ldap_group_id: str
) -> SimpleSyncClient:
    """Mock Simple Sync Client to avoid calling real Azure and LDAP clients."""
    mocker.patch("ops_data_store.auth.AzureClient", autospec=True)
    mocker.patch("ops_data_store.auth.LDAPClient", autospec=True)

    return SimpleSyncClient(azure_group_id=fx_mock_ssc_azure_group_id, ldap_group_id=fx_mock_ssc_ldap_group_id)


@pytest.fixture()
def fx_se_mock_ldap_check_users() -> Callable:
    """Side effect for `LDAPClient.check_users()` used in the `TestAuth.test_check_target_users`."""
    return test_check_target_users__ldap_check_users
