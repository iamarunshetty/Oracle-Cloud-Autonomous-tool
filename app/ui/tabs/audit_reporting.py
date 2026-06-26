"""
Audit & Reporting tab.

Capabilities (UI-wired, backend stubs):
  - User creation report
  - Role assignment report
  - Access change history
  - Audit trail view
  - Excel / PDF export
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.models.report import ReportFormat, ReportRequest, ReportType
from app.services.reporting_service import reporting_service
from app.storage.repositories import audit_repo


class AuditReportingTab(QWidget):
    def __init__(self, log_fn=None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._log = log_fn or (lambda msg: None)
        self._current_rows: list[dict] = []
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Report selector
        selector_row = QHBoxLayout()
        selector_row.addWidget(QLabel("Report:"))
        self._report_combo = QComboBox()
        for rt in ReportType:
            self._report_combo.addItem(rt.value, userData=rt)
        selector_row.addWidget(self._report_combo)

        selector_row.addWidget(QLabel("Format:"))
        self._format_combo = QComboBox()
        for rf in ReportFormat:
            self._format_combo.addItem(rf.value, userData=rf)
        selector_row.addWidget(self._format_combo)

        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self._on_preview)
        selector_row.addWidget(preview_btn)

        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self._on_export)
        selector_row.addWidget(export_btn)

        layout.addLayout(selector_row)

        # Results table
        self._table = QTableWidget()
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self._table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self._table)

        # Audit trail quick view
        audit_row = QHBoxLayout()
        audit_trail_btn = QPushButton("View Audit Trail")
        audit_trail_btn.clicked.connect(self._on_audit_trail)
        audit_row.addWidget(audit_trail_btn)
        audit_row.addStretch()
        layout.addLayout(audit_row)

    # ------------------------------------------------------------------

    def _selected_report_type(self) -> ReportType:
        return self._report_combo.currentData()

    def _selected_format(self) -> ReportFormat:
        return self._format_combo.currentData()

    def _populate_table(self, rows: list[dict]) -> None:
        self._current_rows = rows
        if not rows:
            self._table.setColumnCount(1)
            self._table.setHorizontalHeaderLabels(["Result"])
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem("No data available."))
            return
        headers = list(rows[0].keys())
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(len(rows))
        for row_idx, row in enumerate(rows):
            for col_idx, h in enumerate(headers):
                self._table.setItem(row_idx, col_idx, QTableWidgetItem(str(row.get(h, ""))))
        self._table.resizeColumnsToContents()

    def _on_preview(self) -> None:
        rt = self._selected_report_type()
        request = ReportRequest(report_type=rt, format=self._selected_format(), requested_by="ui_user")
        # Collect data without writing file
        rows = reporting_service._collect_data(request)  # noqa: SLF001
        self._populate_table(rows)
        self._log(f"Preview: {rt.value} – {len(rows)} row(s)")

    def _on_export(self) -> None:
        rt = self._selected_report_type()
        fmt = self._selected_format()
        save_dir = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if not save_dir:
            return
        request = ReportRequest(report_type=rt, format=fmt, requested_by="ui_user")
        result = reporting_service.generate(request, output_dir=save_dir)
        if result.success:
            QMessageBox.information(self, "Export Complete", f"Report saved to:\n{result.output_path}")
            self._log(f"Exported {rt.value} ({fmt.value}) → {result.output_path}")
        else:
            QMessageBox.critical(self, "Export Failed", result.error or "Unknown error")
            self._log(f"Export failed: {result.error}")

    def _on_audit_trail(self) -> None:
        rows = audit_repo.list(limit=500)
        self._populate_table(rows)
        self._log(f"Audit trail loaded: {len(rows)} record(s)")
