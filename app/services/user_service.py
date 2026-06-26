"""
User service – wraps Oracle Fusion user-management REST calls.
"""

from __future__ import annotations

from typing import Any

from app.api.client import OracleAPIClient, APIError
from app.api.endpoints import OracleEndpoints
from app.utils.logger import get_logger

logger = get_logger("oracle_fusion_tool.services.user")


class UserService:
    """High-level operations on Oracle Fusion user accounts."""

    def __init__(self, client: OracleAPIClient) -> None:
        self._client = client

    def create_user(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        description: str = "",
    ) -> dict[str, Any]:
        """Create a new Oracle Fusion user account."""
        logger.info("Creating user: %s", username)
        payload: dict[str, Any] = {
            "userName": username,
            "name": {"givenName": first_name, "familyName": last_name},
            "emails": [{"value": email, "type": "work", "primary": True}],
        }
        if description:
            payload["description"] = description

        result = self._client.post(OracleEndpoints.IDENTITY_USERS, payload)
        logger.info("User created successfully: %s", username)
        return result

    def get_user(self, user_id: str) -> dict[str, Any]:
        """Fetch a user by their Oracle Fusion user ID."""
        path = OracleEndpoints.format(OracleEndpoints.IDENTITY_USER_DETAIL, user_id=user_id)
        return self._client.get(path)

    def search_users(self, query: str = "", limit: int = 50) -> list[dict[str, Any]]:
        """Search users. Returns a list of user dicts."""
        params: dict[str, Any] = {"limit": limit}
        if query:
            params["q"] = f"userName LIKE '%{query}%'"
        result = self._client.get(OracleEndpoints.IDENTITY_USERS, params=params)
        return result.get("items", result if isinstance(result, list) else [])

    def update_user(self, user_id: str, fields: dict[str, Any]) -> dict[str, Any]:
        """Update one or more profile fields of an existing user."""
        logger.info("Updating user %s: fields=%s", user_id, list(fields.keys()))
        path = OracleEndpoints.format(OracleEndpoints.IDENTITY_USER_DETAIL, user_id=user_id)
        result = self._client.patch(path, fields)
        logger.info("User %s updated successfully.", user_id)
        return result

    def lock_user(self, user_id: str) -> dict[str, Any]:
        """Lock a user account, preventing login."""
        logger.info("Locking user: %s", user_id)
        path = OracleEndpoints.format(OracleEndpoints.USER_LOCK, user_id=user_id)
        result = self._client.post(path)
        logger.info("User %s locked.", user_id)
        return result

    def unlock_user(self, user_id: str) -> dict[str, Any]:
        """Unlock a previously locked user account."""
        logger.info("Unlocking user: %s", user_id)
        path = OracleEndpoints.format(OracleEndpoints.USER_UNLOCK, user_id=user_id)
        result = self._client.post(path)
        logger.info("User %s unlocked.", user_id)
        return result
