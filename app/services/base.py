"""Shared service utilities."""
from __future__ import annotations

import logging
from datetime import datetime

from app.models.audit import AuditAction, AuditEvent
from app.storage.repositories import audit_repo

logger = logging.getLogger(__name__)


def audit(
    action: AuditAction,
    performed_by: str = "system",
    target_username: str | None = None,
    description: str | None = None,
    payload: dict | None = None,
    success: bool = True,
    error_message: str | None = None,
) -> AuditEvent:
    """Create and persist an AuditEvent."""
    event = AuditEvent(
        action=action,
        performed_by=performed_by,
        target_username=target_username,
        description=description,
        payload=payload,
        success=success,
        error_message=error_message,
        timestamp=datetime.utcnow(),
    )
    try:
        audit_repo.write(event)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to write audit event: %s", exc)
    return event
