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
