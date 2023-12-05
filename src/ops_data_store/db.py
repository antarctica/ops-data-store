import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import psycopg
from psycopg import Cursor
from psycopg.sql import Composed

from ops_data_store.config import Config


class DBClient:
    """Application database client."""

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating DB client.")

        self._dsn = self.config.DB_DSN
        self.logger.info("DB DSN: %s.", self._dsn)

        self._required_extensions: list[str] = ["postgis", "pgcrypto", "fuzzystrmatch"]
        self._required_data_types: list[str] = ["ddm_point"]
        self._required_functions: list[str] = ["generate_ulid", "geom_as_ddm", "set_updated_at", "set_updated_by"]

        self._custom_data_types: dict[str, str] = {"ddm_point": "CREATE TYPE ddm_point AS (x TEXT, y TEXT);"}
        self._custom_functions: dict[str, str] = {
            "generate_ulid": """
        CREATE OR REPLACE FUNCTION generate_ulid() RETURNS uuid
        AS $$
            SELECT (
                lpad(to_hex(floor(extract(epoch FROM clock_timestamp()) * 1000)::bigint), 12, '0') ||
                encode(gen_random_bytes(10), 'hex')
            )::uuid;
        $$ LANGUAGE SQL;
            """,
            "geom_as_ddm": """
        CREATE OR REPLACE FUNCTION geom_as_ddm(geom GEOMETRY)
            RETURNS ddm_point
            IMMUTABLE
            PARALLEL SAFE
        AS $$
        DECLARE
            lon FLOAT;
            lat FLOAT;
            lon_degree FLOAT;
            lon_minutes FLOAT;
            lon_sign TEXT;
            lat_degree FLOAT;
            lat_minutes FLOAT;
            lat_sign TEXT;
            x TEXT;
            y TEXT;
        BEGIN
            lon := ST_X(geom);
            lat := ST_Y(geom);

            SELECT FLOOR(ABS(lon)), FLOOR(ABS(lat))
            INTO lon_degree, lat_degree;

            SELECT ((ABS(lon) - lon_degree) * 60.0), ((ABS(lat) - lat_degree) * 60.0)
            INTO lon_minutes, lat_minutes;

            IF lon >= 0 THEN
                lon_sign := 'E';
            ELSE
                lon_sign := 'W';
            END IF;

            IF lat >= 0 THEN
                lat_sign := 'N';
            ELSE
                lat_sign := 'S';
            END IF;

            x := CONCAT(CAST(lon_degree AS TEXT), '° ', TO_CHAR(lon_minutes, 'FM999999.999999'), ''' ', lon_sign);
            y := CONCAT(CAST(lat_degree AS TEXT), '° ', TO_CHAR(lat_minutes, 'FM999999.999999'), ''' ', lat_sign);

            RETURN (x, y);
        END;
        $$ LANGUAGE plpgsql;
            """,
            "set_updated_at": """
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
            """,
            "set_updated_by": """
        CREATE OR REPLACE FUNCTION set_updated_by()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_by = current_user;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
            """,
        }

    def _setup_extensions(self, cur: Cursor) -> None:
        """Create required Postgres extensions."""
        for extension in self._required_extensions:
            self.logger.info(f"Setting up required DB extension '{extension}'.")
            # exempting SQL injection check as extension names are effectively fixed
            cur.execute(f"CREATE EXTENSION IF NOT EXISTS {extension}")
            cur.execute(f"SELECT 1 FROM pg_available_extensions WHERE name='{extension}'")  # noqa: S608
            if cur.fetchone()[0] != 1:  # pragma: no cover - see MAGIC/ops-data-store#43
                self.logger.error(f"Required extension '{extension}' not found after attempting to create.")
                msg = f"No. Required extension '{extension}' not found."
                raise RuntimeError(msg)
            self.logger.info(f"Required DB extension '{extension}' ok.")

    def _setup_types(self, cur: Cursor) -> None:
        """Create required Postgres data types."""
        for data_type in self._required_data_types:
            self.logger.info(f"Setting up required DB data type '{data_type}'.")
            cur.execute(
                f"""
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = '{data_type}') THEN
                       {self._custom_data_types[data_type]}
                    END IF;
                END$$;
            """  # noqa: S608
            )

            cur.execute(f"""SELECT 1 FROM pg_type WHERE typname = '{data_type}';""")  # noqa: S608
            if cur.fetchone()[0] != 1:
                self.logger.error(f"Required data type '{data_type}' not found after attempting to create.")
                msg = f"No. Required data type '{data_type}' not found."
                raise RuntimeError(msg)
            self.logger.info(f"Required DB data type '{data_type}' ok.")

    def _setup_functions(self, cur: Cursor) -> None:
        """Create required Postgres functions."""
        for function in self._required_functions:
            self.logger.info(f"Setting up required DB function '{function}'.")
            cur.execute(self._custom_functions[function])
            cur.execute(f"""SELECT 1 FROM pg_proc WHERE proname = '{function}';""")  # noqa: S608
            if cur.fetchone()[0] != 1:
                self.logger.error(f"Required function '{function}' not found after attempting to create.")
                msg = f"No. Required function '{function}' not found."
                raise RuntimeError(msg)
            self.logger.info(f"Required DB function '{function}' ok.")

    def check(self) -> None:
        """
        Check DB can be queried.

        Raises a RuntimeError if test query fails.
        """
        self.logger.info("Checking DB connection.")
        try:
            with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
                cur.execute("SELECT 1;")
                self.logger.info("DB connection ok.")
        except (psycopg.ProgrammingError, psycopg.OperationalError) as e:
            self.logger.error(e, exc_info=True)
            msg = "DB connection failed."
            raise RuntimeError(msg) from e

    def setup(self) -> None:
        """
        Create required Postgres extensions and functions.

        Though it's expected this command will be run once when setting up a new database, it MUST be assumed it may be
        called multiple times (possibly as part of release automation). This command MUST NOT therefore put existing
        data at risk or return errors for pre-existing objects etc.

        Error handling is intentionally omitted in this command as the underlying exceptions will give useful context
        should any command fail, and wrapping these exceptions won't provide any benefit.
        """
        self.logger.info("Setting up required database objects.")

        with psycopg.connect(conninfo=self._dsn) as conn, conn.cursor() as cur:
            self._setup_extensions(cur=cur)
            self._setup_types(cur=cur)
            self._setup_functions(cur=cur)

    def execute(self, query: str) -> None:
        """Execute a query against the DB."""
        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(query)

    def dump(self, path: Path) -> None:
        """
        Backup database to a file.

        Wrapper around `pg_dump` command.

        The current time is appended as a comment to the dump file to ensure uniqueness where data doesn't change.

        Warning: Any existing file at `path` will be overwritten.

        :type path: Path
        :param path: Where to save dump file.
        """
        try:
            self.logger.info("Dumping database via `pg_dump`.")
            subprocess_args = ["pg_dump", f"--dbname={self._dsn}", f"--file={path.resolve()}"]
            self.logger.info(f"Args: {subprocess_args}")
            subprocess.run(args=subprocess_args, check=True, text=True, capture_output=True)

            self.logger.info("Appending timestamp to dump file.")
            with path.open(mode="a") as file:
                file.write(f"--\n-- Database dump created at: {datetime.now(tz=timezone.utc).isoformat()}\n--\n")

            self.logger.info("DB dump ok.")
        except subprocess.CalledProcessError as e:
            self.logger.error(e, exc_info=True)
            msg = "DB dump failed."
            raise RuntimeError(msg) from e

    def fetch(self, query: Composed) -> list[tuple]:
        """
        Fetch results from a query.

        :type query: Composed
        :param query: Query to execute.
        :rtype: list[tuple]
        :return: Query results.
        """
        self.logger.info("Fetching from database.")
        self.logger.debug(f"Query: {query}")

        with psycopg.connect(self._dsn) as conn, conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()
