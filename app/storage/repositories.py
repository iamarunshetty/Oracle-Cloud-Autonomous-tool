"""Repository classes for database access."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Optional

from app.models.audit import AuditAction, AuditEvent
from app.storage.database import db

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


class AuditRepository:
    """Persist and retrieve AuditEvent records."""

    def write(self, event: AuditEvent) -> int:
        """Insert an audit event and return its new row id."""
        payload_str = json.dumps(event.payload) if event.payload else None
        cursor = db.conn.execute(
            """
            INSERT INTO audit_events
                (action, performed_by, target_username, description,
                 payload, success, error_message, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event.action.value if isinstance(event.action, AuditAction) else event.action,
                event.performed_by,
                event.target_username,
                event.description,
                payload_str,
                1 if event.success else 0,
                event.error_message,
                event.timestamp.isoformat(timespec="seconds") + "Z",
            ),
        )
        db.conn.commit()
        event.id = cursor.lastrowid
        logger.debug("Audit event written: id=%s action=%s", event.id, event.action)
        return cursor.lastrowid  # type: ignore[return-value]

    def list(
        self,
        limit: int = 200,
        offset: int = 0,
        target_username: Optional[str] = None,
        action: Optional[str] = None,
    ) -> list[dict]:
        query = "SELECT * FROM audit_events WHERE 1=1"
        params: list = []
        if target_username:
            query += " AND target_username = ?"
            params.append(target_username)
        if action:
            query += " AND action = ?"
            params.append(action)
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        rows = db.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]


class OperationHistoryRepository:
    """Record long-running operation progress."""

    def start(self, operation_type: str, initiated_by: str, details: Optional[dict] = None) -> int:
        cursor = db.conn.execute(
            """
            INSERT INTO operation_history
                (operation_type, initiated_by, status, details, started_at)
            VALUES (?, ?, 'running', ?, ?)
            """,
            (operation_type, initiated_by, json.dumps(details) if details else None, _now_iso()),
        )
        db.conn.commit()
        return cursor.lastrowid  # type: ignore[return-value]

    def finish(
        self, operation_id: int, success: bool, error_message: Optional[str] = None
    ) -> None:
        status = "completed" if success else "failed"
        db.conn.execute(
            """
            UPDATE operation_history
            SET status=?, finished_at=?, error_message=?
            WHERE id=?
            """,
            (status, _now_iso(), error_message, operation_id),
        )
        db.conn.commit()

    def list(self, limit: int = 100) -> list[dict]:
        rows = db.conn.execute(
            "SELECT * FROM operation_history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


audit_repo = AuditRepository()
op_history_repo = OperationHistoryRepository()
