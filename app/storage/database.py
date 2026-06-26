"""SQLite database initialisation and connection management."""
from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

_DDL = """
CREATE TABLE IF NOT EXISTS audit_events (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    action          TEXT    NOT NULL,
    performed_by    TEXT    NOT NULL,
    target_username TEXT,
    description     TEXT,
    payload         TEXT,   -- JSON-encoded dict
    success         INTEGER NOT NULL DEFAULT 1,
    error_message   TEXT,
    timestamp       TEXT    NOT NULL  -- ISO-8601 UTC
);

CREATE TABLE IF NOT EXISTS operation_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type  TEXT    NOT NULL,
    initiated_by    TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'pending',
    details         TEXT,   -- JSON-encoded details
    started_at      TEXT    NOT NULL,
    finished_at     TEXT,
    error_message   TEXT
);

CREATE TABLE IF NOT EXISTS user_cache (
    username        TEXT    PRIMARY KEY,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    email           TEXT    NOT NULL,
    status          TEXT    NOT NULL DEFAULT 'Active',
    department      TEXT,
    job_title       TEXT,
    fusion_person_id TEXT,
    synced_at       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS role_cache (
    role_code       TEXT    PRIMARY KEY,
    role_name       TEXT    NOT NULL,
    role_type       TEXT    NOT NULL DEFAULT 'Job Role',
    description     TEXT,
    category        TEXT,
    fusion_role_id  TEXT,
    synced_at       TEXT    NOT NULL
);
"""


class Database:
    """Thin wrapper around a SQLite connection."""

    def __init__(self, db_path: str | Path = "fusion_tool.db") -> None:
        self._path = Path(db_path)
        self._conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._apply_schema()
        logger.info("Database connected: %s", self._path)

    def _apply_schema(self) -> None:
        assert self._conn is not None
        self._conn.executescript(_DDL)
        self._conn.commit()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise RuntimeError("Database.connect() has not been called.")
        return self._conn

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "Database":
        self.connect()
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# Module-level singleton – call db.connect() once at startup
db = Database()
