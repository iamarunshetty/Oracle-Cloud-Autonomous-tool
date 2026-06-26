"""
Job Monitor tab.

Displays recent background operations (bulk upload, report generation, etc.)
and their current status using the operation_history table.
"""
from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.storage.repositories import op_history_repo


class JobMonitorTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._build_ui()
        self._refresh()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["ID", "Operation", "Initiated By", "Status", "Started At", "Finished At"]
        )
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)

        btn_row = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh)
        btn_row.addWidget(refresh_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def _refresh(self) -> None:
        rows = op_history_repo.list(limit=100)
        self._table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            self._table.setItem(row_idx, 0, QTableWidgetItem(str(row.get("id", ""))))
            self._table.setItem(row_idx, 1, QTableWidgetItem(row.get("operation_type", "")))
            self._table.setItem(row_idx, 2, QTableWidgetItem(row.get("initiated_by", "")))
            self._table.setItem(row_idx, 3, QTableWidgetItem(row.get("status", "")))
            self._table.setItem(row_idx, 4, QTableWidgetItem(row.get("started_at", "")))
            self._table.setItem(row_idx, 5, QTableWidgetItem(row.get("finished_at", "") or ""))
        self._log(f"Job monitor refreshed: {len(rows)} operation(s)")
