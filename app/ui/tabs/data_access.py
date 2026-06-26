"""
Data Access Management tab.

Capabilities (UI-wired, backend stubs):
  - Assign data access roles
  - Assign security contexts
  - View user data access
  - Compare data access between users
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.data_access import SecurityContext
from app.services.data_access_service import data_access_service


class DataAccessTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        filter_row = QHBoxLayout()
        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText("Enter username…")
        load_btn = QPushButton("Load Data Access")
        load_btn.clicked.connect(self._on_load)
        filter_row.addWidget(QLabel("Username:"))
        filter_row.addWidget(self._username_edit)
        filter_row.addWidget(load_btn)
        layout.addLayout(filter_row)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(
            ["Role Code", "Context Name", "Context Value", "Assigned At"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        for label, slot in [
            ("Assign Data Access", self._on_assign),
            ("Assign Security Context", self._on_assign_context),
            ("Compare Users", self._on_compare),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

    # ------------------------------------------------------------------

    def _on_load(self) -> None:
        username = self._username_edit.text().strip()
        if not username:
            return
        assignments = data_access_service.get_user_data_access(username)
        self._table.setRowCount(len(assignments))
        for row, a in enumerate(assignments):
            self._table.setItem(row, 0, QTableWidgetItem(a.role_code))
            ctx = a.security_context
            self._table.setItem(row, 1, QTableWidgetItem(ctx.context_name if ctx else ""))
            self._table.setItem(row, 2, QTableWidgetItem(ctx.context_value if ctx else ""))
            self._table.setItem(row, 3, QTableWidgetItem(str(a.assigned_at)))
        self._log(f"Loaded {len(assignments)} data-access record(s) for {username}")

    def _on_assign(self) -> None:
        dlg = _AssignDataAccessDialog(parent=self)
        if dlg.exec():
            username, role_code = dlg.username(), dlg.role_code()
            data_access_service.assign_data_access(username, role_code, assigned_by="ui_user")
            self._log(f"Assigned data access '{role_code}' to '{username}'")
            if username == self._username_edit.text().strip():
                self._on_load()

    def _on_assign_context(self) -> None:
        dlg = _AssignContextDialog(parent=self)
        if dlg.exec():
            username, role_code, ctx_name, ctx_value = dlg.values()
            ctx = SecurityContext(context_name=ctx_name, context_value=ctx_value)
            data_access_service.assign_data_access(username, role_code, context=ctx, assigned_by="ui_user")
            self._log(f"Assigned security context '{ctx_name}={ctx_value}' to '{username}'")
            if username == self._username_edit.text().strip():
                self._on_load()

    def _on_compare(self) -> None:
        from app.ui.tabs.role_management import _TwoFieldDialog

        dlg = _TwoFieldDialog("Compare Data Access", "User A", "User B", parent=self)
        if dlg.exec():
            user_a, user_b = dlg.values()
            result = data_access_service.compare_data_access(user_a, user_b)
            msg = (
                f"Only in {user_a}: {len(result.only_in_a)} record(s)\n"
                f"Only in {user_b}: {len(result.only_in_b)} record(s)\n"
                f"Common: {len(result.common)} record(s)"
            )
            QMessageBox.information(self, "Data Access Comparison", msg)
            self._log(f"Compared data access: {user_a} vs {user_b}")


# ---------------------------------------------------------------------------
# Helper dialogs
# ---------------------------------------------------------------------------

class _AssignDataAccessDialog:
    def __init__(self, parent=None) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        self._dlg = QDialog(parent)
        self._dlg.setWindowTitle("Assign Data Access")
        layout = QVBoxLayout(self._dlg)
        form = QFormLayout()
        self._username = QLineEdit()
        self._role_code = QLineEdit()
        form.addRow("Username:", self._username)
        form.addRow("Role Code:", self._role_code)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._dlg.accept)
        buttons.rejected.connect(self._dlg.reject)
        layout.addWidget(buttons)

    def exec(self) -> int:
        return self._dlg.exec()

    def username(self) -> str:
        return self._username.text().strip()

    def role_code(self) -> str:
        return self._role_code.text().strip()


class _AssignContextDialog:
    def __init__(self, parent=None) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        self._dlg = QDialog(parent)
        self._dlg.setWindowTitle("Assign Security Context")
        layout = QVBoxLayout(self._dlg)
        form = QFormLayout()
        self._username = QLineEdit()
        self._role_code = QLineEdit()
        self._ctx_name = QLineEdit()
        self._ctx_value = QLineEdit()
        form.addRow("Username:", self._username)
        form.addRow("Role Code:", self._role_code)
        form.addRow("Context Name:", self._ctx_name)
        form.addRow("Context Value:", self._ctx_value)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._dlg.accept)
        buttons.rejected.connect(self._dlg.reject)
        layout.addWidget(buttons)

    def exec(self) -> int:
        return self._dlg.exec()

    def values(self) -> tuple[str, str, str, str]:
        return (
            self._username.text().strip(),
            self._role_code.text().strip(),
            self._ctx_name.text().strip(),
            self._ctx_value.text().strip(),
        )
