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
            self.logger.info("Bind result: %s", self.client.result["description"])
        except ldap.LDAPError as e:
            self.logger.error(e, exc_info=True)
            error_msg = "Failed to connect to LDAP server."
            raise RuntimeError(error_msg) from e
        finally:
            self.client.unbind_s()
