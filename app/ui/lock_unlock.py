"""
Lock / Unlock User panel.
"""

from __future__ import annotations

import customtkinter as ctk

from app.api.client import APIError
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.ui import widgets as W
from app.utils.validators import validate_required


class LockUnlockFrame(ctk.CTkFrame):
    def __init__(self, parent, user_service: UserService, audit_service: AuditService):
        super().__init__(parent, fg_color="transparent")
        self._user_svc = user_service
        self._audit_svc = audit_service
        self._build()

    def _build(self) -> None:
        W.heading(self, "Lock / Unlock User Account").grid(
            row=0, column=0, columnspan=2, pady=(0, 20), sticky="w"
        )

        W.form_label(self, "User ID *").grid(row=1, column=0, sticky="w", pady=4, padx=(0, 12))
        self._id_entry = W.form_entry(self, placeholder="Oracle Fusion user ID", width=320)
        self._id_entry.grid(row=1, column=1, sticky="ew", pady=4)

        self.grid_columnconfigure(1, weight=1)

        # Warning notice
        notice = ctk.CTkLabel(
            self,
            text="⚠  Locking an account will immediately prevent the user from logging in.",
            font=ctk.CTkFont(size=11),
            text_color=W.WARNING_ORANGE,
            wraplength=500,
            justify="left",
        )
        notice.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8, 16))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=3, column=0, columnspan=2, pady=8, sticky="w")
        W.primary_button(btn_row, "🔒  Lock Account", command=self._on_lock).pack(side="left", padx=(0, 8))
        W.secondary_button(btn_row, "🔓  Unlock Account", command=self._on_unlock).pack(side="left")

        self._status = W.status_label(self)
        self._status.grid(row=4, column=0, columnspan=2, sticky="w")

    def _get_user_id(self) -> str | None:
        user_id = self._id_entry.get().strip()
        ok, errors = validate_required(user_id, "User ID")
        if not ok:
            W.set_status(self._status, errors, "error")
            return None
        return user_id

    def _on_lock(self) -> None:
        user_id = self._get_user_id()
        if not user_id:
            return
        if not W.confirm(self, "Confirm Lock", f"Lock account for user '{user_id}'?"):
            return
        try:
            self._user_svc.lock_user(user_id)
            self._audit_svc.record("LOCK_USER", user_id, "success", "Account locked.")
            W.set_status(self._status, f"✔ Account '{user_id}' has been locked.", "success")
        except APIError as exc:
            self._audit_svc.record("LOCK_USER", user_id, "error", str(exc))
            W.set_status(self._status, f"✖ {exc}", "error")

    def _on_unlock(self) -> None:
        user_id = self._get_user_id()
        if not user_id:
            return
        if not W.confirm(self, "Confirm Unlock", f"Unlock account for user '{user_id}'?"):
            return
        try:
            self._user_svc.unlock_user(user_id)
            self._audit_svc.record("UNLOCK_USER", user_id, "success", "Account unlocked.")
            W.set_status(self._status, f"✔ Account '{user_id}' has been unlocked.", "success")
        except APIError as exc:
            self._audit_svc.record("UNLOCK_USER", user_id, "error", str(exc))
            W.set_status(self._status, f"✖ {exc}", "error")
