"""
Password Management tab.

Capabilities (UI-wired, backend stubs):
  - Reset password
  - Force password change
  - Unlock user account
  - View login status
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.password_service import password_service


class PasswordManagementTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Username selector
        user_row = QHBoxLayout()
        self._username_edit = QLineEdit()
        self._username_edit.setPlaceholderText("Enter username…")
        user_row.addWidget(QLabel("Username:"))
        user_row.addWidget(self._username_edit)
        layout.addLayout(user_row)

        # Status panel
        self._status_label = QLabel("Login status: –")
        layout.addWidget(self._status_label)

        # Buttons
        btn_row = QHBoxLayout()
        for label, slot in [
            ("Reset Password", self._on_reset),
            ("Force Password Change", self._on_force_change),
            ("Unlock Account", self._on_unlock),
            ("View Login Status", self._on_login_status),
        ]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    # ------------------------------------------------------------------

    def _username(self) -> str:
        return self._username_edit.text().strip()

    def _on_reset(self) -> None:
        username = self._username()
        if not username:
            QMessageBox.information(self, "Input Required", "Please enter a username.")
            return
        password_service.reset_password(username, performed_by="ui_user")
        QMessageBox.information(self, "Password Reset", f"Password reset triggered for '{username}'.")
        self._log(f"Password reset: {username}")

    def _on_force_change(self) -> None:
        username = self._username()
        if not username:
            QMessageBox.information(self, "Input Required", "Please enter a username.")
            return
        password_service.force_change_password(username, performed_by="ui_user")
        QMessageBox.information(self, "Force Change", f"User '{username}' must change password on next login.")
        self._log(f"Force password change: {username}")

    def _on_unlock(self) -> None:
        username = self._username()
        if not username:
            QMessageBox.information(self, "Input Required", "Please enter a username.")
            return
        password_service.unlock_account(username, performed_by="ui_user")
        QMessageBox.information(self, "Account Unlocked", f"Account '{username}' has been unlocked.")
        self._log(f"Account unlocked: {username}")

    def _on_login_status(self) -> None:
        username = self._username()
        if not username:
            QMessageBox.information(self, "Input Required", "Please enter a username.")
            return
        status = password_service.get_login_status(username)
        locked = status.get("locked", False)
        last = status.get("last_login") or "Unknown"
        self._status_label.setText(
            f"Login status for '{username}':  Locked={locked}  |  Last login={last}"
        )
        self._log(f"Login status checked: {username}")
