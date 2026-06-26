"""Tests for bulk upload validation logic."""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.services.bulk_upload import (
    REQUIRED_COLUMNS,
    parse_bulk_upload,
    validate_headers,
)


class TestValidateHeaders:
    def test_all_required_present(self) -> None:
        headers = ["username", "first_name", "last_name", "email"]
        assert validate_headers(headers) == []

    def test_missing_one(self) -> None:
        headers = ["username", "first_name", "last_name"]
        errors = validate_headers(headers)
        assert any("email" in e for e in errors)

    def test_missing_all(self) -> None:
        errors = validate_headers([])
        assert len(errors) == len(REQUIRED_COLUMNS)

    def test_extra_columns_ok(self) -> None:
        headers = ["username", "first_name", "last_name", "email", "department", "custom_col"]
        assert validate_headers(headers) == []

    def test_case_insensitive(self) -> None:
        headers = ["Username", "First_Name", "Last_Name", "Email"]
        assert validate_headers(headers) == []


class TestParseBulkUpload:
    def _make_xlsx(self, rows: list[list], path: Path) -> None:
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        for row in rows:
            ws.append(row)
        wb.save(str(path))

    def test_valid_file(self, tmp_path: Path) -> None:
        f = tmp_path / "upload.xlsx"
        self._make_xlsx(
            [
                ["username", "first_name", "last_name", "email"],
                ["jdoe", "John", "Doe", "jdoe@example.com"],
                ["asmith", "Alice", "Smith", "asmith@example.com"],
            ],
            f,
        )
        records, errors = parse_bulk_upload(f)
        assert errors == []
        assert len(records) == 2
        assert all(r.is_valid for r in records)

    def test_invalid_email(self, tmp_path: Path) -> None:
        f = tmp_path / "upload.xlsx"
        self._make_xlsx(
            [
                ["username", "first_name", "last_name", "email"],
                ["jdoe", "John", "Doe", "not-an-email"],
            ],
            f,
        )
        records, errors = parse_bulk_upload(f)
        assert errors == []
        assert len(records) == 1
        assert not records[0].is_valid
        assert any("email" in e for e in records[0].errors)

    def test_missing_username(self, tmp_path: Path) -> None:
        f = tmp_path / "upload.xlsx"
        self._make_xlsx(
            [
                ["username", "first_name", "last_name", "email"],
                ["", "John", "Doe", "jdoe@example.com"],
            ],
            f,
        )
        records, errors = parse_bulk_upload(f)
        assert errors == []
        assert not records[0].is_valid
        assert any("username" in e for e in records[0].errors)

    def test_missing_required_column(self, tmp_path: Path) -> None:
        f = tmp_path / "upload.xlsx"
        self._make_xlsx(
            [
                ["username", "first_name", "last_name"],  # missing email
                ["jdoe", "John", "Doe"],
            ],
            f,
        )
        records, errors = parse_bulk_upload(f)
        assert records == []
        assert any("email" in e for e in errors)

    def test_file_not_found(self) -> None:
        records, errors = parse_bulk_upload("/nonexistent/path/file.xlsx")
        assert records == []
        assert errors

    def test_optional_columns(self, tmp_path: Path) -> None:
        f = tmp_path / "upload.xlsx"
        self._make_xlsx(
            [
                ["username", "first_name", "last_name", "email", "department"],
                ["jdoe", "John", "Doe", "jdoe@example.com", "Finance"],
            ],
            f,
        )
        records, errors = parse_bulk_upload(f)
        assert errors == []
        assert records[0].department == "Finance"
