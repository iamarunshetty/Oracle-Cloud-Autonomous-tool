"""User domain models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class UserStatus(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"
    PENDING = "Pending"


@dataclass
class User:
    username: str
    first_name: str
    last_name: str
    email: str
    status: UserStatus = UserStatus.ACTIVE
    person_number: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    manager_username: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_login: Optional[datetime] = None
    # Internal id assigned by Oracle Fusion; None until synced
    fusion_person_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE


@dataclass
class BulkUserRecord:
    """A single row from a bulk-upload spreadsheet."""

    row_index: int
    username: str
    first_name: str
    last_name: str
    email: str
    department: Optional[str] = None
    job_title: Optional[str] = None
    manager_username: Optional[str] = None
    errors: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0
