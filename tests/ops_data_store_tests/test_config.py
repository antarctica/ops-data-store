from os import environ

import pytest
from environs import EnvError

from ops_data_store.config import Config


class TestConfig:
    """Tests for app config."""

    def test_init(self, fx_test_config: Config) -> None:
        """Can be initialised."""
        assert isinstance(fx_test_config, Config)

    def test_dump(self, fx_test_config: Config, fx_test_config_dict: dict) -> None:
        """Config can be dumped to a dict."""
        expected = fx_test_config_dict
        assert fx_test_config.dump() == expected

    def test_validate_ok(self, fx_test_config: Config) -> None:
        """Config can be validated."""
        fx_test_config.validate()

        assert True


class TestConfigVersion:
    """Tests for `VERSION` property."""

    def test_ok(self, fx_test_package_version: str, fx_test_config: Config) -> None:
        """Property can be read."""
        assert fx_test_package_version == fx_test_config.VERSION


class TestConfigDbDsn:
    """Tests for `DB_DSN` property."""

    def test_ok(self, fx_test_config: Config, fx_test_db_dsn: str) -> None:
        """Property check."""
        assert fx_test_db_dsn == fx_test_config.DB_DSN

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property raises exception."""
        db_dsn = environ["APP_ODS_DB_DSN"]
        del environ["APP_ODS_DB_DSN"]

        with pytest.raises(EnvError):
            # noinspection PyStatementEffect
            fx_test_config.DB_DSN  # noqa: B018

        environ["APP_ODS_DB_DSN"] = db_dsn

    def test_validate_error(self, fx_test_config: Config) -> None:
        """Missing `DB_DSN` property fails validation."""
        db_dsn = environ["APP_ODS_DB_DSN"]
        del environ["APP_ODS_DB_DSN"]

        # assert validate method returns RuntimeError and message is 'foo'
        with pytest.raises(RuntimeError) as e:
            fx_test_config.validate()

        assert str(e.value) == "Required config option `DB_DSN` not set."

        environ["APP_ODS_DB_DSN"] = db_dsn


class TestConfigAuthAzureAuthority:
    """Tests for `AUTH_AZURE_AUTHORITY` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_azure_authority: str) -> None:
        """Property check."""
        assert fx_test_auth_azure_authority == fx_test_config.AUTH_AZURE_AUTHORITY

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        authority = environ["APP_ODS_AUTH_AZURE_AUTHORITY"]
        del environ["APP_ODS_AUTH_AZURE_AUTHORITY"]

        assert fx_test_config.AUTH_AZURE_AUTHORITY is None

        environ["APP_ODS_AUTH_AZURE_AUTHORITY"] = authority


class TestConfigAuthAzureClientId:
    """Tests for `AUTH_AZURE_CLIENT_ID` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_azure_client_id: str) -> None:
        """Property check."""
        assert fx_test_auth_azure_client_id == fx_test_config.AUTH_AZURE_CLIENT_ID

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        client_id = environ["APP_ODS_AUTH_AZURE_CLIENT_ID"]
        del environ["APP_ODS_AUTH_AZURE_CLIENT_ID"]

        assert fx_test_config.AUTH_AZURE_CLIENT_ID is None

        environ["APP_ODS_AUTH_AZURE_CLIENT_ID"] = client_id


class TestConfigAuthAzureClientSecret:
    """Tests for `AUTH_AZURE_CLIENT_SECRET` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_azure_client_secret: str) -> None:
        """Property check."""
        assert fx_test_auth_azure_client_secret == fx_test_config.AUTH_AZURE_CLIENT_SECRET

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        client_secret = environ["APP_ODS_AUTH_AZURE_CLIENT_SECRET"]
        del environ["APP_ODS_AUTH_AZURE_CLIENT_SECRET"]

        assert fx_test_config.AUTH_AZURE_CLIENT_SECRET is None

        environ["APP_ODS_AUTH_AZURE_CLIENT_SECRET"] = client_secret


class TestConfigAuthAzureScopes:
    """Tests for `AUTH_AZURE_SCOPES` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_azure_scopes: str) -> None:
        """Property check."""
        assert fx_test_auth_azure_scopes == fx_test_config.AUTH_AZURE_SCOPES


class TestConfigAuthMsGraphEndpoint:
    """Tests for `AUTH_MS_GRAPH_ENDPOINT` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ms_graph_endpoint: str) -> None:
        """Property check."""
        assert fx_test_auth_ms_graph_endpoint == fx_test_config.AUTH_MS_GRAPH_ENDPOINT


class TestConfigAuthLdapUrl:
    """Tests for `AUTH_LDAP_URL` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_url: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_url == fx_test_config.AUTH_LDAP_URL

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_url = environ["APP_ODS_AUTH_LDAP_URL"]
        del environ["APP_ODS_AUTH_LDAP_URL"]

        assert fx_test_config.AUTH_LDAP_URL is None

        environ["APP_ODS_AUTH_LDAP_URL"] = ldap_url


class TestConfigAuthLdapBaseDn:
    """Tests for `AUTH_LDAP_BASE_DN` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_base_dn: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_base_dn == fx_test_config.AUTH_LDAP_BASE_DN

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_base_dn = environ["APP_ODS_AUTH_LDAP_BASE_DN"]
        del environ["APP_ODS_AUTH_LDAP_BASE_DN"]

        assert fx_test_config.AUTH_LDAP_BASE_DN is None

        environ["APP_ODS_AUTH_LDAP_BASE_DN"] = ldap_base_dn


class TestConfigAuthLdapBindDn:
    """Tests for `AUTH_LDAP_BIND_DN` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_bind_dn: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_bind_dn == fx_test_config.AUTH_LDAP_BIND_DN

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_bind_dn = environ["APP_ODS_AUTH_LDAP_BIND_DN"]
        del environ["APP_ODS_AUTH_LDAP_BIND_DN"]

        assert fx_test_config.AUTH_LDAP_BIND_DN is None

        environ["APP_ODS_AUTH_LDAP_BIND_DN"] = ldap_bind_dn


class TestConfigAuthLdapBindPassword:
    """Tests for `AUTH_LDAP_BIND_PASSWORD` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_bind_password: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_bind_password == fx_test_config.AUTH_LDAP_BIND_PASSWORD

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_bind_password = environ["APP_ODS_AUTH_LDAP_BIND_PASSWORD"]
        del environ["APP_ODS_AUTH_LDAP_BIND_PASSWORD"]

        assert fx_test_config.AUTH_LDAP_BIND_PASSWORD is None

        environ["APP_ODS_AUTH_LDAP_BIND_PASSWORD"] = ldap_bind_password


class TestConfigAuthLdapOuUsers:
    """Tests for `AUTH_LDAP_OU_USERS` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_ou_users: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_ou_users == fx_test_config.AUTH_LDAP_OU_USERS

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_ou_users = environ["APP_ODS_AUTH_LDAP_OU_USERS"]
        del environ["APP_ODS_AUTH_LDAP_OU_USERS"]

        assert fx_test_config.AUTH_LDAP_OU_USERS is None

        environ["APP_ODS_AUTH_LDAP_OU_USERS"] = ldap_ou_users


class TestConfigAuthLdapOuGroups:
    """Tests for `AUTH_LDAP_OU_GROUPS` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_ou_groups: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_ou_groups == fx_test_config.AUTH_LDAP_OU_GROUPS

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_ou_groups = environ["APP_ODS_AUTH_LDAP_OU_GROUPS"]
        del environ["APP_ODS_AUTH_LDAP_OU_GROUPS"]

        assert fx_test_config.AUTH_LDAP_OU_GROUPS is None

        environ["APP_ODS_AUTH_LDAP_OU_GROUPS"] = ldap_ou_groups


class TestConfigAuthLdapNameContextUsers:
    """Tests for `AUTH_LDAP_NAME_CONTEXT_USERS` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_name_context_users: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_name_context_users == fx_test_config.AUTH_LDAP_NAME_CONTEXT_USERS

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_name_context_users = environ["APP_ODS_AUTH_LDAP_CXT_USERS"]
        del environ["APP_ODS_AUTH_LDAP_CXT_USERS"]

        assert fx_test_config.AUTH_LDAP_NAME_CONTEXT_USERS is None

        environ["APP_ODS_AUTH_LDAP_CXT_USERS"] = ldap_name_context_users


class TestConfigAuthLdapNameContextGroups:
    """Tests for `AUTH_LDAP_NAME_CONTEXT_GROUPS` property."""

    def test_ok(self, fx_test_config: Config, fx_test_auth_ldap_name_context_groups: str) -> None:
        """Property check."""
        assert fx_test_auth_ldap_name_context_groups == fx_test_config.AUTH_LDAP_NAME_CONTEXT_GROUPS

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property uses None as default."""
        ldap_name_context_groups = environ["APP_ODS_AUTH_LDAP_CXT_GROUPS"]
        del environ["APP_ODS_AUTH_LDAP_CXT_GROUPS"]

        assert fx_test_config.AUTH_LDAP_NAME_CONTEXT_GROUPS is None

        environ["APP_ODS_AUTH_LDAP_CXT_GROUPS"] = ldap_name_context_groups


class TestConfigDataManagedTableNames:
    """Tests for `DATA_MANAGED_TABLE_NAMES` property."""

    def test_ok(self, fx_test_data_managed_table_names: list[str], fx_test_config: Config) -> None:
        """Property check."""
        assert fx_test_data_managed_table_names == fx_test_config.DATA_MANAGED_TABLE_NAMES

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property raises exception."""
        table_names = environ["APP_ODS_DATA_MANAGED_TABLE_NAMES"]
        del environ["APP_ODS_DATA_MANAGED_TABLE_NAMES"]

        with pytest.raises(EnvError):
            # noinspection PyStatementEffect
            fx_test_config.DATA_MANAGED_TABLE_NAMES  # noqa: B018

        environ["APP_ODS_DATA_MANAGED_TABLE_NAMES"] = table_names

    def test_validate_error(self, fx_test_config: Config) -> None:
        """Missing property fails validation."""
        table_names = environ["APP_ODS_DATA_MANAGED_TABLE_NAMES"]
        del environ["APP_ODS_DATA_MANAGED_TABLE_NAMES"]

        # assert validate method returns RuntimeError and message is 'foo'
        with pytest.raises(RuntimeError, match="Required config option `DATA_MANAGED_TABLE_NAMES` not set."):
            fx_test_config.validate()

        environ["APP_ODS_DATA_MANAGED_TABLE_NAMES"] = table_names


class TestDataQgisTableNames:
    """Tests for `DATA_QGIS_TABLE_NAMES` property."""

    def test_ok(self, fx_test_data_qgis_table_names: list[str], fx_test_config: Config) -> None:
        """Property can be read."""
        assert fx_test_data_qgis_table_names == fx_test_config.DATA_QGIS_TABLE_NAMES
