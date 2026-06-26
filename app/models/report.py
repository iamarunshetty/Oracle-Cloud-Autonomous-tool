"""Report-request / result domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ReportFormat(str, Enum):
    EXCEL = "excel"
    PDF = "pdf"
    CSV = "csv"


class ReportType(str, Enum):
    USER_CREATION = "User Creation Report"
    ROLE_ASSIGNMENT = "Role Assignment Report"
    ACCESS_CHANGE_HISTORY = "Access Change History"
    AUDIT_TRAIL = "Audit Trail"
    INACTIVE_USERS = "Inactive Users"
    ORPHAN_ROLES = "Orphan Role Detection"
    SOD_VIOLATIONS = "SoD Violations"
    ELEVATED_ACCESS = "Elevated Access"
    DUPLICATE_ACCESS = "Duplicate Access"


@dataclass
class ReportRequest:
    report_type: ReportType
    format: ReportFormat = ReportFormat.EXCEL
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    filters: dict[str, Any] = field(default_factory=dict)
    requested_by: str = "system"


@dataclass
class ReportResult:
    request: ReportRequest
    rows: list[dict[str, Any]] = field(default_factory=list)
    output_path: Optional[Path] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None
