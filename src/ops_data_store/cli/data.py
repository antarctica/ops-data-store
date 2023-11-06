import logging
from pathlib import Path
from typing import Annotated

import typer

from ops_data_store.config import Config
from ops_data_store.data import DataClient

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")


@app.command(help="Save managed datasets as GeoPackage.")
def backup(output_path: Annotated[Path, typer.Option()]) -> None:
    """Export managed datasets from DB to GeoPackage file."""
    client = DataClient()

    print(
        f"Note: This command only exports tables for formally managed datasets and QGIS layer styles. "
        f"These tables are: {client.export_tables}"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        client.export(path=output_path)
        logger.info("Managed datasets exported normally.")
        print("Ok. Complete.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print("No. Error saving managed datasets.")
        raise typer.Abort() from e
