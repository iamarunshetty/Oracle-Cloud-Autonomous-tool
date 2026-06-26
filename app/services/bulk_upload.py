"""
Bulk-upload Excel parser and validator.

Required columns (case-insensitive):
    username, first_name, last_name, email

Optional columns:
    department, job_title, manager_username
"""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from app.models.user import BulkUserRecord

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = {"username", "first_name", "last_name", "email"}
OPTIONAL_COLUMNS = {"department", "job_title", "manager_username"}
ALL_COLUMNS = REQUIRED_COLUMNS | OPTIONAL_COLUMNS

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _normalise_headers(headers: list[str]) -> dict[str, int]:
    """Return {normalised_header: column_index} mapping."""
    return {h.strip().lower().replace(" ", "_"): i for i, h in enumerate(headers)}


def validate_headers(headers: list[str]) -> list[str]:
    """Return a list of error messages for missing required columns."""
    normalised = set(_normalise_headers(headers).keys())
    missing = REQUIRED_COLUMNS - normalised
    return [f"Missing required column: '{col}'" for col in sorted(missing)]


def parse_bulk_upload(file_path: str | Path) -> tuple[list[BulkUserRecord], list[str]]:
    """
    Parse an Excel bulk-upload file.

    Returns:
        (records, file_errors) where file_errors are errors that prevent
        any record from being processed (e.g. missing required columns).
    """
    try:
        import openpyxl
    except ImportError:
        return [], ["openpyxl is not installed. Run: pip install openpyxl"]

    path = Path(file_path)
    if not path.exists():
        return [], [f"File not found: {path}"]

    try:
        wb = openpyxl.load_workbook(str(path), read_only=True, data_only=True)
    except Exception as exc:  # noqa: BLE001
        return [], [f"Could not open file: {exc}"]

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows:
        return [], ["The spreadsheet is empty."]

    # First row is the header
    header_row = [str(c) if c is not None else "" for c in rows[0]]
    header_errors = validate_headers(header_row)
    if header_errors:
        return [], header_errors

    col_map = _normalise_headers(header_row)
    records: list[BulkUserRecord] = []

    def _get(row: tuple, col: str) -> Any:
        idx = col_map.get(col)
        if idx is None:
            return None
        v = row[idx]
        return str(v).strip() if v is not None else None

    for row_idx, row in enumerate(rows[1:], start=2):  # 1-indexed, skip header
        username = _get(row, "username") or ""
        first_name = _get(row, "first_name") or ""
        last_name = _get(row, "last_name") or ""
        email = _get(row, "email") or ""

        rec = BulkUserRecord(
            row_index=row_idx,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            department=_get(row, "department"),
            job_title=_get(row, "job_title"),
            manager_username=_get(row, "manager_username"),
        )

        # Row-level validation
        if not username:
            rec.errors.append("username is required")
        if not first_name:
            rec.errors.append("first_name is required")
        if not last_name:
            rec.errors.append("last_name is required")
        if not email:
            rec.errors.append("email is required")
        elif not _EMAIL_RE.match(email):
            rec.errors.append(f"email '{email}' is not valid")

        records.append(rec)

    logger.info(
        "Bulk upload parsed: %d rows, %d valid, %d invalid",
        len(records),
        sum(1 for r in records if r.is_valid),
        sum(1 for r in records if not r.is_valid),
    )
    return records, []
