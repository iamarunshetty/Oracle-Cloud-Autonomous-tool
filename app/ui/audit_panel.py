"""
Audit Log panel – shows recent operations and provides CSV export.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog
from datetime import datetime, timezone

import customtkinter as ctk

from app.services.audit_service import AuditService
from app.ui import widgets as W


class AuditFrame(ctk.CTkFrame):
    def __init__(self, parent, audit_service: AuditService):
        super().__init__(parent, fg_color="transparent")
        self._audit_svc = audit_service
        self._build()

    def _build(self) -> None:
        W.heading(self, "Audit Log").grid(row=0, column=0, columnspan=2, pady=(0, 16), sticky="w")

        # Toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 12))
        W.primary_button(toolbar, "⟳  Refresh", command=self._refresh).pack(side="left", padx=(0, 8))
        W.secondary_button(toolbar, "⬇  Export CSV", command=self._export).pack(side="left")

        # Table header
        header = ctk.CTkFrame(self, fg_color="#1a1a2e")
        header.grid(row=2, column=0, columnspan=2, sticky="nsew")
        self.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        for col, label in enumerate(["Timestamp", "Action", "Target User", "Result", "Message"]):
            ctk.CTkLabel(
                header,
                text=label,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#aaaaaa",
                anchor="w",
            ).grid(row=0, column=col, sticky="ew", padx=8, pady=6)

        # Scrollable rows container
        self._rows_frame = ctk.CTkScrollableFrame(self, height=340)
        self._rows_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(0, 12))
        self.grid_rowconfigure(3, weight=1)

        self._status = W.status_label(self)
        self._status.grid(row=4, column=0, columnspan=2, sticky="w")

        self._refresh()

    def _refresh(self) -> None:
        for widget in self._rows_frame.winfo_children():
            widget.destroy()

        entries = self._audit_svc.get_entries()
        if not entries:
            ctk.CTkLabel(
                self._rows_frame,
                text="No audit entries yet.",
                font=ctk.CTkFont(size=11),
                text_color="#888888",
            ).pack(anchor="w", padx=8, pady=8)
            W.set_status(self._status, "No entries.", "info")
            return

        for entry in reversed(entries):  # newest first
            row_frame = ctk.CTkFrame(self._rows_frame, fg_color="transparent")
            row_frame.pack(fill="x", padx=4, pady=1)
            row_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

            result_color = W.SUCCESS_GREEN if entry.result == "success" else W.ERROR_RED
            values = [entry.timestamp, entry.action, entry.target_user, entry.result, entry.message]
            for col, val in enumerate(values):
                color = result_color if col == 3 else W.LABEL_FG
                ctk.CTkLabel(
                    row_frame,
                    text=val,
                    font=ctk.CTkFont(size=11),
                    text_color=color,
                    anchor="w",
                    wraplength=180,
                ).grid(row=0, column=col, sticky="ew", padx=8, pady=3)

        W.set_status(self._status, f"{len(entries)} entries.", "info")

    def _export(self) -> None:
        entries = self._audit_svc.get_entries()
        if not entries:
            W.set_status(self._status, "Nothing to export.", "warning")
            return

        default = f"audit_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialfile=default,
            title="Export Audit Log",
        )
        if not path:
            return
        try:
            saved = self._audit_svc.export_csv(path)
            W.set_status(self._status, f"✔ Exported {len(entries)} entries to {saved}.", "success")
        except OSError as exc:
            W.set_status(self._status, f"✖ Export failed: {exc}", "error")
