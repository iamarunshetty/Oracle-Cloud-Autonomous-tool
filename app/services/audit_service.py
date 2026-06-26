"""
Audit service – records app operations and exports them to CSV.
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from app.utils.logger import get_logger

logger = get_logger("oracle_fusion_tool.services.audit")

@dataclass
class AuditEntry:
    timestamp: str
    action: str
    target_user: str
    result: str          # "success" | "error"
    message: str

    @classmethod
    def now(cls, action: str, target_user: str, result: str, message: str) -> "AuditEntry":
        return cls(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            action=action,
            target_user=target_user,
            result=result,
            message=message,
        )

class AuditService:
    """In-memory audit log with CSV persistence and export."""

    _FIELDNAMES = ["timestamp", "action", "target_user", "result", "message"]

    def __init__(self, audit_file: str = "audit_log.csv") -> None:
        self._audit_file = Path(audit_file)
        self._entries: list[AuditEntry] = []
        self._load_existing()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def record(self, action: str, target_user: str, result: str, message: str) -> AuditEntry:
        """Record an action and persist it to the audit CSV."""
        entry = AuditEntry.now(action, target_user, result, message)
        self._entries.append(entry)
        self._append_to_file(entry)
        logger.info("AUDIT %s | %s | %s | %s", action, target_user, result, message)
        return entry

    def get_entries(self) -> list[AuditEntry]:
        return list(self._entries)

    def export_csv(self, export_path: str) -> str:
        """Export current audit entries to a given file path. Returns the path."""
        path = Path(export_path)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self._FIELDNAMES)
            writer.writeheader()
            writer.writerows(asdict(e) for e in self._entries)
        logger.info("Audit exported to %s (%d entries).", path, len(self._entries))
        return str(path)

    def clear(self) -> None:
        """Clear in-memory entries (does not delete the persisted file)."""
        self._entries.clear()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _append_to_file(self, entry: AuditEntry) -> None:
        write_header = not self._audit_file.exists() or self._audit_file.stat().st_size == 0
        try:
            with open(self._audit_file, "a", newline="", encoding="utf-8") as fh:
                writer = csv.DictWriter(fh, fieldnames=self._FIELDNAMES)
                if write_header:
                    writer.writeheader()
                writer.writerow(asdict(entry))
        except OSError as exc:
            logger.warning("Could not write audit entry to file: %s", exc)

    def _load_existing(self) -> None:
        if not self._audit_file.exists():
            return
        try:
            with open(self._audit_file, "r", encoding="utf-8") as fh:
                reader = csv.DictReader(fh)
                for row in reader:
                    self._entries.append(
                        AuditEntry(
                            timestamp=row.get("timestamp", ""),
                            action=row.get("action", ""),
                            target_user=row.get("target_user", ""),
                            result=row.get("result", ""),
                            message=row.get("message", ""),
                        )
                    )
        except (OSError, csv.Error) as exc:
            logger.warning("Could not load existing audit log: %s", exc)
