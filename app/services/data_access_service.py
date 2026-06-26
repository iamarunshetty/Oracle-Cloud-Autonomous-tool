"""
Data-access service – stub implementation.

TODO: Replace with Oracle Fusion Data Security REST calls.
"""
from __future__ import annotations

import logging

from app.models.audit import AuditAction
from app.models.data_access import DataAccessAssignment, DataAccessComparison, SecurityContext
from app.services.base import audit

logger = logging.getLogger(__name__)

_ASSIGNMENTS: list[DataAccessAssignment] = []


class DataAccessService:
    def assign_data_access(
        self,
        username: str,
        role_code: str,
        context: SecurityContext | None = None,
        assigned_by: str = "system",
    ) -> DataAccessAssignment:
        """
        Assign a data-access role with optional security context.

        TODO: POST /fscmRestApi/resources/.../dataSecurityPolicies
        """
        assignment = DataAccessAssignment(
            username=username,
            role_code=role_code,
            security_context=context,
            assigned_by=assigned_by,
        )
        _ASSIGNMENTS.append(assignment)
        audit(
            AuditAction.ASSIGN_DATA_ACCESS,
            performed_by=assigned_by,
            target_username=username,
            description=f"Assigned data access role {role_code}",
            payload={
                "role_code": role_code,
                "context": context.context_name if context else None,
            },
        )
        logger.info("[STUB] Data access %s assigned to %s", role_code, username)
        return assignment

    def get_user_data_access(self, username: str) -> list[DataAccessAssignment]:
        """TODO: GET .../dataSecurityPolicies?q=Username={username}"""
        return [a for a in _ASSIGNMENTS if a.username == username and a.revoked_at is None]

    def compare_data_access(self, username_a: str, username_b: str) -> DataAccessComparison:
        a_assignments = self.get_user_data_access(username_a)
        b_assignments = self.get_user_data_access(username_b)
        a_keys = {a.role_code for a in a_assignments}
        b_keys = {a.role_code for a in b_assignments}
        return DataAccessComparison(
            user_a=username_a,
            user_b=username_b,
            only_in_a=[a for a in a_assignments if a.role_code not in b_keys],
            only_in_b=[a for a in b_assignments if a.role_code not in a_keys],
            common=[a for a in a_assignments if a.role_code in b_keys],
        )


data_access_service = DataAccessService()
