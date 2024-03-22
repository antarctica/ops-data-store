from pathlib import Path


def test_check_target_users__ldap_check_users(user_ids: list[str]) -> list[str]:
    """
    Return pre-defined results if the correct search terms are given.

    Mocked `LDAPClient.get_users` call for testing the `SimpleSyncClient._check_target_users()` method.
    """
    if "cn=bob" in user_ids:
        return ["cn=bob,ou=users,dc=example,dc=com"]
    if "cn=darren" in user_ids:
        return ["cn=darren,ou=users,dc=example,dc=com"]

    return []


def data_client_export_touch_path(path: Path) -> None:
    """
    Simulate creating a data export.

    Mocked `DataClient.export` method.

    Requires exist_ok=False to ensure pre-existing files are first removed.
    """
    path.touch(exist_ok=False)


def db_client_dump_touch_path(path: Path) -> None:
    """
    Simulate creating a DB dump.

    Mocked `DBClient.dump` method.

    Requires exist_ok=False to ensure pre-existing files are first removed.
    """
    path.touch(exist_ok=False)
