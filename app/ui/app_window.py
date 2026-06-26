"""
Main application window.
Provides a sidebar navigation + content area structure.
"""

from __future__ import annotations

import customtkinter as ctk

from app.api.client import OracleAPIClient
from app.config import Config
from app.services.audit_service import AuditService
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.ui.audit_panel import AuditFrame
from app.ui.create_user import CreateUserFrame
from app.ui.lock_unlock import LockUnlockFrame
from app.ui.role_management import RoleManagementFrame
from app.ui.settings_panel import SettingsFrame
from app.ui.update_user import UpdateUserFrame
from app.ui import widgets as W

# Appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

_APP_TITLE = "Oracle Fusion User Administration"
_NAV_WIDTH = 200
_SIDEBAR_BG = "#0f0f1a"


class AppWindow(ctk.CTk):
    def __init__(self, config: Config) -> None:
        super().__init__()
        self._config = config
        self._client: OracleAPIClient | None = None
        self._audit_svc = AuditService(config.app.audit_file)

        self._rebuild_client()

        self.title(_APP_TITLE)
        self.geometry("1050x700")
        self.minsize(900, 600)

        self._build_layout()
        self._show_page("create_user")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self._sidebar = ctk.CTkFrame(self, width=_NAV_WIDTH, fg_color=_SIDEBAR_BG, corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(20, weight=1)

        # App title in sidebar
        ctk.CTkLabel(
            self._sidebar,
            text="Oracle\nFusion",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#4ea8f5",
        ).grid(row=0, column=0, padx=16, pady=(24, 4), sticky="w")

        ctk.CTkLabel(
            self._sidebar,
            text="User Administration",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
        ).grid(row=1, column=0, padx=16, pady=(0, 20), sticky="w")

        # Navigation buttons
        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        nav_items = [
            ("➕  Create User", "create_user"),
            ("✏  Update User", "update_user"),
            ("🔒  Lock / Unlock", "lock_unlock"),
            ("🛡  Role Management", "role_management"),
            ("📋  Audit Log", "audit"),
            ("⚙  Settings", "settings"),
        ]
        for i, (label, page_id) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self._sidebar,
                text=label,
                command=lambda pid=page_id: self._show_page(pid),
                anchor="w",
                fg_color="transparent",
                hover_color="#1e2040",
                text_color="#cccccc",
                font=ctk.CTkFont(size=12),
                height=38,
                corner_radius=6,
            )
            btn.grid(row=i, column=0, padx=10, pady=2, sticky="ew")
            self._nav_buttons[page_id] = btn

        self._sidebar.grid_columnconfigure(0, weight=1)

        # Status bar at bottom of sidebar
        self._conn_status = ctk.CTkLabel(
            self._sidebar,
            text="⬤ Not connected",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            anchor="w",
        )
        self._conn_status.grid(row=21, column=0, padx=16, pady=16, sticky="sw")

        # Content area
        self._content = ctk.CTkFrame(self, fg_color="#12121e", corner_radius=0)
        self._content.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _show_page(self, page_id: str) -> None:
        # Highlight active nav button
        for pid, btn in self._nav_buttons.items():
            active = pid == page_id
            btn.configure(
                fg_color="#1e2040" if active else "transparent",
                text_color="white" if active else "#cccccc",
            )

        # Clear content area
        for widget in self._content.winfo_children():
            widget.destroy()

        frame = self._make_page(page_id)
        frame.grid(row=0, column=0, sticky="nsew", padx=32, pady=28)

    def _make_page(self, page_id: str) -> ctk.CTkFrame:
        client = self._get_client()
        user_svc = UserService(client)
        role_svc = RoleService(client)

        pages = {
            "create_user": lambda: CreateUserFrame(self._content, user_svc, self._audit_svc),
            "update_user": lambda: UpdateUserFrame(self._content, user_svc, self._audit_svc),
            "lock_unlock": lambda: LockUnlockFrame(self._content, user_svc, self._audit_svc),
            "role_management": lambda: RoleManagementFrame(self._content, role_svc, self._audit_svc),
            "audit": lambda: AuditFrame(self._content, self._audit_svc),
            "settings": lambda: SettingsFrame(
                self._content, self._config, on_save_callback=self._on_settings_saved
            ),
        }
        builder = pages.get(page_id)
        if builder is None:
            f = ctk.CTkFrame(self._content, fg_color="transparent")
            ctk.CTkLabel(f, text="Page not found.").pack()
            return f
        return builder()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _rebuild_client(self) -> None:
        cfg = self._config.oracle
        self._client = OracleAPIClient(
            base_url=cfg.base_url,
            username=cfg.username,
            password=cfg.password,
            token=cfg.token,
            timeout=cfg.timeout,
            retry_count=cfg.retry_count,
        )

    def _get_client(self) -> OracleAPIClient:
        if self._client is None:
            self._rebuild_client()
        return self._client  # type: ignore[return-value]

    def _on_settings_saved(self) -> None:
        """Rebuild the API client after settings are updated."""
        self._rebuild_client()
        base = self._config.oracle.base_url or "not set"
        if self._config.oracle.base_url:
            self._conn_status.configure(text=f"⬤ {base}", text_color="#4ea8f5")
        else:
            self._conn_status.configure(text="⬤ Not connected", text_color="#888888")
