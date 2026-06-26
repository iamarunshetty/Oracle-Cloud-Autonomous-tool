"""Data-access domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SecurityContext:
    context_name: str
    context_value: str
    description: Optional[str] = None


@dataclass
class DataAccessAssignment:
    username: str
    role_code: str
    security_context: Optional[SecurityContext] = None
    assigned_by: Optional[str] = None
    assigned_at: datetime = field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None


@dataclass
class DataAccessComparison:
    user_a: str
    user_b: str
    only_in_a: list[DataAccessAssignment] = field(default_factory=list)
    only_in_b: list[DataAccessAssignment] = field(default_factory=list)
    common: list[DataAccessAssignment] = field(default_factory=list)
