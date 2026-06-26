"""
Password service – stub implementation.

TODO: Replace with Oracle Identity Governance (OIG) / Fusion HCM calls.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.models.audit import AuditAction
from app.services.base import audit

logger = logging.getLogger(__name__)

# Stub login-status store
_LOGIN_STATUS: dict[str, dict] = {}


class PasswordService:
    def reset_password(self, username: str, performed_by: str = "system") -> bool:
        """
        Trigger a password reset email / token.

        TODO: POST /idm/v1/users/{username}/reset-password
        """
        logger.info("[STUB] Password reset triggered for %s", username)
        audit(
            AuditAction.RESET_PASSWORD,
            performed_by=performed_by,
            target_username=username,
            description="Password reset initiated",
        )
        return True

    def force_change_password(self, username: str, performed_by: str = "system") -> bool:
        """
        Force the user to change password on next login.

        TODO: PATCH .../userAccounts/<id> {mustChangePassword: true}
        """
        logger.info("[STUB] Force password change for %s", username)
        audit(
            AuditAction.FORCE_CHANGE_PASSWORD,
            performed_by=performed_by,
            target_username=username,
            description="Force password change on next login",
        )
        return True

    def unlock_account(self, username: str, performed_by: str = "system") -> bool:
        """
        Unlock a locked-out user account.

        TODO: POST /idm/v1/users/{username}/unlock
        """
        logger.info("[STUB] Unlocking account for %s", username)
        _LOGIN_STATUS.setdefault(username, {})["locked"] = False
        audit(
            AuditAction.UNLOCK_ACCOUNT,
            performed_by=performed_by,
            target_username=username,
            description="User account unlocked",
        )
        return True

    def get_login_status(self, username: str) -> dict:
        """
        Return login/lock status for a user.

        TODO: GET /idm/v1/users/{username}/status
        """
        return _LOGIN_STATUS.get(username, {"locked": False, "last_login": None})


password_service = PasswordService()
