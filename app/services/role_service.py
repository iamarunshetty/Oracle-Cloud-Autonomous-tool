"""
Role service – stub implementation.

TODO: Replace stubs with Oracle Fusion Security REST API calls.
      Endpoint family: /fscmRestApi/resources/11.13.18.05/roles
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from app.models.audit import AuditAction
from app.models.role import AssignmentStatus, Role, RoleAssignment, RoleComparisonResult
from app.services.base import audit

logger = logging.getLogger(__name__)

_ROLES: dict[str, Role] = {}
_ASSIGNMENTS: list[RoleAssignment] = []


class RoleService:
    # ------------------------------------------------------------------
    # Role CRUD (cache)
    # ------------------------------------------------------------------

    def add_role(self, role: Role) -> Role:
        """Cache a role definition. TODO: sync from Fusion."""
        _ROLES[role.role_code] = role
        return role

    def list_roles(self) -> list[Role]:
        """TODO: GET /fscmRestApi/resources/.../roles (paginated)"""
        return list(_ROLES.values())

    def get_role(self, role_code: str) -> Optional[Role]:
        return _ROLES.get(role_code)

    # ------------------------------------------------------------------
    # Assignment
    # ------------------------------------------------------------------

    def assign_role(
        self,
        username: str,
        role_code: str,
        assigned_by: str = "system",
        justification: Optional[str] = None,
    ) -> RoleAssignment:
        """
        Assign a role to a user.

        TODO: POST /fscmRestApi/resources/.../roles/<id>/child/assignedUsers
        """
        assignment = RoleAssignment(
            username=username,
            role_code=role_code,
            status=AssignmentStatus.ACTIVE,
            assigned_by=assigned_by,
            justification=justification,
        )
        _ASSIGNMENTS.append(assignment)
        audit(
            AuditAction.ASSIGN_ROLE,
            performed_by=assigned_by,
            target_username=username,
            description=f"Assigned role {role_code}",
            payload={"role_code": role_code, "justification": justification},
        )
        logger.info("[STUB] Role %s assigned to %s", role_code, username)
        return assignment

    def remove_role(
        self,
        username: str,
        role_code: str,
        performed_by: str = "system",
    ) -> bool:
        """TODO: DELETE /fscmRestApi/resources/.../assignedUsers/<id>"""
        for a in _ASSIGNMENTS:
            if a.username == username and a.role_code == role_code and a.status == AssignmentStatus.ACTIVE:
                a.status = AssignmentStatus.REVOKED
                a.revoked_at = datetime.utcnow()
                audit(
                    AuditAction.REMOVE_ROLE,
                    performed_by=performed_by,
                    target_username=username,
                    description=f"Removed role {role_code}",
                    payload={"role_code": role_code},
                )
                logger.info("[STUB] Role %s removed from %s", role_code, username)
                return True
        return False

    def get_user_roles(self, username: str) -> list[RoleAssignment]:
        return [a for a in _ASSIGNMENTS if a.username == username and a.status == AssignmentStatus.ACTIVE]

    # ------------------------------------------------------------------
    # Compare / Copy
    # ------------------------------------------------------------------

    def compare_roles(self, username_a: str, username_b: str) -> RoleComparisonResult:
        """Return role diff between two users."""
        roles_a = {a.role_code for a in self.get_user_roles(username_a)}
        roles_b = {a.role_code for a in self.get_user_roles(username_b)}
        return RoleComparisonResult(
            user_a=username_a,
            user_b=username_b,
            only_in_a=sorted(roles_a - roles_b),
            only_in_b=sorted(roles_b - roles_a),
            common=sorted(roles_a & roles_b),
        )

    def copy_roles(
        self,
        source_username: str,
        target_username: str,
        performed_by: str = "system",
    ) -> int:
        """Copy all active roles from source to target."""
        roles = self.get_user_roles(source_username)
        copied = 0
        for assignment in roles:
            self.assign_role(
                target_username,
                assignment.role_code,
                assigned_by=performed_by,
                justification=f"Copied from {source_username}",
            )
            copied += 1
        audit(
            AuditAction.COPY_ROLES,
            performed_by=performed_by,
            target_username=target_username,
            description=f"Copied {copied} roles from {source_username}",
            payload={"source": source_username, "count": copied},
        )
        return copied

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def assignment_history(self, username: str) -> list[RoleAssignment]:
        """All (active + revoked) assignments for a user."""
        return [a for a in _ASSIGNMENTS if a.username == username]

    # ------------------------------------------------------------------
    # Approval workflow placeholder
    # ------------------------------------------------------------------

    def request_role_approval(
        self,
        username: str,
        role_code: str,
        requested_by: str,
        justification: str = "",
    ) -> str:
        """
        Initiate a role-approval workflow request.

        TODO: Integrate with Oracle Workflow / Approval Management Engine (AME).
        Returns a placeholder request ID.
        """
        request_id = f"REQ-{username}-{role_code}-PENDING"
        assignment = RoleAssignment(
            username=username,
            role_code=role_code,
            status=AssignmentStatus.PENDING_APPROVAL,
            assigned_by=requested_by,
            justification=justification,
            approval_request_id=request_id,
        )
        _ASSIGNMENTS.append(assignment)
        logger.info("[STUB] Approval request %s submitted", request_id)
        return request_id


role_service = RoleService()
