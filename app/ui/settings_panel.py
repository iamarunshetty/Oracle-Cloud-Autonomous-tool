"""
Settings panel – configure Oracle Fusion connection details at runtime.
"""

from __future__ import annotations

import os

import customtkinter as ctk

from app.config import Config, OracleConfig
from app.ui import widgets as W


class SettingsFrame(ctk.CTkFrame):
    """
    Lets users enter/update connection settings without restarting the app.
    Values are kept in memory only and are NOT written to disk.
    """

    def __init__(self, parent, config: Config, on_save_callback=None):
        super().__init__(parent, fg_color="transparent")
        self._config = config
        self._on_save = on_save_callback
        self._build()

    def _build(self) -> None:
        W.heading(self, "Connection Settings").grid(row=0, column=0, columnspan=2, pady=(0, 6), sticky="w")

        notice = ctk.CTkLabel(
            self,
            text="Changes apply to the current session only and are NOT saved to disk. "
                 "Use .env or config.json for persistent configuration.",
            font=ctk.CTkFont(size=11),
            text_color="#aaaaaa",
            wraplength=500,
            justify="left",
        )
        notice.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 16))

        fields = [
            ("Base URL *", "base_url", "", False),
            ("Username", "username", "", False),
            ("Password", "password", "", True),
            ("Bearer Token", "token", "Overrides username/password", True),
            ("Timeout (s)", "timeout", "", False),
            ("Retry Count", "retry_count", "", False),
        ]
        self._entries: dict[str, ctk.CTkEntry] = {}

        for i, (label_text, key, hint, masked) in enumerate(fields, start=2):
            W.form_label(self, label_text).grid(row=i, column=0, sticky="w", pady=4, padx=(0, 12))
            entry = W.form_entry(self, placeholder=hint, show="●" if masked else "", width=320)
            entry.grid(row=i, column=1, sticky="ew", pady=4)
            self._entries[key] = entry

        self.grid_columnconfigure(1, weight=1)

        # Pre-fill current values (mask secrets)
        self._entries["base_url"].insert(0, self._config.oracle.base_url)
        self._entries["username"].insert(0, self._config.oracle.username)
        self._entries["timeout"].insert(0, str(self._config.oracle.timeout))
        self._entries["retry_count"].insert(0, str(self._config.oracle.retry_count))

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=len(fields) + 2, column=0, columnspan=2, pady=16, sticky="w")
        W.primary_button(btn_row, "Apply Settings", command=self._on_apply).pack(side="left", padx=(0, 8))
        W.secondary_button(btn_row, "Reset to Env Defaults", command=self._reset).pack(side="left")

        self._status = W.status_label(self)
        self._status.grid(row=len(fields) + 3, column=0, columnspan=2, sticky="w")

    def _on_apply(self) -> None:
        base_url = self._entries["base_url"].get().strip()
        if not base_url:
            W.set_status(self._status, "Base URL is required.", "error")
            return

        try:
            timeout = int(self._entries["timeout"].get().strip() or "30")
            retry = int(self._entries["retry_count"].get().strip() or "3")
        except ValueError:
            W.set_status(self._status, "Timeout and Retry Count must be integers.", "error")
            return

        self._config.oracle.base_url = base_url
        self._config.oracle.username = self._entries["username"].get().strip()
        self._config.oracle.password = self._entries["password"].get()
        self._config.oracle.token = self._entries["token"].get()
        self._config.oracle.timeout = timeout
        self._config.oracle.retry_count = retry

        if self._on_save:
            self._on_save()

        W.set_status(self._status, "✔ Settings applied for this session.", "success")

    def _reset(self) -> None:
        from app.config import load_config
        fresh = load_config()
        self._config.oracle = fresh.oracle
        self._entries["base_url"].delete(0, "end")
        self._entries["base_url"].insert(0, fresh.oracle.base_url)
        self._entries["username"].delete(0, "end")
        self._entries["username"].insert(0, fresh.oracle.username)
        self._entries["password"].delete(0, "end")
        self._entries["token"].delete(0, "end")
        self._entries["timeout"].delete(0, "end")
        self._entries["timeout"].insert(0, str(fresh.oracle.timeout))
        self._entries["retry_count"].delete(0, "end")
        self._entries["retry_count"].insert(0, str(fresh.oracle.retry_count))
        W.set_status(self._status, "Reset to environment defaults.", "info")
