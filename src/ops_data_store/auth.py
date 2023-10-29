import logging

import ldap
import requests
from msal import ConfidentialClientApplication

from ops_data_store.config import Config


class AzureClient:
    """
    Application client for Azure.

    Used for accessing resources protected by the Microsoft Azure Entra (Active Directory).
    """

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating Azure client.")

        self.client = ConfidentialClientApplication(
            authority=self.config.AUTH_AZURE_AUTHORITY,
            client_id=self.config.AUTH_AZURE_CLIENT_ID,
            client_credential=self.config.AUTH_AZURE_CLIENT_SECRET,
        )

    def get_token(self) -> str:
        """
        Acquire Azure access token.

        The Azure client includes a cache to avoid requesting new tokens unnecessarily.
        """
        self.logger.info("Attempting to acquire access token silently (from cache).")
        result = self.client.acquire_token_silent(self.config.AUTH_AZURE_SCOPES, account=None)

        if not result:
            self.logger.info("Failed to acquire token silently, attempting to request fresh token.")
            result = self.client.acquire_token_for_client(scopes=self.config.AUTH_AZURE_SCOPES)

        try:
            self.logger.info("Access token: %s", result.get("access_token"))
            return result["access_token"]
        except KeyError as e:
            self.logger.error(e, exc_info=True)
            self.logger.info("Error: %s", result["error"])
            self.logger.info("Error description: %s", result["error_description"])
            self.logger.info("Correlation ID: %s", result["correlation_id"])

            error_msg = "Failed to acquire Azure token."
            raise RuntimeError(error_msg) from e

    def get_group_members(self, group_id: str) -> list[str]:
    def check_group(self, group_id: str) -> None:
        """
        Get User Principal Name's (UPNs) of members of an Azure group.
        Check Azure group exists.

        In Azure the UPN is the user's email address (e.g. conwat@bas.ac.uk).
        Raises a ValueError if the specified group does not exist

        :type group_id: str
        :param group_id: Azure AD group ID
        :rtype List of dict
        :return: List of group member UPNs
        """
        self.logger.info("Getting members of group ID: %s from MS Graph API.", group_id)
        self.logger.info("Checking group ID: %s exists.", group_id)

        r = requests.get(
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}/members",
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            timeout=10,
        )
        r.raise_for_status()

        upns = [member["userPrincipalName"] for member in r.json()["value"]]
        self.logger.debug("Members (%s): %s", len(upns), ", ".join(upns))
        return upns
        if (
            r.status_code == 400
            and "error" in r.json()
            and "message" in r.json()["error"]
            and "Invalid object identifier" in r.json()["error"]["message"]
        ):
            msg = f"Group ID: {group_id} does not exist."
            self.logger.error(msg)
            raise ValueError(msg) from None

        self.logger.info("Group ID: %s exists.", group_id)

    def get_group_name(self, group_id: str) -> str:
        """
        Get display name of Azure group.

        :type group_id: str
        :param group_id: Azure AD group ID
        :rtype str
        :return: Group display name
        """
        self.logger.info("Getting display name of group ID: %s from MS Graph API.", group_id)
        r = requests.get(
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            timeout=10,
        )
        r.raise_for_status()

        self.logger.debug("displayName: %s", r.json()["displayName"])

        return r.json()["displayName"]


class LDAPClient:
    """
    Application client for LDAP.

    Used for managing resources within an LDAP directory.
    """

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating LDAP client.")

        self.client = ldap.initialize(self.config.AUTH_LDAP_URL)

    def _search_objects(self, base: str, object_ids: list[str], attributes: list[str]) -> list[str]:
        """
        Check objects exist.

        Finds one or more objects within the LDAP server. Any objects that are found are returned as a Distinguished
        Names (DNs). (E.g. `cn=conwat` will be returned as `cn=conwat,ou=users,dc=example,dc=com`).

        Because objects are searched for in a specific base (typically an OU), object names should be specified as
        partial names, not a full DN (E.g. `cn=admins` not `cn=admins,ou=groups,dc=example,dc=com`).

        :type base: str
        :param base: Base DN to search in, e.g. `ou=users,dc=example,dc=com`
        :type object_ids: list[str]
        :param object_ids: One or more object IDs with correct prefix for the LDAP server, e.g. `cn=conwat`
        :type attributes: list[str]
        :param attributes: Attributes to return for each object, e.g. `["dn"]`
        :rtype list[str]
        :return: DNs for any object IDs found in the LDAP server
        """
        ldap_filter = f"(|{''.join([f'({object_id})' for object_id in object_ids])})"
        dns_searched = [f"{object_id},{base}" for object_id in object_ids]

        self.logger.info("Attempting to bind to LDAP server.")
        self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
        self.logger.info("LDAP bind successful.")

        self.logger.info("Searching for: %s in: %s with filter: %s.", attributes, base, ldap_filter)
        results = self.client.search_s(base=base, scope=ldap.SCOPE_SUBTREE, filterstr=ldap_filter, attrlist=attributes)
        self.client.unbind_s()
        self.logger.debug("Results: %s", results)

        dns_found = [result[0] for result in results]
        dns_missing = list(set(dns_searched) - set(dns_found))
        self.logger.info("Distinguished names found: %s", dns_found)
        self.logger.info("Distinguished names missing: %s", dns_missing)

        return dns_found

    def verify_bind(self) -> None:
        """Check credentials allow LDAP bind."""
        try:
            self.logger.info("Attempting to bind to LDAP server.")
            self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
            self.logger.info("LDAP bind successful.")
        except ldap.LDAPError as e:
            self.logger.error(e, exc_info=True)
            error_msg = "Failed to connect to LDAP server."
            raise RuntimeError(error_msg) from e
        finally:
            self.client.unbind_s()

    def check_users(self, user_ids: list[str]) -> list[str]:
        """
        Check users exist.

        Searches for one or more users in the LDAP server. Any users that are found are returned as a Distinguished
        Name (DN). (E.g. `cn=conwat` will be returned as `cn=conwat,ou=users,dc=example,dc=com` if it exists).

        Users should be specified as a partial name, not a full DN as searches are scoped to configured groups OU
        already. (E.g. `cn=conwat` not `cn=conwat,ou=users,dc=example,dc=com`).

        :type user_ids: list[str]
        :param user_ids: One or more user IDs with correct naming context prefix for the LDAP server, e.g. `cn=conwat`
        :rtype list[str]
        :return: One or more user DNs found in the LDAP server
        """
        ldap_base = f"ou={self.config.AUTH_LDAP_OU_USERS},{self.config.AUTH_LDAP_BASE_DN}"
        return self._search_objects(base=ldap_base, object_ids=user_ids, attributes=["dn"])

    def check_groups(self, group_ids: list[str]) -> list[str]:
        """
        Check groups exist.

        Searches for one or more groups in the LDAP server. Any groups that are found are returned as a Distinguished
        Name (DN). (E.g. `cn=admins` will be returned as `cn=admins,ou=groups,dc=example,dc=com` if it exists).

        Groups should be specified as a partial name, not a full DN as searches are scoped to configured groups OU
        already. (E.g. `cn=admins` not `cn=admins,ou=groups,dc=example,dc=com`).

        :type group_ids: list[str]
        :param group_ids: One or more group IDs with correct naming context prefix for the LDAP server, e.g. `cn=admins`
        :rtype list[str]
        :return: One or more group DNs found in the LDAP server
        """
        ldap_base = f"ou={self.config.AUTH_LDAP_OU_GROUPS},{self.config.AUTH_LDAP_BASE_DN}"
        return self._search_objects(base=ldap_base, object_ids=group_ids, attributes=["dn"])

    def get_group_members(self, group_dn: str) -> list[str]:
        """
        Get Distinguished Names (DNs) of members of a group.

        :type group_dn: str
        :param group_dn: Group DN, with correct naming context prefix for the LDAP server, e.g. `cn=admins`
        :rtype list[str]
        :return: List of member DNs
        """
        ldap_filter = f"({group_dn.split(',')[0]})"
        ldap_base = ",".join(group_dn.split(",")[1:])

        self.logger.info("Attempting to bind to LDAP server.")
        self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
        self.logger.info("LDAP bind successful.")

        self.logger.info("Searching in: %s with filter: %s.", ldap_base, ldap_filter)
        results = self.client.search_s(
            base=ldap_base, scope=ldap.SCOPE_SUBTREE, filterstr=ldap_filter, attrlist=["member"]
        )
        self.client.unbind_s()
        self.logger.debug("Results: %s", results)

        return [member.decode() for member in results[0][1]["member"]]

    def add_to_group(self, group_dn: str, user_dns: list[str]) -> None:
        """
        Add users to group as members.

        The group and all members to be added should be specified using their Distinguished Names (DNs).

        :type group_dn: str
        :param group_dn: Group DN, with correct naming context prefix for the LDAP server, e.g. `cn=admins`
        :type user_dns: list[str]
        :param user_dns: One or more user DNs with correct naming context prefix for the LDAP server, e.g. `cn=conwat`
        """
        self.logger.info("Attempting to bind to LDAP server.")
        self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
        self.logger.info("LDAP bind successful.")

        self.logger.info("Group to add to: %s.", group_dn)
        self.logger.info("Users to add: %s.", user_dns)
        self.client.modify_s(dn=group_dn, modlist=[(ldap.MOD_ADD, "member", [member.encode() for member in user_dns])])

    def remove_from_group(self, group_dn: str, user_dns: list[str]) -> None:
        """
        Remove members from group.

        The group and all members to be removed should be specified using their Distinguished Names (DNs).

        :type group_dn: str
        :param group_dn: Group DN, with correct naming context prefix for the LDAP server, e.g. `cn=admins`
        :type user_dns: list[str]
        :param user_dns: One or more user DNs with correct naming context prefix for the LDAP server, e.g. `cn=conwat`
        """
        self.logger.info("Attempting to bind to LDAP server.")
        self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
        self.logger.info("LDAP bind successful.")

        self.logger.info("Group to remove from: %s.", group_dn)
        self.logger.info("Users to remove: %s.", user_dns)
        result = self.client.modify_s(
            dn=group_dn, modlist=[(ldap.MOD_DELETE, "member", [member.encode() for member in user_dns])]
        )
        print(result)
