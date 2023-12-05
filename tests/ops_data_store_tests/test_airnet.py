import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import UUID

import pytest
from bas_air_unit_network_dataset.models.route import Route
from bas_air_unit_network_dataset.models.routes import RouteCollection
from bas_air_unit_network_dataset.models.waypoint import Waypoint
from bas_air_unit_network_dataset.models.waypoints import WaypointCollection
from pytest_mock import MockFixture

from ops_data_store.airnet import AirUnitNetworkClient


class TestAirnetClient:
    """Tests for app AirNet client."""

    def test_init(self, caplog: pytest.LogCaptureFixture) -> None:
        """Can be initialised."""
        client = AirUnitNetworkClient()

        assert "Creating airnet client." in caplog.text

        assert isinstance(client, AirUnitNetworkClient)

    def test_fetch_ok(
        self, mocker: MockFixture, fx_airnet_client: AirUnitNetworkClient, fx_at_wp_start: Waypoint, fx_at_rt: Route
    ) -> None:
        """Fetch succeeds."""
        waypoints = [
            (
                UUID("018c36a6-ce23-95f4-e9e8-1d4fb9647e54"),
                "ALPHA",
                -75.01463335007429,
                -69.91516669280827,
                "Alpha",
                "Foo",
                datetime.date(2012, 4, 24),
                "~conwat",
                "There's unlimited juice?",
            ),
            (
                UUID("018c36a6-ce3f-ee5f-f027-2436451e1b10"),
                "BRAVO",
                -75.19033329561353,
                -70.8301666751504,
                None,
                None,
                None,
                None,
                None,
            ),
        ]
        routes = [(UUID("018c36a6-ce54-904f-52df-a5b8360e0f95"), "01_ALPHA_TO_BRAVO")]
        route_waypoints = [
            (UUID("018c36a6-ce54-904f-52df-a5b8360e0f95"), UUID("018c36a6-ce23-95f4-e9e8-1d4fb9647e54"), 1),
            (UUID("018c36a6-ce54-904f-52df-a5b8360e0f95"), UUID("018c36a6-ce3f-ee5f-f027-2436451e1b10"), 2),
        ]
        mocker.patch.object(fx_airnet_client.db_client, "fetch", side_effect=[waypoints, route_waypoints, routes])

        # reset/empty network
        fx_airnet_client.network._waypoints = WaypointCollection()
        fx_airnet_client.network._routes = RouteCollection()

        fx_airnet_client.fetch()

        assert len(fx_airnet_client.network.waypoints) == len(waypoints)
        assert repr(fx_airnet_client.network.waypoints[fx_at_wp_start.fid]) == repr(fx_at_wp_start)
        assert repr(fx_airnet_client.network.routes[fx_at_rt.fid]) == repr(fx_at_rt)

    def test_export_ok(
        self,
        fx_airnet_client: AirUnitNetworkClient,
        caplog: pytest.LogCaptureFixture,
        fx_test_data_managed_table_names: list[str],
    ):
        """Export succeeds."""
        with TemporaryDirectory() as workspace:
            fx_airnet_client.network._output_path = Path(workspace)
            fx_airnet_client.export()

            paths = list(Path(workspace).glob("**/*"))

        assert "Exporting waypoints as CSVs." in caplog.text
        assert "Exporting network as GPX." in caplog.text
        assert "Exporting routes and waypoints as FPLs." in caplog.text

        assert len(paths) > 0
