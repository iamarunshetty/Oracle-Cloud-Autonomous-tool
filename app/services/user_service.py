"""
User service – stub implementation.

TODO: Replace stub methods with Oracle Fusion HCM / Identity REST API calls.
      Base URL: settings.fusion_base_url
      Auth:     secrets.get_credential("fusion-password")
"""
from __future__ import annotations

import logging
from typing import Optional

from app.models.audit import AuditAction
from app.models.user import BulkUserRecord, User, UserStatus
from app.services.base import audit

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# In-memory store used by stubs so the UI can demonstrate functionality
# ---------------------------------------------------------------------------
_USERS: dict[str, User] = {}


class UserService:
    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_user(self, user: User, performed_by: str = "system") -> User:
        """
        Create a user in Oracle Fusion.

        TODO: POST /hcmRestApi/resources/11.13.18.05/userAccounts
        """
        logger.info("[STUB] Creating user: %s", user.username)
        _USERS[user.username] = user
        audit(
            AuditAction.CREATE_USER,
            performed_by=performed_by,
            target_username=user.username,
            description=f"Created user {user.full_name}",
            payload={"email": user.email},
        )
        return user

    def edit_user(
        self,
        username: str,
        updates: dict,
        performed_by: str = "system",
    ) -> Optional[User]:
        """
        Edit user attributes.

        TODO: PATCH /hcmRestApi/resources/.../userAccounts/<id>
        """
        logger.info("[STUB] Editing user: %s", username)
        user = _USERS.get(username)
        if user is None:
            return None
        for k, v in updates.items():
            if hasattr(user, k):
                setattr(user, k, v)
        audit(
            AuditAction.EDIT_USER,
            performed_by=performed_by,
            target_username=username,
            description="User details updated",
            payload=updates,
        )
        return user

    def enable_user(self, username: str, performed_by: str = "system") -> bool:
        """TODO: PATCH .../userAccounts/<id> {status: Active}"""
        logger.info("[STUB] Enabling user: %s", username)
        user = _USERS.get(username)
        if user:
            user.status = UserStatus.ACTIVE
        audit(AuditAction.ENABLE_USER, performed_by=performed_by, target_username=username)
        return True

    def disable_user(self, username: str, performed_by: str = "system") -> bool:
        """TODO: PATCH .../userAccounts/<id> {status: Inactive}"""
        logger.info("[STUB] Disabling user: %s", username)
        user = _USERS.get(username)
        if user:
            user.status = UserStatus.INACTIVE
        audit(AuditAction.DISABLE_USER, performed_by=performed_by, target_username=username)
        return True

    def delete_user(self, username: str, performed_by: str = "system") -> bool:
        """
        End-dates / terminates a user's access.  Hard-delete is rarely
        supported by Oracle Fusion; this records a termination instead.

        TODO: PATCH .../userAccounts/<id> {endDate: today}
        """
        logger.info("[STUB] Deleting/terminating user: %s", username)
        _USERS.pop(username, None)
        audit(
            AuditAction.DELETE_USER,
            performed_by=performed_by,
            target_username=username,
            description="User access terminated",
        )
        return True

    def get_user(self, username: str) -> Optional[User]:
        """TODO: GET /hcmRestApi/resources/.../userAccounts?q=Username={username}"""
        return _USERS.get(username)

    def search_users(self, query: str) -> list[User]:
        """
        Search by username, name, or email (case-insensitive).

        TODO: GET .../userAccounts?q=Username LIKE '%{query}%'
        """
        q = query.lower()
        return [
            u
            for u in _USERS.values()
            if q in u.username.lower()
            or q in u.full_name.lower()
            or q in u.email.lower()
        ]

    def list_users(self) -> list[User]:
        """TODO: GET .../userAccounts (paginated)"""
        return list(_USERS.values())

    # ------------------------------------------------------------------
    # Bulk upload
    # ------------------------------------------------------------------

    def bulk_upload(
        self,
        records: list[BulkUserRecord],
        performed_by: str = "system",
    ) -> dict:
        """Create multiple users from validated bulk-upload records."""
        created, failed = 0, 0
        for rec in records:
            if not rec.is_valid:
                failed += 1
                continue
            from app.models.user import User  # local import to avoid cycle

            user = User(
                username=rec.username,
                first_name=rec.first_name,
                last_name=rec.last_name,
                email=rec.email,
                department=rec.department,
                job_title=rec.job_title,
                manager_username=rec.manager_username,
            )
            self.create_user(user, performed_by=performed_by)
            created += 1
        audit(
            AuditAction.BULK_UPLOAD,
            performed_by=performed_by,
            description=f"Bulk upload: {created} created, {failed} failed",
            payload={"created": created, "failed": failed},
        )
        return {"created": created, "failed": failed}

    # ------------------------------------------------------------------
    # Comparison
    # ------------------------------------------------------------------

    def compare_users(self, username_a: str, username_b: str) -> dict:
        """
        Return a field-by-field diff between two users.

        TODO: Enhance with live Fusion data.
        """
        user_a = _USERS.get(username_a)
        user_b = _USERS.get(username_b)
        diff: dict = {}
        fields = ["email", "department", "job_title", "status", "manager_username"]
        for f in fields:
            va = getattr(user_a, f, None) if user_a else None
            vb = getattr(user_b, f, None) if user_b else None
            if va != vb:
                diff[f] = {"user_a": va, "user_b": vb}
        return diff


user_service = UserService()
