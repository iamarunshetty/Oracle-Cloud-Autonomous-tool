"""
Update User panel.
"""

from __future__ import annotations

import customtkinter as ctk

from app.api.client import APIError
from app.services.audit_service import AuditService
from app.services.user_service import UserService
from app.ui import widgets as W
from app.utils.validators import validate_email, validate_required, run_all


class UpdateUserFrame(ctk.CTkFrame):
    def __init__(self, parent, user_service: UserService, audit_service: AuditService):
        super().__init__(parent, fg_color="transparent")
        self._user_svc = user_service
        self._audit_svc = audit_service
        self._build()

    def _build(self) -> None:
        W.heading(self, "Update User Profile").grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # --- Lookup row ---
        W.subheading(self, "1. Look up user by ID").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 6))
        W.form_label(self, "User ID *").grid(row=2, column=0, sticky="w", pady=4, padx=(0, 12))
        self._id_entry = W.form_entry(self, placeholder="Oracle Fusion user ID", width=320)
        self._id_entry.grid(row=2, column=1, sticky="ew", pady=4)
        W.secondary_button(self, "Look Up", command=self._lookup).grid(row=3, column=1, sticky="w", pady=(4, 12))

        # --- Edit fields ---
        W.subheading(self, "2. Edit fields to update").grid(row=4, column=0, columnspan=2, sticky="w", pady=(0, 6))

        edit_fields = [
            ("First Name", "first_name"),
            ("Last Name", "last_name"),
            ("Work Email", "email"),
            ("Description", "description"),
        ]
        self._entries: dict[str, ctk.CTkEntry] = {}
        for i, (label_text, key) in enumerate(edit_fields, start=5):
            W.form_label(self, label_text).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 12))
            entry = W.form_entry(self, width=320)
            entry.grid(row=i, column=1, sticky="ew", pady=4)
            self._entries[key] = entry

        self.grid_columnconfigure(1, weight=1)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=10, column=0, columnspan=2, pady=16, sticky="w")
        W.primary_button(btn_row, "Save Changes", command=self._on_save).pack(side="left", padx=(0, 8))
        W.secondary_button(btn_row, "Clear", command=self._clear).pack(side="left")

        self._status = W.status_label(self)
        self._status.grid(row=11, column=0, columnspan=2, sticky="w")

    def _clear(self) -> None:
        self._id_entry.delete(0, "end")
        for entry in self._entries.values():
            entry.delete(0, "end")
        W.set_status(self._status, "")

    def _lookup(self) -> None:
        user_id = self._id_entry.get().strip()
        if not user_id:
            W.set_status(self._status, "Enter a User ID to look up.", "warning")
            return
        try:
            user = self._user_svc.get_user(user_id)
            name = user.get("name", {})
            emails = user.get("emails", [{}])
            self._entries["first_name"].delete(0, "end")
            self._entries["first_name"].insert(0, name.get("givenName", ""))
            self._entries["last_name"].delete(0, "end")
            self._entries["last_name"].insert(0, name.get("familyName", ""))
            self._entries["email"].delete(0, "end")
            email_val = emails[0].get("value", "") if emails else ""
            self._entries["email"].insert(0, email_val)
            self._entries["description"].delete(0, "end")
            self._entries["description"].insert(0, user.get("description", ""))
            W.set_status(self._status, f"Loaded user {user_id}.", "info")
        except APIError as exc:
            W.set_status(self._status, f"✖ {exc}", "error")

    def _on_save(self) -> None:
        user_id = self._id_entry.get().strip()
        ok, errors = run_all(validate_required(user_id, "User ID"))
        if not ok:
            W.set_status(self._status, " | ".join(errors), "error")
            return

        fields: dict = {}
        fn = self._entries["first_name"].get().strip()
        ln = self._entries["last_name"].get().strip()
        email = self._entries["email"].get().strip()
        desc = self._entries["description"].get().strip()

        if fn or ln:
            fields["name"] = {}
            if fn:
                fields["name"]["givenName"] = fn
            if ln:
                fields["name"]["familyName"] = ln
        if email:
            valid, err = validate_email(email)
            if not valid:
                W.set_status(self._status, err, "error")
                return
            fields["emails"] = [{"value": email, "type": "work", "primary": True}]
        if desc:
            fields["description"] = desc

        if not fields:
            W.set_status(self._status, "No fields to update.", "warning")
            return

        try:
            self._user_svc.update_user(user_id, fields)
            self._audit_svc.record("UPDATE_USER", user_id, "success", f"Updated: {list(fields.keys())}")
            W.set_status(self._status, f"✔ User '{user_id}' updated successfully.", "success")
        except APIError as exc:
            self._audit_svc.record("UPDATE_USER", user_id, "error", str(exc))
            W.set_status(self._status, f"✖ {exc}", "error")
