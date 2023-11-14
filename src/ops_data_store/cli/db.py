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


@app.command(help="Check database connectivity.")
def check() -> None:
    """Check database connection."""
    client = DBClient()

    try:
        client.check()
        print("Ok. Database connection successful.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print("No. Database connection failed.")
        raise typer.Abort() from e


@app.command(help="Configure new database instance for use.")
def setup() -> None:
    """Set up database for use."""
    print("Setting up database for first time use.")
    print(
        "Note: If this command fails, please either create an issue in the 'Ops Data Store' project in GitLab, or "
        "contact MAGIC at magic@bas.ac.uk with the output of this command."
    )
    client = DBClient()

    try:
        client.setup()
        print("Ok. Database setup completed normally.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print(e)
        print("No. Database setup failed.")
        raise typer.Abort() from e


@app.command(help="Execute contents of an SQL against database.")
def run(input_path: Annotated[Path, typer.Option()]) -> None:
    """Load contents of SQL file and execute against database."""
    client = DBClient()

    logger.info("Loading file contents and running inside database.")

    logger.info(f"Input path: {input_path.resolve()}")
    if not input_path.exists():
        logger.error("Input path not found.")
        print(f"No. Input path '{input_path.resolve()}' does not exist.")
        raise typer.Abort()
    if not input_path.is_file():
        logger.error("Input path not a file.")
        print(f"No. Input path '{input_path.resolve()}' is not a file.")
        raise typer.Abort()

    try:
        print(f"Executing SQL from input file at '{input_path.resolve()}' against app database.")
        client.execute(query=input_path.read_text())
    except (psycopg.ProgrammingError, psycopg.OperationalError) as e:
        logger.error(e, exc_info=True)
        print("No. Error running commands in input file.")
        raise typer.Abort() from e

    logger.info("Input file loaded and executed normally.")
    print("Ok. Complete.")


@app.command(help="Save database as backup file.")
def backup(output_path: Annotated[Path, typer.Option()]) -> None:
    """Save contents of database into an SQL file."""
    client = DBClient()

    logger.info("Saving app database to file.")
    logger.info(f"Output path: {output_path.resolve()}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        client.dump(path=output_path)
        logger.info("App database saved to file normally.")
        print("Ok. Complete.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print("No. Error saving database.")
        raise typer.Abort() from e
