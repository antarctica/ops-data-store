import logging
from pprint import pprint

import typer

from ops_data_store.config import Config

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")




@app.command(help="Display the current app configuration.")
def show() -> None:
    """Display the current app configuration."""
    try:
        logger.info("Checking app config.")
        config.validate()
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        typer.echo("No. Application config is invalid. Check with `ods-ctl config check`.")
        raise typer.Abort() from e
    logger.info("App config ok.")

    logger.info("Dumping app config.")
    pprint(config.dump())
