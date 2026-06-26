"""
Role Management panel (assign / remove roles from a user).
"""

from __future__ import annotations

import customtkinter as ctk

from app.api.client import APIError
from app.services.audit_service import AuditService
from app.services.role_service import RoleService
from app.services.sod_service import SodService
from app.ui import widgets as W
from app.utils.validators import validate_required


class RoleManagementFrame(ctk.CTkFrame):
    def __init__(self, parent, role_service: RoleService, audit_service: AuditService):
        super().__init__(parent, fg_color="transparent")
        self._role_svc = role_service
        self._audit_svc = audit_service
        self._sod_svc = SodService()
        self._current_roles: list[dict] = []
        self._build()

    def _build(self) -> None:
        W.heading(self, "Role Management").grid(row=0, column=0, columnspan=3, pady=(0, 20), sticky="w")

        # -- User lookup row --
        W.form_label(self, "Username *").grid(row=1, column=0, sticky="w", pady=4, padx=(0, 12))
        self._username_entry = W.form_entry(self, placeholder="Oracle Fusion username", width=260)
        self._username_entry.grid(row=1, column=1, sticky="ew", pady=4)
        W.secondary_button(self, "Load Roles", command=self._load_user_roles).grid(
            row=1, column=2, padx=(8, 0), pady=4
        )

        self.grid_columnconfigure(1, weight=1)

        # -- Assign role row --
        W.subheading(self, "Assign role").grid(row=2, column=0, columnspan=3, sticky="w", pady=(16, 4))
        W.form_label(self, "Role Name *").grid(row=3, column=0, sticky="w", pady=4, padx=(0, 12))
        self._role_entry = W.form_entry(self, placeholder="e.g. ORA_PER_EMPLOYEE_ABSTRACT", width=260)
        self._role_entry.grid(row=3, column=1, sticky="ew", pady=4)
        W.primary_button(self, "Assign", command=self._on_assign).grid(row=3, column=2, padx=(8, 0), pady=4)

        # -- Current roles list --
        W.subheading(self, "Current roles").grid(row=4, column=0, columnspan=3, sticky="w", pady=(16, 4))

        self._roles_frame = ctk.CTkScrollableFrame(self, height=160)
        self._roles_frame.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=(0, 16))
        self.grid_rowconfigure(5, weight=1)
        self._roles_label = ctk.CTkLabel(
            self._roles_frame,
            text="Load a user to see their current roles.",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
        )
        self._roles_label.pack(anchor="w", padx=8, pady=8)

        self._status = W.status_label(self)
        self._status.grid(row=6, column=0, columnspan=3, sticky="w")

    def _load_user_roles(self) -> None:
        username = self._username_entry.get().strip()
        ok, err = validate_required(username, "Username")
        if not ok:
            W.set_status(self._status, err, "error")
            return
        try:
            roles = self._role_svc.get_user_roles(username)
            self._current_roles = roles
            self._render_roles()
            W.set_status(self._status, f"Loaded {len(roles)} role(s) for '{username}'.", "info")
        except APIError as exc:
            W.set_status(self._status, f"✖ {exc}", "error")

    def _render_roles(self) -> None:
        for widget in self._roles_frame.winfo_children():
            widget.destroy()
        if not self._current_roles:
            ctk.CTkLabel(
                self._roles_frame,
                text="No roles assigned.",
                font=ctk.CTkFont(size=11),
                text_color="#888888",
            ).pack(anchor="w", padx=8, pady=8)
            return
        for role in self._current_roles:
            row = ctk.CTkFrame(self._roles_frame, fg_color="transparent")
            row.pack(fill="x", padx=4, pady=2)
            name = role.get("roleName", role.get("displayName", str(role)))
            membership_id = role.get("id", role.get("roleMembershipId", ""))
            ctk.CTkLabel(
                row, text=name, font=ctk.CTkFont(size=12), text_color=W.LABEL_FG, anchor="w"
            ).pack(side="left", fill="x", expand=True)
            if membership_id:
                W.secondary_button(
                    row,
                    "Remove",
                    command=lambda mid=membership_id, rname=name: self._on_remove(mid, rname),
                ).pack(side="right")

    def _on_assign(self) -> None:
        username = self._username_entry.get().strip()
        role_name = self._role_entry.get().strip()
        ok_u, err_u = validate_required(username, "Username")
        ok_r, err_r = validate_required(role_name, "Role Name")
        if not ok_u or not ok_r:
            W.set_status(self._status, " | ".join(filter(None, [err_u, err_r])), "error")
            return

        # SOD conflict check
        existing_role_names = [
            r.get("roleName", r.get("displayName", "")) for r in self._current_roles
        ]
        conflicts = self._sod_svc.check_conflicts(role_name, existing_role_names)
        if conflicts:
            self._audit_svc.record(
                "SOD_CONFLICT",
                username,
                "warning",
                f"SOD conflict detected assigning '{role_name}': "
                + ", ".join(c.conflicting_role for c in conflicts),
            )
            proceed = W.sod_warning(self, role_name, conflicts)
            if not proceed:
                W.set_status(self._status, "Assignment cancelled due to SOD conflict.", "warning")
                return

        try:
            self._role_svc.assign_role(username, role_name)
            self._audit_svc.record("ASSIGN_ROLE", username, "success", f"Role '{role_name}' assigned.")
            W.set_status(self._status, f"✔ Role '{role_name}' assigned to '{username}'.", "success")
            self._role_entry.delete(0, "end")
            self._load_user_roles()
        except APIError as exc:
            self._audit_svc.record("ASSIGN_ROLE", username, "error", str(exc))
            W.set_status(self._status, f"✖ {exc}", "error")

    def _on_remove(self, membership_id: str, role_name: str) -> None:
        username = self._username_entry.get().strip()
        if not W.confirm(self, "Confirm Remove", f"Remove role '{role_name}' from '{username}'?"):
            return
        try:
            self._role_svc.remove_role(membership_id)
            self._audit_svc.record("REMOVE_ROLE", username, "success", f"Role '{role_name}' removed.")
            W.set_status(self._status, f"✔ Role '{role_name}' removed.", "success")
            self._load_user_roles()
        except APIError as exc:
            self._audit_svc.record("REMOVE_ROLE", username, "error", str(exc))
            W.set_status(self._status, f"✖ {exc}", "error")
