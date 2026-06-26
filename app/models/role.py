"""Role domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RoleType(str, Enum):
    JOB = "Job Role"
    ABSTRACT = "Abstract Role"
    DATA = "Data Role"
    DUTY = "Duty Role"


class AssignmentStatus(str, Enum):
    ACTIVE = "Active"
    PENDING_APPROVAL = "Pending Approval"
    REJECTED = "Rejected"
    REVOKED = "Revoked"


@dataclass
class Role:
    role_code: str
    role_name: str
    role_type: RoleType = RoleType.JOB
    description: Optional[str] = None
    category: Optional[str] = None
    # None until synced with Oracle Fusion
    fusion_role_id: Optional[str] = None


@dataclass
class RoleAssignment:
    username: str
    role_code: str
    status: AssignmentStatus = AssignmentStatus.ACTIVE
    assigned_by: Optional[str] = None
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    justification: Optional[str] = None
    approval_request_id: Optional[str] = None


@dataclass
class RoleComparisonResult:
    user_a: str
    user_b: str
    only_in_a: list[str] = field(default_factory=list)
    only_in_b: list[str] = field(default_factory=list)
    common: list[str] = field(default_factory=list)
