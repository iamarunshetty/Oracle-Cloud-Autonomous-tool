"""
Reusable UI widgets and helpers built on top of CustomTkinter.
"""

from __future__ import annotations

import customtkinter as ctk


# ------------------------------------------------------------------
# Colour / theme tokens
# ------------------------------------------------------------------

ACCENT_BLUE = "#1e6dbf"
ERROR_RED = "#d32f2f"
SUCCESS_GREEN = "#388e3c"
WARNING_ORANGE = "#f57c00"
BG_SECONDARY = "#1a1a2e"
LABEL_FG = "#e0e0e0"


def heading(parent: ctk.CTkFrame, text: str, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color=LABEL_FG,
        **kwargs,
    )


def subheading(parent: ctk.CTkFrame, text: str, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color=LABEL_FG,
        **kwargs,
    )


def form_label(parent: ctk.CTkFrame, text: str, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text=text,
        font=ctk.CTkFont(size=12),
        text_color=LABEL_FG,
        anchor="w",
        **kwargs,
    )


def form_entry(parent: ctk.CTkFrame, placeholder: str = "", show: str = "", **kwargs) -> ctk.CTkEntry:
    return ctk.CTkEntry(
        parent,
        placeholder_text=placeholder,
        show=show,
        font=ctk.CTkFont(size=12),
        height=34,
        **kwargs,
    )


def primary_button(parent, text: str, command=None, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color=ACCENT_BLUE,
        hover_color="#1558a0",
        font=ctk.CTkFont(size=12, weight="bold"),
        height=36,
        **kwargs,
    )


def secondary_button(parent, text: str, command=None, **kwargs) -> ctk.CTkButton:
    return ctk.CTkButton(
        parent,
        text=text,
        command=command,
        fg_color="transparent",
        border_width=1,
        border_color=ACCENT_BLUE,
        text_color=ACCENT_BLUE,
        hover_color="#e3eefa",
        font=ctk.CTkFont(size=12),
        height=36,
        **kwargs,
    )


def status_label(parent: ctk.CTkFrame, **kwargs) -> ctk.CTkLabel:
    return ctk.CTkLabel(
        parent,
        text="",
        font=ctk.CTkFont(size=11),
        text_color=LABEL_FG,
        wraplength=420,
        justify="left",
        **kwargs,
    )


def set_status(label: ctk.CTkLabel, message: str, kind: str = "info") -> None:
    """Update a status label with the appropriate colour."""
    colours = {
        "success": SUCCESS_GREEN,
        "error": ERROR_RED,
        "warning": WARNING_ORANGE,
        "info": LABEL_FG,
    }
    label.configure(text=message, text_color=colours.get(kind, LABEL_FG))


class ConfirmDialog(ctk.CTkToplevel):
    """Modal confirmation dialog. Returns True if the user clicked Confirm."""

    def __init__(self, parent, title: str, message: str) -> None:
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.result = False
        self._build(message)
        self.grab_set()
        self.wait_window()

    def _build(self, message: str) -> None:
        self.geometry("380x160")
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            frame,
            text=message,
            font=ctk.CTkFont(size=12),
            wraplength=340,
            justify="center",
        ).pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack()
        secondary_button(btn_row, "Cancel", command=self._cancel).pack(side="left", padx=6)
        primary_button(btn_row, "Confirm", command=self._confirm).pack(side="left", padx=6)

    def _confirm(self) -> None:
        self.result = True
        self.destroy()

    def _cancel(self) -> None:
        self.result = False
        self.destroy()


def confirm(parent, title: str, message: str) -> bool:
    """Show a confirmation dialog. Returns True if confirmed."""
    dlg = ConfirmDialog(parent, title, message)
    return dlg.result


class SodWarningDialog(ctk.CTkToplevel):
    """
    Modal dialog shown when SOD conflicts are detected on a role assignment.

    Displays each conflict with its description and lets the user either cancel
    the assignment or proceed anyway (override).  Returns True when the user
    chooses to proceed.
    """

    def __init__(self, parent, proposed_role: str, conflicts: list) -> None:
        super().__init__(parent)
        self.title("⚠  SOD Conflict Detected")
        self.resizable(False, False)
        self.result = False
        self._build(proposed_role, conflicts)
        self.grab_set()
        self.wait_window()

    def _build(self, proposed_role: str, conflicts: list) -> None:
        self.geometry("480x360")
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True, padx=20, pady=16)

        # Header
        ctk.CTkLabel(
            outer,
            text="⚠  Segregation of Duties Warning",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=WARNING_ORANGE,
            anchor="w",
        ).pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            outer,
            text=f"Assigning '{proposed_role}' conflicts with the user's existing roles:",
            font=ctk.CTkFont(size=12),
            wraplength=440,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(0, 8))

        # Scrollable conflict list
        scroll = ctk.CTkScrollableFrame(outer, height=140, fg_color="#1a1a2e")
        scroll.pack(fill="x", pady=(0, 12))

        for conflict in conflicts:
            item = ctk.CTkFrame(scroll, fg_color="transparent")
            item.pack(fill="x", padx=6, pady=3)
            ctk.CTkLabel(
                item,
                text=f"• {conflict.conflicting_role}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=ERROR_RED,
                anchor="w",
            ).pack(anchor="w")
            if conflict.description:
                ctk.CTkLabel(
                    item,
                    text=f"  {conflict.description}",
                    font=ctk.CTkFont(size=10),
                    text_color="#aaaaaa",
                    wraplength=420,
                    justify="left",
                    anchor="w",
                ).pack(anchor="w")

        ctk.CTkLabel(
            outer,
            text="Proceeding may violate your organisation's compliance policy.",
            font=ctk.CTkFont(size=11),
            text_color=WARNING_ORANGE,
            wraplength=440,
            justify="left",
            anchor="w",
        ).pack(anchor="w", pady=(0, 12))

        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack()
        primary_button(btn_row, "Cancel Assignment", command=self._cancel).pack(
            side="left", padx=6
        )
        secondary_button(btn_row, "Assign Anyway", command=self._proceed).pack(
            side="left", padx=6
        )

    def _proceed(self) -> None:
        self.result = True
        self.destroy()

    def _cancel(self) -> None:
        self.result = False
        self.destroy()


def sod_warning(parent, proposed_role: str, conflicts: list) -> bool:
    """
    Show a SOD conflict warning dialog.

    Returns True if the user chooses to assign the role anyway, False to cancel.
    """
    dlg = SodWarningDialog(parent, proposed_role, conflicts)
    return dlg.result
