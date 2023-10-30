def test_check_target_users__ldap_check_users(user_ids: list[str]) -> list[str]:
    """
    Return pre-defined results if the correct search terms are given.

    Mocked LDAPClient.get_users call for testing the `SimpleSyncCLient._check_target_users()` method.
    """
    if "cn=bob" in user_ids:
        return ["cn=bob,ou=users,dc=example,dc=com"]
    if "cn=darren" in user_ids:
        return ["cn=darren,ou=users,dc=example,dc=com"]

    return []
