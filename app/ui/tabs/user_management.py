"""
User Management tab.

Capabilities (UI-wired, backend stubs):
  - Create user
  - Edit user
  - Enable / Disable user
  - Delete / terminate user
  - Search users
  - Bulk upload (Excel)
  - User comparison
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
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
    QVBoxLayout,
    QWidget,
)

from app.models.user import User, UserStatus
from app.services.bulk_upload import parse_bulk_upload
from app.services.user_service import user_service


class UserManagementTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._build_ui()
        self._refresh_table()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)

        # ---- Search bar ----
        search_box = QHBoxLayout()
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText("Search by username, name or email…")
        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self._on_search)
        search_box.addWidget(self._search_edit)
        search_box.addWidget(search_btn)
        main_layout.addLayout(search_box)

        # ---- Users table ----
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Username", "Full Name", "Email", "Status", "Department", "Job Title"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setSelectionBehavior(QTableWidget.SelectRows)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self._table)

        # ---- Action buttons ----
        btn_row = QHBoxLayout()
        for label, slot in [
            ("Create User", self._on_create),
            ("Edit User", self._on_edit),
            ("Enable", self._on_enable),
            ("Disable", self._on_disable),
            ("Delete / Terminate", self._on_delete),
            ("Bulk Upload (Excel)", self._on_bulk_upload),
            ("Compare Users", self._on_compare),
            ("Refresh", self._refresh_table),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        main_layout.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _refresh_table(self, users: list[User] | None = None) -> None:
        if users is None:
            users = user_service.list_users()
        self._table.setRowCount(len(users))
        for row, user in enumerate(users):
            self._table.setItem(row, 0, QTableWidgetItem(user.username))
            self._table.setItem(row, 1, QTableWidgetItem(user.full_name))
            self._table.setItem(row, 2, QTableWidgetItem(user.email))
            self._table.setItem(row, 3, QTableWidgetItem(user.status.value))
            self._table.setItem(row, 4, QTableWidgetItem(user.department or ""))
            self._table.setItem(row, 5, QTableWidgetItem(user.job_title or ""))

    def _selected_username(self) -> str | None:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.text() if item else None

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_search(self) -> None:
        query = self._search_edit.text().strip()
        if not query:
            self._refresh_table()
        else:
            results = user_service.search_users(query)
            self._refresh_table(results)
            self._log(f"Search '{query}' → {len(results)} result(s)")

    def _on_create(self) -> None:
        dlg = _UserFormDialog(parent=self)
        if dlg.exec():
            data = dlg.values()
            user = User(
                username=data["username"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                email=data["email"],
                department=data.get("department"),
                job_title=data.get("job_title"),
            )
            user_service.create_user(user, performed_by="ui_user")
            self._refresh_table()
            self._log(f"Created user: {user.username}")

    def _on_edit(self) -> None:
        username = self._selected_username()
        if not username:
            QMessageBox.information(self, "Select User", "Please select a user to edit.")
            return
        user = user_service.get_user(username)
        if not user:
            return
        dlg = _UserFormDialog(user=user, parent=self)
        if dlg.exec():
            updates = dlg.values()
            user_service.edit_user(username, updates, performed_by="ui_user")
            self._refresh_table()
            self._log(f"Edited user: {username}")

    def _on_enable(self) -> None:
        username = self._selected_username()
        if not username:
            QMessageBox.information(self, "Select User", "Please select a user.")
            return
        user_service.enable_user(username, performed_by="ui_user")
        self._refresh_table()
        self._log(f"Enabled user: {username}")

    def _on_disable(self) -> None:
        username = self._selected_username()
        if not username:
            QMessageBox.information(self, "Select User", "Please select a user.")
            return
        user_service.disable_user(username, performed_by="ui_user")
        self._refresh_table()
        self._log(f"Disabled user: {username}")

    def _on_delete(self) -> None:
        username = self._selected_username()
        if not username:
            QMessageBox.information(self, "Select User", "Please select a user.")
            return
        reply = QMessageBox.question(
            self,
            "Confirm Termination",
            f"Terminate access for '{username}'?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            user_service.delete_user(username, performed_by="ui_user")
            self._refresh_table()
            self._log(f"Terminated user: {username}")

    def _on_bulk_upload(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Bulk Upload File", "", "Excel Files (*.xlsx *.xls)"
        )
        if not path:
            return
        records, file_errors = parse_bulk_upload(path)
        if file_errors:
            QMessageBox.critical(self, "File Error", "\n".join(file_errors))
            return
        valid = [r for r in records if r.is_valid]
        invalid = [r for r in records if not r.is_valid]
        result = user_service.bulk_upload(valid, performed_by="ui_user")
        msg = f"Bulk upload complete.\nCreated: {result['created']}\nFailed: {result['failed'] + len(invalid)}"
        if invalid:
            details = "\n".join(
                f"Row {r.row_index}: {', '.join(r.errors)}" for r in invalid[:10]
            )
            msg += f"\n\nValidation errors (first 10):\n{details}"
        QMessageBox.information(self, "Bulk Upload Result", msg)
        self._refresh_table()
        self._log(f"Bulk upload: {result['created']} created, {result['failed']} failed")

    def _on_compare(self) -> None:
        dlg = _CompareUsersDialog(parent=self)
        if dlg.exec():
            user_a, user_b = dlg.usernames()
            diff = user_service.compare_users(user_a, user_b)
            if not diff:
                QMessageBox.information(self, "Comparison", "No differences found.")
            else:
                lines = [f"Field '{k}': {v['user_a']} → {v['user_b']}" for k, v in diff.items()]
                QMessageBox.information(self, "User Comparison", "\n".join(lines))
            self._log(f"Compared users {user_a} vs {user_b}: {len(diff)} difference(s)")


# ---------------------------------------------------------------------------
# Helper dialogs
# ---------------------------------------------------------------------------

class _UserFormDialog(QWidget):
    """Simple create/edit user form."""

    def __init__(self, user: User | None = None, parent: QWidget | None = None) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        # We need QDialog; rebuild as inner approach
        self._dlg = QDialog(parent)
        self._dlg.setWindowTitle("Create User" if user is None else "Edit User")
        layout = QVBoxLayout(self._dlg)
        form = QFormLayout()

        self._fields: dict[str, QLineEdit] = {}
        field_defs = [
            ("username", "Username *"),
            ("first_name", "First Name *"),
            ("last_name", "Last Name *"),
            ("email", "Email *"),
            ("department", "Department"),
            ("job_title", "Job Title"),
        ]
        for key, label in field_defs:
            edit = QLineEdit()
            if user:
                edit.setText(str(getattr(user, key, "") or ""))
            if user and key == "username":
                edit.setReadOnly(True)
            form.addRow(label, edit)
            self._fields[key] = edit

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._dlg.accept)
        buttons.rejected.connect(self._dlg.reject)
        layout.addWidget(buttons)

    def exec(self) -> int:
        return self._dlg.exec()

    def values(self) -> dict:
        return {k: v.text().strip() for k, v in self._fields.items()}


class _CompareUsersDialog:
    def __init__(self, parent: QWidget | None = None) -> None:
        from PySide6.QtWidgets import QDialog, QDialogButtonBox

        self._dlg = QDialog(parent)
        self._dlg.setWindowTitle("Compare Users")
        layout = QVBoxLayout(self._dlg)
        form = QFormLayout()
        self._a = QLineEdit()
        self._b = QLineEdit()
        form.addRow("User A Username:", self._a)
        form.addRow("User B Username:", self._b)
        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._dlg.accept)
        buttons.rejected.connect(self._dlg.reject)
        layout.addWidget(buttons)

    def exec(self) -> int:
        return self._dlg.exec()

    def usernames(self) -> tuple[str, str]:
        return self._a.text().strip(), self._b.text().strip()
