"""
Oracle Fusion REST API endpoint definitions.
Centralised so paths can be updated without touching UI or service code.
"""


class OracleEndpoints:
    """Build Oracle Fusion SCIM/HCM REST API paths relative to a base URL."""

    # SCIM Users endpoint (Oracle Identity Cloud Service / Fusion SCIM)
    SCIM_USERS = "/hcmRestApi/resources/latest/emps"
    SCIM_USER_DETAIL = "/hcmRestApi/resources/latest/emps/{user_id}"

    # Identity – Users (Oracle Fusion Security Console REST)
    IDENTITY_USERS = "/fscmRestApi/resources/latest/userAccounts"
    IDENTITY_USER_DETAIL = "/fscmRestApi/resources/latest/userAccounts/{user_id}"

    # Roles / Role Assignments
    ROLES = "/fscmRestApi/resources/latest/roles"
    USER_ROLE_MEMBERSHIPS = (
        "/fscmRestApi/resources/latest/userRoles"
    )
    USER_ROLE_DETAIL = "/fscmRestApi/resources/latest/userRoles/{role_membership_id}"

    # Account status
    USER_LOCK = "/fscmRestApi/resources/latest/userAccounts/{user_id}/action/lock"
    USER_UNLOCK = "/fscmRestApi/resources/latest/userAccounts/{user_id}/action/unlock"

    @staticmethod
    def format(path: str, **kwargs: str) -> str:
        """Format a path template with named parameters."""
        return path.format(**kwargs)
