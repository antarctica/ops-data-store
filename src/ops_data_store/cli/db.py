import logging
from pathlib import Path
from typing import Annotated

import psycopg
import typer

from ops_data_store.config import Config
from ops_data_store.db import DBClient

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")


@app.command(help="Check DB connectivity.")
def check() -> None:
    """Check DB connection."""
    client = DBClient()

    try:
        client.check()
        print("Ok. DB connection successful.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print("No. DB connection failed.")
        raise typer.Abort() from e


@app.command(help="Configure a new DB for use.")
def setup() -> None:
    """Set up DB for use."""
    print("Setting up database for first time use.")
    print(
        "Note: If this command fails, please either create an issue in the 'Ops Data Store' project in GitLab, or "
        "contact MAGIC at magic@bas.ac.uk with the output of this command."
    )
    client = DBClient()

    try:
        client.setup()
        print("Ok. DB setup complete.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print(e)
        print("No. DB setup failed.")
        raise typer.Abort() from e


@app.command(help="Execute contents of an SQL against DB.")
def run(input_path: Annotated[Path, typer.Option()]) -> None:
    """Load contents of SQL file and execute against DB."""
    client = DBClient()

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
        client.execute(query=input_path.read_text())
    except (psycopg.ProgrammingError, psycopg.OperationalError) as e:
        logger.error(e, exc_info=True)
        print("No. Error running commands in input file.")
        raise typer.Abort() from e

    logging.info("Input file loaded and executed successfully.")
    print("Complete.")
