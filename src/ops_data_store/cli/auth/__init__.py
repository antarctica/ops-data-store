import logging

import typer

from ops_data_store.auth import AzureClient, LDAPClient
from ops_data_store.config import Config

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")


@app.command(help="Check auth (Azure/LDAP) connectivity.")
def check() -> None:
    """Check Auth connection."""
    print("Note: If this command fails, please check the configured credentials and external connectivity.")
    print(
        "If problem persists, create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at "
        "magic@bas.ac.uk with the output of this command."
    )

    azure_client = AzureClient()
    ldap_client = LDAPClient()

    logger.info("Checking Azure connectivity.")
    azure_client.get_token()
    logger.info("Azure connectivity ok.")
    logger.info("Checking LDAP connectivity.")
    ldap_client.verify_bind()
    logger.info("LDAP connectivity ok.")
    print("Ok. Auth connection successful.")
