"""
Role Management tab.

Capabilities (UI-wired, backend stubs):
  - Assign / Remove roles
  - Compare user roles
  - Copy roles from User A to User B
  - Request role approval (workflow stub)
  - View role assignment history
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.services.role_service import role_service


class RoleManagementTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # ---- User filter ----
        filter_row = QHBoxLayout()
        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText("Enter username to view roles…")
        load_btn = QPushButton("Load Roles")
        load_btn.clicked.connect(self._on_load)
        filter_row.addWidget(QLabel("Username:"))
        filter_row.addWidget(self._username_edit)
        filter_row.addWidget(load_btn)
        layout.addLayout(filter_row)

        # ---- Assignments table ----
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["Role Code", "Status", "Assigned By", "Assigned At", "Justification"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self._table)

        # ---- Actions ----
        btn_row = QHBoxLayout()
        for label, slot in [
            ("Assign Role", self._on_assign),
            ("Remove Role", self._on_remove),
            ("Compare Users", self._on_compare),
            ("Copy Roles A→B", self._on_copy),
            ("Request Approval", self._on_request_approval),
            ("Assignment History", self._on_history),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_load(self) -> None:
        username = self._username_edit.text().strip()
        if not username:
            return
        assignments = role_service.get_user_roles(username)
        self._table.setRowCount(len(assignments))
        for row, a in enumerate(assignments):
            self._table.setItem(row, 0, QTableWidgetItem(a.role_code))
            self._table.setItem(row, 1, QTableWidgetItem(a.status.value))
            self._table.setItem(row, 2, QTableWidgetItem(a.assigned_by or ""))
            self._table.setItem(row, 3, QTableWidgetItem(str(a.assigned_at)))
            self._table.setItem(row, 4, QTableWidgetItem(a.justification or ""))
        self._log(f"Loaded {len(assignments)} role(s) for {username}")

    def _on_assign(self) -> None:
        dlg = _TwoFieldDialog("Assign Role", "Username", "Role Code", parent=self)
        if dlg.exec():
            username, role_code = dlg.values()
            role_service.assign_role(username, role_code, assigned_by="ui_user")
            self._log(f"Assigned role '{role_code}' to '{username}'")
            if username == self._username_edit.text().strip():
                self._on_load()

    def _on_remove(self) -> None:
        dlg = _TwoFieldDialog("Remove Role", "Username", "Role Code", parent=self)
        if dlg.exec():
            username, role_code = dlg.values()
            ok = role_service.remove_role(username, role_code, performed_by="ui_user")
            self._log(
                f"Removed role '{role_code}' from '{username}'"
                if ok
                else f"Role '{role_code}' not found for '{username}'"
            )
            if username == self._username_edit.text().strip():
                self._on_load()

    def _on_compare(self) -> None:
        dlg = _TwoFieldDialog("Compare Roles", "User A", "User B", parent=self)
        if dlg.exec():
            user_a, user_b = dlg.values()
            result = role_service.compare_roles(user_a, user_b)
            msg = (
                f"Only in {user_a}: {', '.join(result.only_in_a) or 'none'}\n"
                f"Only in {user_b}: {', '.join(result.only_in_b) or 'none'}\n"
                f"Common: {', '.join(result.common) or 'none'}"
            )
            QMessageBox.information(self, "Role Comparison", msg)
            self._log(f"Compared roles: {user_a} vs {user_b}")

    def _on_copy(self) -> None:
        dlg = _TwoFieldDialog("Copy Roles", "Source Username", "Target Username", parent=self)
        if dlg.exec():
            source, target = dlg.values()
            count = role_service.copy_roles(source, target, performed_by="ui_user")
            QMessageBox.information(self, "Copy Roles", f"Copied {count} role(s) from {source} to {target}.")
            self._log(f"Copied {count} roles from '{source}' to '{target}'")

    def _on_request_approval(self) -> None:
        dlg = _TwoFieldDialog("Request Role Approval", "Username", "Role Code", parent=self)
        if dlg.exec():
            username, role_code = dlg.values()
            req_id = role_service.request_role_approval(
                username, role_code, requested_by="ui_user", justification="Requested via UI"
            )
            QMessageBox.information(self, "Approval Requested", f"Request ID: {req_id}")
            self._log(f"Approval request submitted: {req_id}")

    def _on_history(self) -> None:
        username = self._username_edit.text().strip()
        if not username:
            QMessageBox.information(self, "History", "Enter a username first.")
            return
        history = role_service.assignment_history(username)
        if not history:
            QMessageBox.information(self, "History", "No assignment history found.")
            return
        lines = [f"{a.role_code} | {a.status.value} | {a.assigned_at}" for a in history]
        dlg = _InfoDialog(f"Assignment History – {username}", "\n".join(lines), parent=self)
        dlg.exec()
        self._log(f"Viewed history for {username}: {len(history)} record(s)")


# ---------------------------------------------------------------------------
# Helper dialogs
# ---------------------------------------------------------------------------

class _TwoFieldDialog:
    def __init__(self, title: str, label_a: str, label_b: str, parent=None) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        self._dlg = QDialog(parent)
        self._dlg.setWindowTitle(title)
        layout = QVBoxLayout(self._dlg)
        form = QFormLayout()
        self._a = QLineEdit()
        self._b = QLineEdit()
        form.addRow(label_a + ":", self._a)
        form.addRow(label_b + ":", self._b)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._dlg.accept)
        buttons.rejected.connect(self._dlg.reject)
        layout.addWidget(buttons)

    def exec(self) -> int:
        return self._dlg.exec()

    def values(self) -> tuple[str, str]:
        return self._a.text().strip(), self._b.text().strip()


class _InfoDialog:
    def __init__(self, title: str, text: str, parent=None) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        self._dlg = QDialog(parent)
        self._dlg.setWindowTitle(title)
        self._dlg.resize(600, 400)
        layout = QVBoxLayout(self._dlg)
        te = QTextEdit()
        te.setReadOnly(True)
        te.setPlainText(text)
        layout.addWidget(te)
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self._dlg.reject)
        layout.addWidget(buttons)

    def exec(self) -> int:
        return self._dlg.exec()
