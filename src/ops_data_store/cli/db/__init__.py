import logging
from pathlib import Path
from typing import Annotated

import psycopg
import typer

from ops_data_store.config import Config

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")


@app.command(help="Check DB connectivity.")
def check() -> None:
    """Check DB connection."""
    try:
        logger.info("Checking DB connectivity.")
        with psycopg.connect(conninfo=config.DB_DSN, connect_timeout=3) as conn:
            conn.read_only = True

            with conn.cursor() as cur:
                cur.execute("SELECT 1")

            logger.info("DB connectivity ok.")
            print("Ok. DB connection successful.")
    except (psycopg.ProgrammingError, psycopg.OperationalError) as e:
        logger.error(e, exc_info=True)
        print("No. DB connection failed.")
        raise typer.Abort() from e


@app.command(help="Configure a new DB for use.")
def setup() -> None:
    """
    Create required Postgres extensions and functions.

    It's expected this command will be run once as part of setting up a new database as part of an instance of this
    application. It MUST be assumed however that this command may be run multiple times (possibly as part of ongoing
    automation) and so this command MUST NOT put existing data at risk or return errors for pre-existing objects etc.

    Error handling is intentionally omitted in this command as the underlying exceptions will give useful context
    should any command fail, and wrapping these exceptions won't provide any benefit.
    """
    logger.info("Setting up required database objects.")
    print("Setting up database for first time use.")
    print(
        "Note: If this command fails, please either create an issue in the 'Ops Data Store' project in GitLab, or "
        "contact MAGIC at magic@bas.ac.uk with the output of this command."
    )

    with psycopg.connect(config.DB_DSN) as conn, conn.cursor() as cur:
        for extension in ["postgis", "pgcrypto"]:
            logger.info(f"Setting up required DB extension {extension}.")
            # exempting SQL injection check as extension names are effectively fixed
            cur.execute(f"CREATE EXTENSION IF NOT EXISTS {extension}")
            cur.execute(f"SELECT COUNT(name) FROM pg_available_extensions WHERE name='{extension}'")  # noqa: S608
            if cur.fetchone()[0] != 1:  # pragma: no cover - see MAGIC/ops-data-store#43
                logger.error(f"Required extension '{extension}' not found after creating.")
                print(f"No. Required extension '{extension}' not found.")
                raise typer.Abort()
            logger.info(f"Required DB extension '{extension}' ok.")

        logger.info("Setting up required DB function 'generate_ulid'.")
        cur.execute(
            """
        CREATE OR REPLACE FUNCTION generate_ulid() RETURNS uuid
            AS $$
                SELECT (
                    lpad(to_hex(floor(extract(epoch FROM clock_timestamp()) * 1000)::bigint), 12, '0') ||
                    encode(gen_random_bytes(10), 'hex')
                )::uuid;
            $$ LANGUAGE SQL;
        """
        )
        cur.execute("""SELECT COUNT(*) FROM pg_proc WHERE proname = 'generate_ulid';""")
        if cur.fetchone()[0] != 1:  # pragma: no cover - see MAGIC/ops-data-store#43
            logger.error("Required function 'generate_ulid' not found after creating.")
            print("No. Required function 'generate_ulid' not found.")
            raise typer.Abort()
        logger.info("Required DB function 'generate_ulid' ok.")

    logger.info("Database setup complete.")
    print("Complete.")


@app.command(help="Execute contents of an SQL against DB.")
def run(input_path: Annotated[Path, typer.Option()]) -> None:
    """Load contents of SQL file and execute against DB."""
    logger.info("Loading file contents and running inside DB.")
    logging.info(f"Input path: {input_path.resolve()}")

    if not input_path.exists():
        logging.error("Input path not found.")
        print(f"No. Input path '{input_path.resolve()}' does not exist.")
        raise typer.Abort()
    if not input_path.is_file():
        logging.error("Input path not a file.")
        print(f"No. Input path '{input_path.resolve()}' is not a file.")
        raise typer.Abort()

    try:
        print(f"Executing SQL from input file at '{input_path.resolve()}' against app DB.")
        with psycopg.connect(config.DB_DSN) as conn, conn.cursor() as cur:
            cur.execute(input_path.read_text())
    except (psycopg.ProgrammingError, psycopg.OperationalError) as e:
        logger.error(e, exc_info=True)
        print("No. Error running commands in input file.")
        raise typer.Abort() from e

    logging.info("Input file loaded and executed successfully.")
    print("Complete.")
