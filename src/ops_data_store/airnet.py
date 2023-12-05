import logging
from datetime import date

import ulid
from bas_air_unit_network_dataset.models.route import Route
from bas_air_unit_network_dataset.models.route_waypoint import RouteWaypoint
from bas_air_unit_network_dataset.models.waypoint import Waypoint
from bas_air_unit_network_dataset.networks.bas_air_unit import MainAirUnitNetwork
from psycopg.sql import SQL, Identifier

from ops_data_store.config import Config
from ops_data_store.db import DBClient


class AirUnitNetworkClient:
    """
    Air Unit Network client.

    A utility to convert waypoints and routes from the Air Unit travel network into outputs for devices.
    """

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating airnet client.")

        self.output_path = self.config.DATA_AIRNET_OUTPUT_PATH

        self.network = MainAirUnitNetwork(output_path=self.output_path)

        self.db_client = DBClient()

    def _fetch_waypoints(self) -> None:
        """Load waypoints from database into network."""
        self.logger.info("Fetching waypoints from database.")

        # noinspection SqlResolve,SqlMissingColumnAliases
        query = SQL(
            """
            SELECT
                pid, id, st_x(geom), st_y(geom), name, colocated_with, last_accessed_at, last_accessed_by, comment
            FROM {}
            """
        ).format(Identifier(self.config.DATA_AIRNET_WAYPOINTS_TABLE))
        results = self.db_client.fetch(query=query)
        self.logger.debug(f"query count: {len(results)}")

        for result in results:
            waypoint = Waypoint()

            waypoint.fid = str(ulid.parse(result[0]))
            waypoint.identifier = result[1]
            waypoint.geometry = [result[2], result[3]]
            if result[4] is not None:
                waypoint.name = result[4]
            if result[5] is not None:
                waypoint.colocated_with = result[5]
            if isinstance(result[6], date):
                waypoint.last_accessed_at = result[6]
            if result[7] is not None:
                waypoint.last_accessed_by = result[7]
            if result[8] is not None:
                waypoint.comment = result[8]

            self.logger.debug(f"Loading: {waypoint}")
            self.network.waypoints.append(waypoint)

    def _fetch_routes(self) -> None:
        """Load route and route waypoints from database into network."""
        self.logger.info("Fetching routes and route_waypoints from database.")

        # noinspection SqlResolve,SqlMissingColumnAliases
        query = SQL("""SELECT route_pid, waypoint_id, sequence FROM {} ORDER BY route_pid, sequence""").format(
            Identifier(self.config.DATA_AIRNET_ROUTE_WAYPOINTS_TABLE)
        )
        route_waypoint_results = self.db_client.fetch(query=query)
        self.logger.debug(f"route waypoint query count: {len(route_waypoint_results)}")

        route_waypoints = {}
        for result in route_waypoint_results:
            waypoint = next(
                waypoint for waypoint in self.network.waypoints.waypoints if waypoint.fid == str(ulid.parse(result[1]))
            )  # pragma: no cover
            route_waypoints.setdefault(str(ulid.parse(result[0])), []).append(
                RouteWaypoint(waypoint=waypoint, sequence=result[2])
            )

        # noinspection SqlResolve,SqlMissingColumnAliases
        query = SQL("""SELECT pid, id FROM {}""").format(Identifier(self.config.DATA_AIRNET_ROUTES_TABLE))
        route_results = self.db_client.fetch(query=query)
        self.logger.debug(f"route query count: {len(route_results)}")

        for result in route_results:
            route = Route()

            route_fid = str(ulid.parse(result[0]))
            route.fid = route_fid
            route.name = result[1]
            route.waypoints.extend(route_waypoints[route_fid])

            self.logger.debug(f"Loading: {route}")
            self.network.routes.append(route)

    def fetch(self) -> None:
        """Load data from database into network."""
        self._fetch_waypoints()
        self._fetch_routes()

    def export(self) -> None:
        """Convert network to output formats."""
        self.logger.info("Exporting waypoints as CSVs.")
        self.network.dump_csv()
        self.logger.info("Exporting network as GPX.")
        self.network.dump_gpx()
        self.logger.info("Exporting routes and waypoints as FPLs.")
        self.network.dump_fpl()
