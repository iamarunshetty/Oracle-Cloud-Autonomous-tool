"""Audit-event domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class AuditAction(str, Enum):
    CREATE_USER = "CREATE_USER"
    EDIT_USER = "EDIT_USER"
    ENABLE_USER = "ENABLE_USER"
    DISABLE_USER = "DISABLE_USER"
    DELETE_USER = "DELETE_USER"
    ASSIGN_ROLE = "ASSIGN_ROLE"
    REMOVE_ROLE = "REMOVE_ROLE"
    COPY_ROLES = "COPY_ROLES"
    ASSIGN_DATA_ACCESS = "ASSIGN_DATA_ACCESS"
    RESET_PASSWORD = "RESET_PASSWORD"
    FORCE_CHANGE_PASSWORD = "FORCE_CHANGE_PASSWORD"
    UNLOCK_ACCOUNT = "UNLOCK_ACCOUNT"
    BULK_UPLOAD = "BULK_UPLOAD"
    EXPORT_REPORT = "EXPORT_REPORT"
    SOD_CHECK = "SOD_CHECK"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    OTHER = "OTHER"


@dataclass
class AuditEvent:
    action: AuditAction
    performed_by: str
    target_username: Optional[str] = None
    description: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None  # set after DB insert
