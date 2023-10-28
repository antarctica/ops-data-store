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
        """
        Get User Principal Name's (UPNs) of members of an Azure group.

        In Azure the UPN is the user's email address (e.g. conwat@bas.ac.uk).

        :type group_id: str
        :param group_id: Azure AD group ID
        :rtype List of dict
        :return: List of group member UPNs
        """
        self.logger.info("Getting members of group ID: %s from MS Graph API.", group_id)
        r = requests.get(
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}/members",
            headers={"Authorization": f"Bearer {self.get_token()}"},
            timeout=10,
        )
        r.raise_for_status()

        upns = [member["userPrincipalName"] for member in r.json()["value"]]
        self.logger.debug("Members (%s): %s", len(upns), ", ".join(upns))
        return upns

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

        Searches for users in the configured user/people OU. Any users that are not found are returned.

        :type user_ids: list[str]
        :param user_ids: One or more user IDs with correct naming context prefix for the LDAP server, e.g. `cn=conwat`
        :rtype list[str]
        :return: One or more user IDs not found in the LDAP server
        """
        ldap_base = f"ou={self.config.AUTH_LDAP_OU_USERS},{self.config.AUTH_LDAP_BASE_DN}"
        ldap_filter = f"(|{''.join([f'({user_id})' for user_id in user_ids])})"

        self.logger.info("Attempting to bind to LDAP server.")
        self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
        self.logger.info("LDAP bind successful.")

        self.logger.info("Searching in: %s with filter: %s.", ldap_base, ldap_filter)
        results = self.client.search_s(base=ldap_base, scope=ldap.SCOPE_SUBTREE, filterstr=ldap_filter, attrlist=["dn"])
        self.client.unbind_s()
        self.logger.debug("Results: %s", results)

        dns_searched = [f"{user_id},{ldap_base}" for user_id in user_ids]
        dns_found = [result[0] for result in results]
        dns_missing = list(set(dns_searched) - set(dns_found))
        self.logger.info("Distinguished names found: %s", dns_found)
        self.logger.info("Distinguished names missing: %s", dns_missing)

        return [dn.split(",")[0] for dn in dns_missing]
