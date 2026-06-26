"""Tests for the audit trail write path."""
from __future__ import annotations

import pytest

from app.models.audit import AuditAction, AuditEvent
from app.storage.database import Database
from app.storage.repositories import AuditRepository


@pytest.fixture()
def tmp_db(tmp_path):
    """Provide an isolated in-memory-backed database for each test."""
    db_path = tmp_path / "test.db"
    test_db = Database(db_path)
    test_db.connect()
    yield test_db
    test_db.close()


@pytest.fixture()
def audit_repo(tmp_db, monkeypatch):
    """Return an AuditRepository wired to the temporary database."""
    import app.storage.repositories as repo_module
    import app.storage.database as db_module

    # Patch module-level `db` so the repository uses our temp database
    monkeypatch.setattr(db_module, "db", tmp_db)
    monkeypatch.setattr(repo_module, "db", tmp_db)
    return AuditRepository()


class TestAuditRepository:
    def test_write_and_retrieve(self, audit_repo: AuditRepository) -> None:
        event = AuditEvent(
            action=AuditAction.CREATE_USER,
            performed_by="test_user",
            target_username="jdoe",
            description="Test audit",
            success=True,
        )
        row_id = audit_repo.write(event)
        assert row_id > 0
        assert event.id == row_id

    def test_list_returns_written_events(self, audit_repo: AuditRepository) -> None:
        for action in [AuditAction.ENABLE_USER, AuditAction.DISABLE_USER]:
            audit_repo.write(
                AuditEvent(action=action, performed_by="admin", target_username="jdoe")
            )
        rows = audit_repo.list(limit=10)
        assert len(rows) == 2

    def test_filter_by_target_username(self, audit_repo: AuditRepository) -> None:
        audit_repo.write(AuditEvent(action=AuditAction.CREATE_USER, performed_by="admin", target_username="alice"))
        audit_repo.write(AuditEvent(action=AuditAction.CREATE_USER, performed_by="admin", target_username="bob"))
        rows = audit_repo.list(target_username="alice")
        assert len(rows) == 1
        assert rows[0]["target_username"] == "alice"

    def test_filter_by_action(self, audit_repo: AuditRepository) -> None:
        audit_repo.write(AuditEvent(action=AuditAction.ASSIGN_ROLE, performed_by="admin", target_username="alice"))
        audit_repo.write(AuditEvent(action=AuditAction.REMOVE_ROLE, performed_by="admin", target_username="alice"))
        rows = audit_repo.list(action=AuditAction.ASSIGN_ROLE.value)
        assert len(rows) == 1
        assert rows[0]["action"] == AuditAction.ASSIGN_ROLE.value

    def test_failure_event_recorded(self, audit_repo: AuditRepository) -> None:
        event = AuditEvent(
            action=AuditAction.RESET_PASSWORD,
            performed_by="admin",
            target_username="jdoe",
            success=False,
            error_message="Connection timeout",
        )
        audit_repo.write(event)
        rows = audit_repo.list(target_username="jdoe")
        assert rows[0]["success"] == 0
        assert rows[0]["error_message"] == "Connection timeout"

    def test_payload_persisted_as_json(self, audit_repo: AuditRepository) -> None:
        import json

        event = AuditEvent(
            action=AuditAction.BULK_UPLOAD,
            performed_by="admin",
            payload={"created": 5, "failed": 1},
        )
        audit_repo.write(event)
        rows = audit_repo.list(limit=1)
        payload = json.loads(rows[0]["payload"])
        assert payload["created"] == 5
        assert payload["failed"] == 1
