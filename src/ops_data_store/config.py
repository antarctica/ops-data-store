from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import Optional

from environs import Env, EnvError


class Config:
    """Application configuration."""

    def __init__(self) -> None:
        """
        Create Config instance and load options from possible dotenv file.

        To support application tests which may need to manipulate options, such as the application database, variables
        loaded from a possible `.env` file, or that are set as environment variables directly, will be overriden by any
        variables set in a possible `.test.env` file.
        """
        self.env = Env()
        self.env.read_env()
        self.env.read_env(".test.env", override=True)

    def validate(self) -> None:
        """
        Validate required configuration options have valid values.

        `AUTH_*` options are not validated as they are not required to use the core functionality of this application.
        They will be validated at runtime if performing auth related functions.
        """
        try:
            self.env.str("APP_ODS_DB_DSN")
        except EnvError as e:
            msg = "Required config option `DB_DSN` not set."
            raise RuntimeError(msg) from e

        try:
            self.env.list("APP_ODS_DATA_MANAGED_TABLE_NAMES")
        except EnvError as e:
            msg = "Required config option `DATA_MANAGED_TABLE_NAMES` not set."
            raise RuntimeError(msg) from e

        try:
            backups_path: Path = self.env.path("APP_ODS_BACKUPS_PATH")
            if not backups_path.is_dir():
                msg = f"`BACKUPS_PATH` config value: '{backups_path.resolve()}' not a directory or does not exist."
                raise RuntimeError(msg)
        except EnvError as e:
            msg = "Required config option `BACKUPS_PATH` not set."
            raise RuntimeError(msg) from e

        try:
            backups_count: int = self.env.int("APP_ODS_BACKUPS_COUNT")
            if backups_count < 1:
                msg = f"`BACKUPS_COUNT` config value: '{backups_count}' must be greater than 0."
                raise RuntimeError(msg)
        except EnvError as e:
            msg = "Required config option `BACKUPS_COUNT` not set."
            raise RuntimeError(msg) from e

    def dump(self) -> dict:
        """Return application configuration as a dictionary."""
        return {
            "VERSION": self.VERSION,
            "DB_DSN": self.DB_DSN,
            "AUTH_AZURE_AUTHORITY": self.AUTH_AZURE_AUTHORITY,
            "AUTH_AZURE_CLIENT_ID": self.AUTH_AZURE_CLIENT_ID,
            "AUTH_AZURE_CLIENT_SECRET": self.AUTH_AZURE_CLIENT_SECRET,
            "AUTH_AZURE_SCOPES": self.AUTH_AZURE_SCOPES,
            "AUTH_MS_GRAPH_ENDPOINT": self.AUTH_MS_GRAPH_ENDPOINT,
            "AUTH_LDAP_URL": self.AUTH_LDAP_URL,
            "AUTH_LDAP_BASE_DN": self.AUTH_LDAP_BASE_DN,
            "AUTH_LDAP_BIND_DN": self.AUTH_LDAP_BIND_DN,
            "AUTH_LDAP_BIND_PASSWORD": self.AUTH_LDAP_BIND_PASSWORD,
            "AUTH_LDAP_OU_USERS": self.AUTH_LDAP_OU_USERS,
            "AUTH_LDAP_OU_GROUPS": self.AUTH_LDAP_OU_GROUPS,
            "AUTH_LDAP_NAME_CONTEXT_USERS": self.AUTH_LDAP_NAME_CONTEXT_USERS,
            "AUTH_LDAP_NAME_CONTEXT_GROUPS": self.AUTH_LDAP_NAME_CONTEXT_GROUPS,
            "DATA_MANAGED_TABLE_NAMES": self.DATA_MANAGED_TABLE_NAMES,
            "DATA_QGIS_TABLE_NAMES": self.DATA_QGIS_TABLE_NAMES,
            "BACKUPS_PATH": self.BACKUPS_PATH,
            "BACKUPS_COUNT": self.BACKUPS_COUNT,
        }

    @property
    def VERSION(self) -> str:
        """Application version."""
        return version("ops-data-store")

    @property
    def DB_DSN(self) -> str:
        """
        DB connection string.

        Must be defined as a Postgres connection URI.

        Source: https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING-URIS
        """
        return self.env.str("APP_ODS_DB_DSN")

    @property
    def AUTH_AZURE_AUTHORITY(self) -> Optional[str]:
        """
        Azure Entra authority URL.

        Typically defined as an Azure tenancy specific URL such in the form:
        `https://login.microsoftonline.com/{TENANT_ID}`.
        """
        return self.env.str("APP_ODS_AUTH_AZURE_AUTHORITY", default=None)

    @property
    def AUTH_AZURE_CLIENT_ID(self) -> Optional[str]:
        """
        Azure Entra client ID.

        As defined by the relevant Application Registration in the Azure Portal.
        """
        return self.env.str("APP_ODS_AUTH_AZURE_CLIENT_ID", default=None)

    @property
    def AUTH_AZURE_CLIENT_SECRET(self) -> Optional[str]:
        """
        Azure Entra client secret.

        As defined by the relevant Application Registration in the Azure Portal.
        """
        return self.env.str("APP_ODS_AUTH_AZURE_CLIENT_SECRET", default=None)

    @property
    def AUTH_AZURE_SCOPES(self) -> list[str]:
        """
        Azure Entra scopes.

        Scopes required to access relevant resources. The special `/.default` scope is used to access pre-configured
        permissions within the MS Graph API.

        Source: https://learn.microsoft.com/en-us/graph/auth-v2-service?tabs=http#4-request-an-access-token
        """
        return ["https://graph.microsoft.com/.default"]

    @property
    def AUTH_MS_GRAPH_ENDPOINT(self) -> str:
        """
        Base endpoint for the Microsoft Graph API.

        Source: https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0#call-the-v10-endpoint
        """
        return "https://graph.microsoft.com/v1.0"

    @property
    def AUTH_LDAP_URL(self) -> Optional[str]:
        """LDAP server URL."""
        return self.env.str("APP_ODS_AUTH_LDAP_URL", default=None)

    @property
    def AUTH_LDAP_BASE_DN(self) -> Optional[str]:
        """Distinguished Name (DN) used as common base/root for all LDAP queries."""
        return self.env.str("APP_ODS_AUTH_LDAP_BASE_DN", default=None)

    @property
    def AUTH_LDAP_BIND_DN(self) -> Optional[str]:
        """Distinguished Name (DN) used for LDAP client binding."""
        return self.env.str("APP_ODS_AUTH_LDAP_BIND_DN", default=None)

    @property
    def AUTH_LDAP_BIND_PASSWORD(self) -> Optional[str]:
        """Password used for LDAP client binding."""
        return self.env.str("APP_ODS_AUTH_LDAP_BIND_PASSWORD", default=None)

    @property
    def AUTH_LDAP_OU_USERS(self) -> Optional[str]:
        """Organisational Unit (OU) containing users (individuals)."""
        return self.env.str("APP_ODS_AUTH_LDAP_OU_USERS", default=None)

    @property
    def AUTH_LDAP_OU_GROUPS(self) -> Optional[str]:
        """Organisational Unit (OU) containing groups."""
        return self.env.str("APP_ODS_AUTH_LDAP_OU_GROUPS", default=None)

    @property
    def AUTH_LDAP_NAME_CONTEXT_USERS(self) -> str:
        """
        LDAP naming context prefix used to identify users (individuals).

        Typically, either `cn` or `uid`.
        """
        return self.env.str("APP_ODS_AUTH_LDAP_CXT_USERS", default=None)

    @property
    def AUTH_LDAP_NAME_CONTEXT_GROUPS(self) -> str:
        """
        LDAP naming context prefix used to identify groups.

        Typically, `cn`.
        """
        return self.env.str("APP_ODS_AUTH_LDAP_CXT_GROUPS", default=None)

    @property
    def DATA_MANAGED_TABLE_NAMES(self) -> list[str]:
        """Names of tables used for managed datasets."""
        return self.env.list("APP_ODS_DATA_MANAGED_TABLE_NAMES")

    @property
    def DATA_QGIS_TABLE_NAMES(self) -> list[str]:
        """Names of tables used for optional QGIS features."""
        return ["layer_styles"]

    @property
    def BACKUPS_PATH(self) -> Path:
        """Where to store backups."""
        return self.env.path("APP_ODS_BACKUPS_PATH")

    @property
    def BACKUPS_COUNT(self) -> int:
        """
        Number of backup iterations to keep.

        Applies to per backup series - i.e. if set to `3`, 3 DB and 3 managed datasets backups will be kept.
        """
        return self.env.int("APP_ODS_BACKUPS_COUNT")
