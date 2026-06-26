"""
Security Analysis tab.

Capabilities (UI-wired, backend stubs):
  - SoD check
  - Elevated access detection
  - Inactive user report
  - Orphan role detection
  - Duplicate access detection
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.services.security_service import security_service


class SecurityAnalysisTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Username for per-user checks
        user_row = QHBoxLayout()
        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText("Enter username for SoD check…")
        sod_btn = QPushButton("Run SoD Check")
        sod_btn.clicked.connect(self._on_sod)
        user_row.addWidget(QLabel("Username:"))
        user_row.addWidget(self._username_edit)
        user_row.addWidget(sod_btn)
        layout.addLayout(user_row)

        # Results table
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Username", "Finding", "Detail", "Severity"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)

        # Bulk analysis buttons
        btn_row = QHBoxLayout()
        for label, slot in [
            ("Elevated Access (All)", self._on_elevated),
            ("Inactive Users (All)", self._on_inactive),
            ("Orphan Roles (All)", self._on_orphan),
            ("Duplicate Access (All)", self._on_duplicate),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _populate(self, rows: list[dict], username_key: str, finding: str, detail_key: str, severity_key: str = "risk") -> None:
        self._table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            self._table.setItem(i, 0, QTableWidgetItem(str(r.get(username_key, ""))))
            self._table.setItem(i, 1, QTableWidgetItem(finding))
            self._table.setItem(i, 2, QTableWidgetItem(str(r.get(detail_key, ""))))
            self._table.setItem(i, 3, QTableWidgetItem(str(r.get(severity_key, ""))))

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_sod(self) -> None:
        username = self._username_edit.text().strip()
        if not username:
            return
        conflicts = security_service.sod_check(username)
        self._table.setRowCount(len(conflicts))
        for i, c in enumerate(conflicts):
            self._table.setItem(i, 0, QTableWidgetItem(c["username"]))
            self._table.setItem(i, 1, QTableWidgetItem("SoD Conflict"))
            self._table.setItem(i, 2, QTableWidgetItem(c["description"]))
            self._table.setItem(i, 3, QTableWidgetItem(c.get("severity", "")))
        self._log(f"SoD check for {username}: {len(conflicts)} conflict(s)")

    def _on_elevated(self) -> None:
        results = security_service.detect_elevated_access()
        self._table.setRowCount(len(results))
        for i, r in enumerate(results):
            self._table.setItem(i, 0, QTableWidgetItem(r["username"]))
            self._table.setItem(i, 1, QTableWidgetItem("Elevated Access"))
            self._table.setItem(i, 2, QTableWidgetItem(", ".join(r["elevated_roles"])))
            self._table.setItem(i, 3, QTableWidgetItem(r.get("risk", "")))
        self._log(f"Elevated access detection: {len(results)} user(s) flagged")

    def _on_inactive(self) -> None:
        results = security_service.inactive_users_report()
        self._table.setRowCount(len(results))
        for i, r in enumerate(results):
            self._table.setItem(i, 0, QTableWidgetItem(r["username"]))
            self._table.setItem(i, 1, QTableWidgetItem("Inactive User"))
            self._table.setItem(i, 2, QTableWidgetItem(f"Last login: {r['last_login']}"))
            self._table.setItem(i, 3, QTableWidgetItem("Medium"))
        self._log(f"Inactive users: {len(results)} found")

    def _on_orphan(self) -> None:
        results = security_service.detect_orphan_roles()
        self._table.setRowCount(len(results))
        for i, r in enumerate(results):
            self._table.setItem(i, 0, QTableWidgetItem(r["username"]))
            self._table.setItem(i, 1, QTableWidgetItem("Orphan Roles"))
            roles_str = ", ".join(r.get("roles", []))
            self._table.setItem(i, 2, QTableWidgetItem(roles_str))
            self._table.setItem(i, 3, QTableWidgetItem("High"))
        self._log(f"Orphan role detection: {len(results)} user(s) found")

    def _on_duplicate(self) -> None:
        results = security_service.detect_duplicate_access()
        self._table.setRowCount(len(results))
        for i, r in enumerate(results):
            self._table.setItem(i, 0, QTableWidgetItem(r["username"]))
            self._table.setItem(i, 1, QTableWidgetItem("Duplicate Access"))
            dupes = ", ".join(f"{rc}×{cnt}" for rc, cnt in r["duplicates"].items())
            self._table.setItem(i, 2, QTableWidgetItem(dupes))
            self._table.setItem(i, 3, QTableWidgetItem("Medium"))
        self._log(f"Duplicate access detection: {len(results)} user(s) found")
