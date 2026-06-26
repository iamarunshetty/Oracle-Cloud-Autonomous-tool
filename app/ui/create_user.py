"""
Create User panel.
"""

from __future__ import annotations

import customtkinter as ctk

from app.api.client import APIError
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.ui import widgets as W
from app.utils.validators import validate_email, validate_required, validate_username, run_all


class CreateUserFrame(ctk.CTkFrame):
    def __init__(self, parent, user_service: UserService, audit_service: AuditService):
        super().__init__(parent, fg_color="transparent")
        self._user_svc = user_service
        self._audit_svc = audit_service
        self._build()

    def _build(self) -> None:
        W.heading(self, "Create User").grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        fields = [
            ("Username *", "username"),
            ("First Name *", "first_name"),
            ("Last Name *", "last_name"),
            ("Work Email *", "email"),
            ("Description", "description"),
        ]
        self._entries: dict[str, ctk.CTkEntry] = {}

        for i, (label_text, key) in enumerate(fields, start=1):
            W.form_label(self, label_text).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 12))
            entry = W.form_entry(self, width=320)
            entry.grid(row=i, column=1, sticky="ew", pady=4)
            self._entries[key] = entry

        self.grid_columnconfigure(1, weight=1)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=len(fields) + 1, column=0, columnspan=2, pady=16, sticky="w")
        W.primary_button(btn_row, "Create User", command=self._on_create).pack(side="left", padx=(0, 8))
        W.secondary_button(btn_row, "Clear", command=self._clear).pack(side="left")

        self._status = W.status_label(self)
        self._status.grid(row=len(fields) + 2, column=0, columnspan=2, sticky="w")

    def _clear(self) -> None:
        for entry in self._entries.values():
            entry.delete(0, "end")
        W.set_status(self._status, "")

    def _on_create(self) -> None:
        vals = {k: e.get().strip() for k, e in self._entries.items()}

        ok, errors = run_all(
            validate_username(vals["username"]),
            validate_required(vals["first_name"], "First Name"),
            validate_required(vals["last_name"], "Last Name"),
            validate_email(vals["email"]),
        )
        if not ok:
            W.set_status(self._status, " | ".join(errors), "error")
            return

        try:
            self._user_svc.create_user(
                username=vals["username"],
                first_name=vals["first_name"],
                last_name=vals["last_name"],
                email=vals["email"],
                description=vals["description"],
            )
            self._audit_svc.record("CREATE_USER", vals["username"], "success", "User created.")
            W.set_status(self._status, f"✔ User '{vals['username']}' created successfully.", "success")
            self._clear()
        except APIError as exc:
            self._audit_svc.record("CREATE_USER", vals["username"], "error", str(exc))
            W.set_status(self._status, f"✖ {exc}", "error")
