from pprint import pprint

import typer

from ops_data_store.config import Config

app = typer.Typer()

config = Config()


@app.command(help="Display the current app configuration.")
def show() -> None:
    """Display the current app configuration."""
    pprint(config.dump())
