import logging
from typing import Annotated

import typer

from ops_data_store.auth import AzureClient, LDAPClient, SimpleSyncClient
from ops_data_store.config import Config

app = typer.Typer()

config = Config()
logger = logging.getLogger("app")


def _print_sync_evaluation(eval_result: dict[str, list[str]]) -> None:
    print("=== Sync Evaluation ===")
    print(f"\nUsers to be added to target group [{len(eval_result['missing'])}]:")
    for user in eval_result["missing"]:
        print(f" + {user}")
    print(f"\nUsers to be removed from target group [{len(eval_result['remove'])}]:")
    for user in eval_result["remove"]:
        print(f" - {user}")
    print(f"\nUsers not in target LDAP server (need to be registered first) [{len(eval_result['unknown'])}]:")
    for user in eval_result["unknown"]:
        print(f" ! {user}")
    print(f"\nUsers in source and target group (no change, for reference) [{len(eval_result['present'])}]:")
    print(f" = {', '.join(eval_result['present'])}")
    print(f"\nAll users in source group (for reference) [{len(eval_result['source'])}]:")
    print(f" > {', '.join(eval_result['source'])}")
    print(f"\nAll users in target group (for reference) [{len(eval_result['target'])}]:")
    print(f" < {', '.join(eval_result['target'])}")
    print("\n")


@app.command(help="Check auth (Azure/LDAP) connectivity.")
def check() -> None:
    """Check Auth connection."""
    print("Note: If this command fails, please check the configured credentials and external internet connectivity.")
    print(
        "If problems persist, create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at "
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


@app.command(help="Sync group members from Azure to LDAP.")
def sync(
    azure_group: Annotated[str, typer.Option("--azure-group", "-ag", help="ID of Azure group")],
    ldap_group: Annotated[str, typer.Option("--ldap-group", "-lg", help="ID of LDAP group")],
) -> None:
    """Sync group members from Azure to LDAP."""
    print("Note: If this command fails, please run the `ods-ctl auth check` command and resolve an errors.")
    print(
        "If problems persist, create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at "
        "magic@bas.ac.uk with the output of this command."
    )

    sync_client = SimpleSyncClient(azure_group_id=azure_group, ldap_group_id=ldap_group)

    try:
        _print_sync_evaluation(eval_result=sync_client.evaluate())

        if not typer.confirm("Continue with these additions and removals?"):
            print("Ok. Sync aborted.")
            raise typer.Abort()

        print("Syncing...")
        sync_client.sync()
        _print_sync_evaluation(eval_result=sync_client.evaluate())
        print("Ok. Sync completed.")
    except RuntimeError as e:
        logger.error(e, exc_info=True)
        print(f"No. {e} Sync aborted.")
        raise typer.Abort() from e
