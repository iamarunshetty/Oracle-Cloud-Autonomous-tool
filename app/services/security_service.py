"""
Security-analysis service – stub implementation.

TODO: Implement actual SoD rule engine, pull live data from Fusion.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Optional

from app.models.audit import AuditAction
from app.services.base import audit
from app.services.role_service import role_service
from app.services.user_service import user_service

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Stub SoD rule set – replace with a configurable policy file or DB table.
# ---------------------------------------------------------------------------
_SOD_RULES: list[tuple[str, str]] = [
    # (role_a, role_b) – having both is a conflict
    ("AP_INVOICES_ENTRY", "AP_PAYMENT_APPROVAL"),
    ("AR_BILLING_ENTRY", "AR_RECEIPT_ENTRY"),
    ("GL_JOURNAL_ENTRY", "GL_JOURNAL_APPROVAL"),
]


class SecurityAnalysisService:
    def sod_check(self, username: str) -> list[dict]:
        """
        Return SoD conflicts for a user.

        TODO: Integrate with Oracle Access Governance (OAG) or custom rule engine.
        """
        assignments = role_service.get_user_roles(username)
        user_roles = {a.role_code for a in assignments}
        conflicts = []
        for role_a, role_b in _SOD_RULES:
            if role_a in user_roles and role_b in user_roles:
                conflicts.append(
                    {
                        "username": username,
                        "role_a": role_a,
                        "role_b": role_b,
                        "severity": "High",
                        "description": f"SoD conflict: {role_a} + {role_b}",
                    }
                )
        audit(
            AuditAction.SOD_CHECK,
            performed_by="system",
            target_username=username,
            description=f"SoD check found {len(conflicts)} conflict(s)",
            payload={"conflicts": len(conflicts)},
        )
        return conflicts

    def detect_elevated_access(self) -> list[dict]:
        """
        Identify users with elevated/privileged roles.

        TODO: Define 'elevated' roles in a configurable policy.
        """
        elevated_roles = {"IT_SECURITY_MANAGER", "SUPER_USER", "APPLICATION_ADMIN"}
        result = []
        for user in user_service.list_users():
            user_roles = {a.role_code for a in role_service.get_user_roles(user.username)}
            flagged = user_roles & elevated_roles
            if flagged:
                result.append(
                    {
                        "username": user.username,
                        "elevated_roles": sorted(flagged),
                        "risk": "High",
                    }
                )
        return result

    def inactive_users_report(self, inactive_days: int = 90) -> list[dict]:
        """
        Return users who have not logged in for *inactive_days* days.

        TODO: Pull last-login from Fusion HCM.
        """
        threshold = datetime.utcnow() - timedelta(days=inactive_days)
        result = []
        for user in user_service.list_users():
            if user.last_login is None or user.last_login < threshold:
                result.append(
                    {
                        "username": user.username,
                        "last_login": str(user.last_login) if user.last_login else "Never",
                        "status": user.status.value,
                    }
                )
        return result

    def detect_orphan_roles(self) -> list[dict]:
        """
        Find role assignments whose owning user is disabled/inactive.

        TODO: Cross-reference with live Fusion user status.
        """
        from app.models.user import UserStatus

        result = []
        for user in user_service.list_users():
            if user.status != UserStatus.ACTIVE:
                active_roles = role_service.get_user_roles(user.username)
                if active_roles:
                    result.append(
                        {
                            "username": user.username,
                            "status": user.status.value,
                            "orphan_role_count": len(active_roles),
                            "roles": [a.role_code for a in active_roles],
                        }
                    )
        return result

    def detect_duplicate_access(self) -> list[dict]:
        """
        Identify users who have duplicate/overlapping role assignments.

        TODO: Expand with data-access overlap analysis.
        """
        from collections import Counter

        result = []
        for user in user_service.list_users():
            assignments = role_service.get_user_roles(user.username)
            counts = Counter(a.role_code for a in assignments)
            duplicates = {rc: cnt for rc, cnt in counts.items() if cnt > 1}
            if duplicates:
                result.append({"username": user.username, "duplicates": duplicates})
        return result


security_service = SecurityAnalysisService()
