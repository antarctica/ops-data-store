from __future__ import annotations

from typing import Optional

import typer

from ops_data_store.cli.auth import app as auth_cli
from ops_data_store.cli.config import app as config_cli
from ops_data_store.cli.db import app as db_cli
from ops_data_store.config import Config

config = Config()

app = typer.Typer(name="ods-ctl", help="BAS MAGIC Operations Data Store control CLI.")
app.add_typer(auth_cli, name="auth", help="Manage application authentication/authorisation.")
app.add_typer(config_cli, name="config", help="Manage application configuration.")
app.add_typer(db_cli, name="db", help="Manage application database.")
_version_option = typer.Option(None, "-v", "--version", is_eager=True, help="Show application version and exit.")


@app.callback(invoke_without_command=True)
def cli(version: Optional[bool] = _version_option) -> None:
    """Display application version."""
    if version:
        print(config.VERSION)
        raise typer.Exit()
