import json
from datetime import date, datetime, timezone
from importlib.metadata import version
from pathlib import Path
from typing import Callable
from unittest.mock import Mock

import ldap
import pytest
from bas_air_unit_network_dataset.models.route import Route
from bas_air_unit_network_dataset.models.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.models.waypoint import Waypoint
from environs import Env
from pytest_mock import MockFixture
from typer.testing import CliRunner

from ops_data_store.airnet import AirUnitNetworkClient
from ops_data_store.auth import AzureClient, SimpleSyncClient
from ops_data_store.backup import BackupClient, RollingFileState, RollingFileStateIteration, RollingFileStateMeta
from ops_data_store.config import Config
from ops_data_store.data import DataClient
from tests.mocks import (
    data_client_export_touch_path,
    db_client_dump_touch_path,
    test_check_target_users__ldap_check_users,
)


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
def fx_test_data_managed_table_names(fx_test_env: Env) -> list[str]:
    """Names of managed dataset tables."""
    return fx_test_env.list("APP_ODS_DATA_MANAGED_TABLE_NAMES")


@pytest.fixture()
def fx_test_data_qgis_table_names(fx_test_env: Env) -> list[str]:
    """Names of QGIS tables."""
    return ["layer_styles"]


@pytest.fixture()
def fx_test_backups_path(fx_test_env: Env) -> Path:
    """Path for backups."""
    return fx_test_env.path("APP_ODS_BACKUPS_PATH")


@pytest.fixture()
def fx_test_backups_count(fx_test_env: Env) -> int:
    """Maximum number of backup iterations to keep."""
    return fx_test_env.int("APP_ODS_BACKUPS_COUNT")


@pytest.fixture()
def fx_test_data_airnet_output_path(fx_test_env: Env) -> Path:
    """Path for Air Unit Network outputs."""
    return fx_test_env.path("APP_ODS_DATA_AIRNET_OUTPUT_PATH")


@pytest.fixture()
def fx_test_data_airnet_routes_table() -> str:
    """Name of table used for Air Unit Network routes."""
    return "route_container"


@pytest.fixture()
def fx_test_data_airnet_route_waypoints_table() -> str:
    """Name of table used for Air Unit Network route waypoints."""
    return "route_waypoint"


@pytest.fixture()
def fx_test_data_airnet_waypoints_table() -> str:
    """Name of table used for Air Unit Network waypoints."""
    return "waypoint"


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
    fx_test_data_managed_table_names: list[str],
    fx_test_data_qgis_table_names: list[str],
    fx_test_backups_path: Path,
    fx_test_backups_count: int,
    fx_test_data_airnet_output_path: Path,
    fx_test_data_airnet_routes_table: str,
    fx_test_data_airnet_route_waypoints_table: str,
    fx_test_data_airnet_waypoints_table: str,
) -> dict:
    """Config as dict."""
    return {
        "AUTH_AZURE_AUTHORITY": fx_test_auth_azure_authority,
        "AUTH_AZURE_CLIENT_ID": fx_test_auth_azure_client_id,
        "AUTH_AZURE_CLIENT_SECRET": fx_test_auth_azure_client_secret,
        "AUTH_AZURE_SCOPES": fx_test_auth_azure_scopes,
        "AUTH_LDAP_BASE_DN": fx_test_auth_ldap_base_dn,
        "AUTH_LDAP_BIND_DN": fx_test_auth_ldap_bind_dn,
        "AUTH_LDAP_BIND_PASSWORD": fx_test_auth_ldap_bind_password,
        "AUTH_LDAP_NAME_CONTEXT_GROUPS": fx_test_auth_ldap_name_context_groups,
        "AUTH_LDAP_NAME_CONTEXT_USERS": fx_test_auth_ldap_name_context_users,
        "AUTH_LDAP_OU_GROUPS": fx_test_auth_ldap_ou_groups,
        "AUTH_LDAP_OU_USERS": fx_test_auth_ldap_ou_users,
        "AUTH_LDAP_URL": fx_test_auth_ldap_url,
        "AUTH_MS_GRAPH_ENDPOINT": fx_test_auth_ms_graph_endpoint,
        "BACKUPS_COUNT": fx_test_backups_count,
        "BACKUPS_PATH": fx_test_backups_path,
        "DATA_AIRNET_OUTPUT_PATH": fx_test_data_airnet_output_path,
        "DATA_AIRNET_ROUTES_TABLE": fx_test_data_airnet_routes_table,
        "DATA_AIRNET_ROUTE_WAYPOINTS_TABLE": fx_test_data_airnet_route_waypoints_table,
        "DATA_AIRNET_WAYPOINTS_TABLE": fx_test_data_airnet_waypoints_table,
        "DATA_MANAGED_TABLE_NAMES": fx_test_data_managed_table_names,
        "DATA_QGIS_TABLE_NAMES": fx_test_data_qgis_table_names,
        "DB_DSN": fx_test_db_dsn,
        "VERSION": fx_test_package_version,
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
def fx_mock_ssc_azure_group_ids() -> list[str]:
    """Mock Azure group ID."""
    return ["123"]


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
    mocker: MockFixture, fx_mock_ssc_azure_group_ids: list[str], fx_mock_ssc_ldap_group_id: str
) -> SimpleSyncClient:
    """Mock Simple Sync Client to avoid calling real Azure and LDAP clients."""
    mocker.patch("ops_data_store.auth.AzureClient", autospec=True)
    mocker.patch("ops_data_store.auth.LDAPClient", autospec=True)

    return SimpleSyncClient(azure_group_ids=fx_mock_ssc_azure_group_ids, ldap_group_id=fx_mock_ssc_ldap_group_id)


@pytest.fixture()
def fx_se_mock_ldap_check_users() -> Callable:
    """Side effect for `LDAPClient.check_users()` used in the `TestAuth.test_check_target_users`."""
    return test_check_target_users__ldap_check_users


@pytest.fixture()
def fx_data_client() -> DataClient:
    """App data client."""
    return DataClient()


@pytest.fixture()
def fx_rfs_schema_version() -> str:
    """Rolling file set schema version."""  # noqa: D401
    return "1"


@pytest.fixture()
def fx_rfs_max_iterations() -> int:
    """Maximum iterations for rolling file set."""
    return 3


@pytest.fixture()
def fx_rfs_first_iteration() -> RollingFileStateIteration:
    """Original, oldest, iteration in a rolling file set."""
    created = datetime(year=2022, month=4, day=24, hour=4, minute=40, second=1, tzinfo=timezone.utc)
    return RollingFileStateIteration(
        sha1sum="d4f497e82c586022966d3f7d3d3d93faa76721aa",
        replaces_sha1sum="",
        created_at=created,
        original_name="alice.txt",
        sequence=0,
        path=Path("/foo_1.txt"),
    )


@pytest.fixture()
def fx_rfs_second_iteration(fx_rfs_first_iteration: RollingFileStateIteration) -> RollingFileStateIteration:
    """Newest, most recent, iteration in a rolling file set."""
    created = datetime(year=2022, month=5, day=25, hour=5, minute=50, second=1, tzinfo=timezone.utc)
    return RollingFileStateIteration(
        sha1sum="7fa79c52bf5a13daab69690c634dcc64c1871db0",
        replaces_sha1sum=fx_rfs_first_iteration.sha1sum,
        created_at=created,
        original_name="bob.txt",
        sequence=1,
        path=Path("/foo_2.txt"),
    )


@pytest.fixture()
def fx_rfs_meta(fx_rfs_max_iterations: int, fx_rfs_second_iteration: RollingFileStateIteration) -> RollingFileStateMeta:
    """Rolling file set state metadata."""  # noqa: D401
    return RollingFileStateMeta(
        max_iterations=fx_rfs_max_iterations,
        iterations=2,
        newest_iteration_sha1sum=fx_rfs_second_iteration.sha1sum,
        updated_at=datetime.fromisoformat("2023-11-07T12:43:40.065573+00:00"),
    )


@pytest.fixture()
def fx_rfs_state(
    fx_rfs_meta: RollingFileStateMeta,
    fx_rfs_first_iteration: RollingFileStateIteration,
    fx_rfs_second_iteration: RollingFileStateIteration,
) -> RollingFileState:
    """Rolling file set state."""  # noqa: D401
    iterations = {
        fx_rfs_first_iteration.sha1sum: fx_rfs_first_iteration,
        fx_rfs_second_iteration.sha1sum: fx_rfs_second_iteration,
    }
    return RollingFileState(meta=fx_rfs_meta, iterations=iterations)


@pytest.fixture()
def fx_rfs_state_json() -> str:
    """Rolling file set state as JSON encoded str."""  # noqa: D401
    data = {
        "meta": {
            "max_iterations": 3,
            "iterations": 2,
            "newest_iteration_sha1sum": "7fa79c52bf5a13daab69690c634dcc64c1871db0",
            "schema_version": "1",
            "updated_at": "2023-11-07T12:43:40.065573+00:00",
        },
        "iterations": {
            "d4f497e82c586022966d3f7d3d3d93faa76721aa": {
                "sha1sum": "d4f497e82c586022966d3f7d3d3d93faa76721aa",
                "replaces_sha1sum": "",
                "created_at": "2022-04-24T04:40:01+00:00",
                "original_name": "alice.txt",
                "sequence": 0,
                "path": "/foo_1.txt",
            },
            "7fa79c52bf5a13daab69690c634dcc64c1871db0": {
                "sha1sum": "7fa79c52bf5a13daab69690c634dcc64c1871db0",
                "replaces_sha1sum": "d4f497e82c586022966d3f7d3d3d93faa76721aa",
                "created_at": "2022-05-25T05:50:01+00:00",
                "original_name": "bob.txt",
                "sequence": 1,
                "path": "/foo_2.txt",
            },
        },
    }
    return json.dumps(data, indent=2)


@pytest.fixture()
def fx_backup_client(mocker: MockFixture) -> BackupClient:
    """App backup client."""
    data_client_mock = mocker.patch("ops_data_store.backup.DataClient", autospec=True)
    db_client_mock = mocker.patch("ops_data_store.backup.DBClient", autospec=True)
    mocker.patch("ops_data_store.backup.RollingFileSet", autospec=True)

    data_client_mock.return_value.export = data_client_export_touch_path
    db_client_mock.return_value.dump = db_client_dump_touch_path

    return BackupClient()


@pytest.fixture()
def fx_at_wp_start() -> Waypoint:
    """Start/origin waypoint in a travel network."""
    waypoint = Waypoint(
        identifier="ALPHA",
        lon=-75.01463335007429,
        lat=-69.91516669280827,
        name="Alpha",
        colocated_with="Foo",
        last_accessed_at=date(2012, 4, 24),
        last_accessed_by="~conwat",
        comment="There's unlimited juice?",
    )
    waypoint.fid = "01HGVADKH3JQTEKT0X9YWP8ZJM"

    return waypoint


@pytest.fixture()
def fx_at_wp_end() -> Waypoint:
    """End/destination waypoint in a travel network."""
    waypoint = Waypoint(identifier="BRAVO", lon=-75.19033329561353, lat=-70.8301666751504)
    waypoint.fid = "01HGVADKHZXSFZ09S46S2HW6RG"

    return waypoint


@pytest.fixture()
def fx_at_rt(fx_at_wp_start: Waypoint, fx_at_wp_end: Waypoint) -> Route:
    """Route in a travel network."""
    route = Route(name="01_ALPHA_TO_BRAVO")
    route.fid = "01HGVADKJMJ17N5QX5Q0V0W3WN"
    route.waypoints.append(RouteWaypoint(waypoint=fx_at_wp_start, sequence=1))
    route.waypoints.append(RouteWaypoint(waypoint=fx_at_wp_end, sequence=2))

    return route


@pytest.fixture()
def fx_airnet_client(
    mocker: MockFixture, fx_at_wp_start: Waypoint, fx_at_wp_end: Waypoint, fx_at_rt: Route
) -> AirUnitNetworkClient:
    """
    App AirNet client.

    Pre-populated with test waypoint and route.
    """
    mocker.patch("ops_data_store.airnet.DBClient", autospec=True)

    client = AirUnitNetworkClient()
    client.network.waypoints.append(fx_at_wp_start)
    client.network.waypoints.append(fx_at_wp_end)
    client.network.routes.append(fx_at_rt)

    return client
