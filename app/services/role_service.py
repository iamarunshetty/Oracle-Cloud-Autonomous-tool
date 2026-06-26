"""
Role service – wraps Oracle Fusion role assignment REST calls.
"""

from __future__ import annotations

from typing import Any

from app.api.client import OracleAPIClient
from app.api.endpoints import OracleEndpoints
from app.utils.logger import get_logger

logger = get_logger("oracle_fusion_tool.services.role")


class RoleService:
    """High-level operations for Oracle Fusion role assignments."""

    def __init__(self, client: OracleAPIClient) -> None:
        self._client = client

    def list_roles(self, query: str = "", limit: int = 100) -> list[dict[str, Any]]:
        """Return available Oracle Fusion roles."""
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["q"] = f"roleName LIKE '%{query}%'"
        result = self._client.get(OracleEndpoints.ROLES, params=params)
        return result.get("items", result if isinstance(result, list) else [])

    def get_user_roles(self, username: str) -> list[dict[str, Any]]:
        """Return roles currently assigned to a user."""
        params = {"q": f"userName={username}"}
        result = self._client.get(OracleEndpoints.USER_ROLE_MEMBERSHIPS, params=params)
        return result.get("items", result if isinstance(result, list) else [])

    def assign_role(self, username: str, role_name: str) -> dict[str, Any]:
        """Assign a role to a user."""
        logger.info("Assigning role '%s' to user '%s'.", role_name, username)
        payload = {"userName": username, "roleName": role_name}
        result = self._client.post(OracleEndpoints.USER_ROLE_MEMBERSHIPS, payload)
        logger.info("Role '%s' assigned to '%s'.", role_name, username)
        return result

    def remove_role(self, role_membership_id: str) -> None:
        """Remove a role from a user by membership record ID."""
        logger.info("Removing role membership: %s", role_membership_id)
        path = OracleEndpoints.format(
            OracleEndpoints.USER_ROLE_DETAIL, role_membership_id=role_membership_id
        )
        self._client.delete(path)
        logger.info("Role membership %s removed.", role_membership_id)
