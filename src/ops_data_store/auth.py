from __future__ import annotations

import logging
import weakref
from typing import Optional

import ldap
import requests
from ldap.ldapobject import SimpleLDAPObject
from msal import ConfidentialClientApplication

from ops_data_store.config import Config


class AzureClient:
    """
    Application Azure client.

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

    def _get_token(self) -> str:
        """Acquire Azure access token."""
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

            msg = "Failed to acquire Azure token."
            raise RuntimeError(msg) from e

    def check_token(self) -> None:
        """
        Check token can be requested.

        Raises an exception if binding fails.
        """
        self._get_token()

    def check_group(self, group_id: str) -> None:
        """
        Check Azure group exists.

        Raises a ValueError if the specified group does not exist
        """
        self.logger.info("Checking group ID: %s exists.", group_id)

        r = requests.get(
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}",
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=10,
        )

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
        """Get display name of Azure group."""
        self.logger.info("Getting display name of group ID: %s.", group_id)
        r = requests.get(
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}",
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=10,
        )
        r.raise_for_status()

        self.logger.info("group ID: %s DisplayName is: %s", group_id, r.json()["displayName"])
        return r.json()["displayName"]

    def get_group_members(self, group_id: str) -> list[str]:
        """
        Get User Principal Name's (UPNs) of members of an Azure group.

        In Azure the UPN is the user's email address (e.g. conwat@bas.ac.uk).
        """
        self.logger.info("Getting members of group ID: %s from MS Graph API.", group_id)
        r = requests.get(
            url=f"{self.config.AUTH_MS_GRAPH_ENDPOINT}/groups/{group_id}/members",
            headers={"Authorization": f"Bearer {self._get_token()}"},
            timeout=10,
        )
        r.raise_for_status()

        upns = [member["userPrincipalName"] for member in r.json()["value"]]
        self.logger.info("Members (%s): %s", len(upns), ", ".join(upns))
        return upns


class LDAPClient:
    """
    Application LDAP client.

    Used for managing resources within an LDAP directory.

    This client will maintain bound to the LDAP server until the class instance is destroyed. It will bind automatically
    when first needed.
    """

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating LDAP client.")

        self.client = ldap.initialize(self.config.AUTH_LDAP_URL)
        self._is_bound = False

        self._finalizer = weakref.finalize(self, self._unbind, self.logger, self.client)

    @classmethod
    def _unbind(cls: LDAPClient, logger: logging.Logger, client: SimpleLDAPObject) -> None:
        """
        Unbind from LDAP server.

        This method is called as the '_finalizer' when the class instance is destroyed, as such it cannot access any
        class attributes and is passed the logger, client, etc. as arguments.
        """
        logger.info("Attempting to unbind from LDAP server.")
        client.unbind_s()
        logger.info("LDAP unbind successful.")

    def _bind(self) -> None:
        """Bind to LDAP server."""
        self.logger.info("Attempting to bind to LDAP server.")

        if self._is_bound:
            self.logger.info("Skipping as already bound.")
            return

        try:
            self.client.simple_bind_s(who=self.config.AUTH_LDAP_BIND_DN, cred=self.config.AUTH_LDAP_BIND_PASSWORD)
            self.logger.info("LDAP bind successful.")
            self._is_bound = True
        except ldap.LDAPError as e:
            self.logger.error(e, exc_info=True)
            msg = "Failed to connect to LDAP server."
            raise RuntimeError(msg) from e

    def _search_objects(self, base: str, ldap_filter: str, attributes: list[str]) -> dict:
        """
        Search for objects.

        Finds one or more objects within the LDAP server, returning requested attributes for each result (e.g. `["DN"]`).

        The `base` should be a valid base DN and the `ldap_filter` a valid LDAP search filter.
        """
        self._bind()
        self.logger.info("Searching for: %s in: %s with filter: %s.", attributes, base, ldap_filter)
        results = self.client.search_s(base=base, scope=ldap.SCOPE_SUBTREE, filterstr=ldap_filter, attrlist=attributes)
        self.logger.debug("Results: %s", results)

        return results

    def _check_objects(self, base: str, object_ids: list[str]) -> list[str]:
        """
        Check objects exist.

        Any objects that are found are returned as a Distinguished Names (DNs). (E.g. `cn=conwat` will be returned as
        `cn=conwat,ou=users,dc=example,dc=com`).

        Because objects are searched for in a specific base (typically an OU), object IDs should be specified as
        partial names, not a full DN (E.g. `cn=admins` not `cn=admins,ou=groups,dc=example,dc=com`).

        The `base` should be a valid base DN and `object_ids`, one or more object IDs with correct prefix for the
        LDAP server, e.g. `cn=conwat`.
        """
        ldap_filter = f"(|{''.join([f'({object_id})' for object_id in object_ids])})"
        dns_searched = [f"{object_id},{base}" for object_id in object_ids]

        results = self._search_objects(base=base, ldap_filter=ldap_filter, attributes=["dn"])
        dns_found = [result[0] for result in results]
        dns_missing = list(set(dns_searched) - set(dns_found))
        self.logger.info("Distinguished names found: %s", dns_found)
        self.logger.info("Distinguished names missing: %s", dns_missing)

        return dns_found

    def check_bind(self) -> None:
        """
        Check credentials allow LDAP bind.

        Raises a LDAPError exception if binding fails.
        """
        self._bind()

    def check_users(self, user_ids: list[str]) -> list[str]:
        """
        Check users exist.

        Searches for one or more users in the LDAP server. Any users that are found are returned as a Distinguished
        Name (DN). (E.g. `cn=conwat` will be returned as `cn=conwat,ou=users,dc=example,dc=com` if it exists).

        Users should be specified as a partial name, not a full DN as searches are scoped to configured groups OU
        already. (E.g. `cn=conwat` not `cn=conwat,ou=users,dc=example,dc=com`).
        """
        ldap_base = f"ou={self.config.AUTH_LDAP_OU_USERS},{self.config.AUTH_LDAP_BASE_DN}"
        return self._check_objects(base=ldap_base, object_ids=user_ids)

    def check_groups(self, group_ids: list[str]) -> list[str]:
        """
        Check groups exist.

        Searches for one or more groups in the LDAP server. Any groups that are found are returned as a Distinguished
        Name (DN). (E.g. `cn=admins` will be returned as `cn=admins,ou=groups,dc=example,dc=com` if it exists).

        Groups should be specified as a partial name, not a full DN as searches are scoped to configured groups OU
        already. (E.g. `cn=admins` not `cn=admins,ou=groups,dc=example,dc=com`).
        """
        ldap_base = f"ou={self.config.AUTH_LDAP_OU_GROUPS},{self.config.AUTH_LDAP_BASE_DN}"
        return self._check_objects(base=ldap_base, object_ids=group_ids)

    def get_group_members(self, group_dn: str) -> list[str]:
        """
        Get Distinguished Names (DNs) of members of a group.

        The group DN should use the correct naming context prefix for the LDAP server, e.g. `cn=admins`.
        """
        ldap_filter = f"({group_dn.split(',')[0]})"
        ldap_base = ",".join(group_dn.split(",")[1:])

        results = self._search_objects(base=ldap_base, ldap_filter=ldap_filter, attributes=["member"])

        return [member.decode() for member in results[0][1]["member"]]

    def add_to_group(self, group_dn: str, user_dns: list[str]) -> None:
        """
        Add users to group as members.

        The group and all members to be added should be specified using their Distinguished Names (DNs).
        """
        if len(user_dns) == 0:
            self.logger.info("Skipping as no users specified.")
            return

        self._bind()

        # batch changes to 10 users to prevent requests being too large
        for i in range(0, len(user_dns), 10):
            user_dns_batch = user_dns[i : i + 10]

            self.logger.info("Batch %s of %s.", i + 1, len(user_dns) // 10 + 1)
            self.logger.info("Group to add to: %s.", group_dn)
            self.logger.info("Users to add: %s.", user_dns)
            self.client.modify_s(
                dn=group_dn, modlist=[(ldap.MOD_ADD, "member", [member.encode() for member in user_dns_batch])]
            )

    def remove_from_group(self, group_dn: str, user_dns: list[str]) -> None:
        """
        Remove members from group.

        The group and all members to be removed should be specified using their Distinguished Names (DNs).
        """
        if len(user_dns) == 0:
            self.logger.info("Skipping as no users specified.")
            return

        self._bind()

        # batch changes to 10 users to prevent requests being too large
        for i in range(0, len(user_dns), 10):
            user_dns_batch = user_dns[i : i + 10]

            self.logger.info("Batch %s of %s.", i + 1, len(user_dns) // 10 + 1)
            self.logger.info("Group to remove from: %s.", group_dn)
            self.logger.info("Users to remove: %s.", user_dns)
            self.client.modify_s(
                dn=group_dn, modlist=[(ldap.MOD_DELETE, "member", [member.encode() for member in user_dns_batch])]
            )


class SimpleSyncClient:
    """
    Simple implementation of syncing users from Azure groups to LDAP.

    In this simple client, users from one or more (source) Azure groups are synced to a single (target) LDAP group.
    Members in the target group are replaced by the union of those in the source. Any LDAP members not in the Azure
    group are dropped.
    """

    def __init__(self, azure_group_ids: list[str], ldap_group_id: str) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating sync client.")

        self.azure_client = AzureClient()
        self.ldap_client = LDAPClient()

        self.logger.info(f"Azure group IDs: {azure_group_ids}")
        self.logger.info(f"LDAP group ID: {ldap_group_id}")

        self._source_group_ids: list[str] = azure_group_ids
        self._target_group_id: str = ldap_group_id
        self._target_group_dn: Optional[str] = None

        self._source_user_ids: list[str] = []
        self._target_user_ids: list[str] = []

        self._user_ids_already_in_target: list[str] = []
        self._user_ids_missing_in_target: list[str] = []
        self._user_ids_unknown_in_target: list[str] = []
        self._user_ids_unknown_in_source: list[str] = []

        self._target_dns_del: list[str] = []
        self._target_dns_add: list[str] = []

        self._evaluated: bool = False

    def _check_groups_exist(self) -> Optional[str]:
        """
        Check Azure and LDAP groups exist.

        Returns Distinguished Name (DN) for LDAP group if it exists.
        """
        for group_id in self._source_group_ids:
            try:
                self.azure_client.check_group(group_id=group_id)
            except ValueError as e:
                msg = f"Azure group {group_id} does not exist."
                self.logger.error(e, exc_info=True)
                raise RuntimeError(msg) from e

        ldap_group_uid = f"{self.config.AUTH_LDAP_NAME_CONTEXT_GROUPS}={self._target_group_id}"
        results = self.ldap_client.check_groups(group_ids=[ldap_group_uid])
        if len(results) == 1 and self._target_group_id in results[0]:
            return results[0]

        msg = f"LDAP group {self._target_group_id} does not exist."
        self.logger.error(msg)
        raise RuntimeError(msg) from None

    def _check_target_users(self) -> None:
        """
        Check users from source not in target exist in target.

        E.g. If:
        - a source group contains users `alice`, `bob` and `connie`
        - a target group contains `alice` and `darren`
        - the target more widely contains `alice`, `bob` and `darren` (but not `connie`)
        Then:
        - `alice` is already in the target group and is ignored as by implication they exist in the target
        - `bob` and `connie` are searched for in the target
        - `bob` is found and can be added to the target group
        - `connie` is not found and cannot be added to the target group as they don't exist in the target
        """
        # For users not in the target already, convert IDs to UIDs (e.g. `conwat` -> `cn=conwat`)
        search_ids = list(set(self._source_user_ids) - set(self._target_user_ids))
        search_uids = [f"{self.config.AUTH_LDAP_NAME_CONTEXT_USERS}={user}" for user in search_ids]

        # Search for users in target, converting DNs to IDs (e.g. `cn=conwat,ou=users,dc=example,dc=com` -> `conwat`)
        found_dns = self.ldap_client.check_users(user_ids=search_uids)
        found_ids = [user.split(",")[0].split("=")[1] for user in found_dns]

        # Distinguish between users not in target and those not in target group
        self._user_ids_unknown_in_target = list(set(search_ids) - set(found_ids))
        self._user_ids_missing_in_target = found_ids

        # Store DNs for users to be removed and added
        search_ids = list(set(self._target_user_ids) - set(self._source_user_ids))
        search_uids = [f"{self.config.AUTH_LDAP_NAME_CONTEXT_USERS}={user}" for user in search_ids]
        self._target_dns_del = self.ldap_client.check_users(user_ids=search_uids)
        self._target_dns_add = found_dns

    def _get_source_user_ids(self) -> None:
        """
        Store members of source Azure groups as usernames.

        Azure group members are identified by their User Principal Name (UPN, an email address). These need converting
        into generic usernames for comparison with LDAP users. E.g. a user `conwat@bas.ac.uk` becomes `conwat`.
        """
        members = []

        for group_id in self._source_group_ids:
            members.extend(self.azure_client.get_group_members(group_id=group_id))

        self._source_user_ids = [member.split("@")[0] for member in members]

    def _get_target_user_ids(self) -> None:
        """
        Store members of target LDAP group as usernames.

        LDAP group members are identified by their Distinguished Name (DN). These need converting into generic
        usernames for comparison with Azure users. E.g. a user `cn=conwat,ou=users,dc=example,dc=com` becomes `conwat`.
        """
        members = self.ldap_client.get_group_members(group_dn=self._target_group_dn)
        self._target_user_ids = [member.split(",")[0].split("=")[1] for member in members]

    def evaluate(self) -> dict[str, list[str]]:
        """
        Assess syncing users from one or more Azure groups to an LDAP group.

        This method performs no modifications to LDAP. It examines the members of the Azure and LDAP groups
        (if they exist) and determines which users should be added to or removed from the LDAP group.

        It returns a dictionary of [keys] and lists of users that are:
        -  [target]: in the source group (for information)
        -  [source]: in the target group (for information)
        - [present]: in both the source and target groups (no change needed)
        - [missing]: in the source group but not the target group (can be added)
        - [unknown]: not in the target server (cannot be added)
        -  [remove]: in the target group but not the source group (can be removed)
        """
        self.logger.info("Evaluating Azure to LDAP group sync.")

        self._target_group_dn = self._check_groups_exist()

        self._get_source_user_ids()
        self._get_target_user_ids()
        self._check_target_users()
        self._user_ids_already_in_target = list(set(self._source_user_ids) & set(self._target_user_ids))
        self._user_ids_unknown_in_source = list(set(self._target_user_ids) - set(self._source_user_ids))

        self.logger.info(f" user IDs target: {self._source_user_ids}")
        self.logger.info(f" user IDs source: {self._target_user_ids}")
        self.logger.info(f"user IDs present: {self._user_ids_already_in_target}")
        self.logger.info(f"user IDs missing: {self._user_ids_missing_in_target}")
        self.logger.info(f"user IDs unknown: {self._user_ids_unknown_in_target}")
        self.logger.info(f" user IDs remove: {self._user_ids_unknown_in_source}")
        self.logger.info(f" user DNs to add: {self._target_dns_add}")
        self.logger.info(f" user DNs to del: {self._target_dns_del}")

        self._evaluated = True

        return {
            "source": self._source_user_ids,
            "target": self._target_user_ids,
            "present": self._user_ids_already_in_target,
            "missing": self._user_ids_missing_in_target,
            "unknown": self._user_ids_unknown_in_target,
            "remove": self._user_ids_unknown_in_source,
        }

    def sync(self) -> None:
        """
        Sync users from one or more Azure groups to an LDAP group.

        This method will modify LDAP!

        It depends on the `evaluate` method to check source/target groups exist and determine DNs to add/remove.

        Users are added before removing to prevent trying to remove the last member of a group which isn't permitted.
        """
        if not self._evaluated:
            self.logger.info("Sync not yet evaluated, evaluating first.")

            self.evaluate()

        self.logger.info("Syncing members of Azure groups to LDAP.")
        self.ldap_client.add_to_group(group_dn=self._target_group_dn, user_dns=self._target_dns_add)
        self.ldap_client.remove_from_group(group_dn=self._target_group_dn, user_dns=self._target_dns_del)
