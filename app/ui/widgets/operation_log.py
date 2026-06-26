"""Operation-log panel widget."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPlainTextEdit, QVBoxLayout, QWidget


class OperationLogPanel(QWidget):
    """Scrollable read-only log panel shown at the bottom of the main window."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._text = QPlainTextEdit()
        self._text.setReadOnly(True)
        self._text.setMaximumHeight(120)
        self._text.setPlaceholderText("Operation log…")
        layout.addWidget(self._text)

    def append(self, message: str) -> None:
        """Append a line to the log."""
        self._text.appendPlainText(message)
        sb = self._text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear(self) -> None:
        self._text.clear()
