import logging

import typer

from ops_data_store.backup import BackupClient
from ops_data_store.config import Config

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")


@app.command(help="Backup database and managed datasets.")
def now() -> None:
    """Create backups as part of managed file set."""
    client = BackupClient()
    print(f"Backing up database and managed datasets backup as part of file set at: '{config.BACKUPS_PATH.resolve()}'.")

    client.backup()
    print("Ok. Complete.")
