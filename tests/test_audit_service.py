"""
Tests for the AuditService.
"""

import csv
import os
import tempfile

import pytest

from app.services.audit_service import AuditService, AuditEntry


class TestAuditEntry:
    def test_now_creates_entry(self):
        entry = AuditEntry.now("CREATE_USER", "jdoe", "success", "Created OK.")
        assert entry.action == "CREATE_USER"
        assert entry.target_user == "jdoe"
        assert entry.result == "success"
        assert "UTC" in entry.timestamp

    def test_timestamp_format(self):
        entry = AuditEntry.now("LOCK_USER", "alice", "error", "Failed.")
        parts = entry.timestamp.split(" ")
        assert len(parts) == 3  # date, time, UTC
        assert len(parts[0]) == 10  # YYYY-MM-DD


class TestAuditService:
    def _service(self, tmpdir) -> AuditService:
        return AuditService(os.path.join(str(tmpdir), "audit.csv"))

    def test_record_adds_entry(self, tmp_path):
        svc = AuditService(str(tmp_path / "audit.csv"))
        svc.record("CREATE_USER", "jdoe", "success", "User created.")
        entries = svc.get_entries()
        assert len(entries) == 1
        assert entries[0].action == "CREATE_USER"

    def test_record_persists_to_file(self, tmp_path):
        path = str(tmp_path / "audit.csv")
        svc = AuditService(path)
        svc.record("LOCK_USER", "alice", "error", "Not found.")
        assert os.path.exists(path)
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 1
        assert rows[0]["action"] == "LOCK_USER"

    def test_load_existing_entries(self, tmp_path):
        path = str(tmp_path / "audit.csv")
        svc1 = AuditService(path)
        svc1.record("UPDATE_USER", "bob", "success", "Updated.")

        # Create a second service pointing at the same file
        svc2 = AuditService(path)
        assert len(svc2.get_entries()) == 1
        assert svc2.get_entries()[0].target_user == "bob"

    def test_export_csv(self, tmp_path):
        svc = AuditService(str(tmp_path / "audit.csv"))
        svc.record("ASSIGN_ROLE", "carol", "success", "Role added.")
        svc.record("REMOVE_ROLE", "carol", "success", "Role removed.")

        export_path = str(tmp_path / "export.csv")
        returned = svc.export_csv(export_path)
        assert returned == export_path
        assert os.path.exists(export_path)
        with open(export_path, newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) == 2
        assert rows[0]["action"] == "ASSIGN_ROLE"

    def test_clear_removes_in_memory_entries(self, tmp_path):
        svc = AuditService(str(tmp_path / "audit.csv"))
        svc.record("CREATE_USER", "dave", "success", "Created.")
        svc.clear()
        assert svc.get_entries() == []

    def test_multiple_records_accumulate(self, tmp_path):
        svc = AuditService(str(tmp_path / "audit.csv"))
        for i in range(5):
            svc.record("ACTION", f"user{i}", "success", "ok")
        assert len(svc.get_entries()) == 5
