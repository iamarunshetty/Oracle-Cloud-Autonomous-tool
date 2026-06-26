"""Tests for report export utilities (Excel and CSV paths)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.models.report import ReportFormat, ReportRequest, ReportType
from app.services.reporting_service import ReportingService


@pytest.fixture()
def service() -> ReportingService:
    return ReportingService()


@pytest.fixture()
def sample_rows() -> list[dict]:
    return [
        {"Username": "jdoe", "Full Name": "John Doe", "Status": "Active"},
        {"Username": "asmith", "Full Name": "Alice Smith", "Status": "Inactive"},
    ]


class TestExcelExport:
    def test_creates_file(self, service: ReportingService, tmp_path: Path, sample_rows) -> None:
        out = tmp_path / "report.xlsx"
        service._export_excel(sample_rows, out, title="Test Report")
        assert out.exists()
        assert out.stat().st_size > 0

    def test_empty_rows_creates_file(self, service: ReportingService, tmp_path: Path) -> None:
        out = tmp_path / "empty.xlsx"
        service._export_excel([], out, title="Empty")
        assert out.exists()

    def test_headers_present(self, service: ReportingService, tmp_path: Path, sample_rows) -> None:
        import openpyxl

        out = tmp_path / "headers.xlsx"
        service._export_excel(sample_rows, out)
        wb = openpyxl.load_workbook(str(out))
        ws = wb.active
        first_row = [cell.value for cell in ws[1]]
        assert "Username" in first_row
        assert "Full Name" in first_row


class TestCsvExport:
    def test_creates_file(self, service: ReportingService, tmp_path: Path, sample_rows) -> None:
        out = tmp_path / "report.csv"
        service._export_csv(sample_rows, out)
        assert out.exists()

    def test_content(self, service: ReportingService, tmp_path: Path, sample_rows) -> None:
        out = tmp_path / "content.csv"
        service._export_csv(sample_rows, out)
        content = out.read_text(encoding="utf-8")
        assert "jdoe" in content
        assert "asmith" in content

    def test_empty_rows(self, service: ReportingService, tmp_path: Path) -> None:
        out = tmp_path / "empty.csv"
        service._export_csv([], out)
        assert out.exists()


class TestReportGenerate:
    def test_generate_excel_report(self, service: ReportingService, tmp_path: Path) -> None:
        request = ReportRequest(
            report_type=ReportType.USER_CREATION,
            format=ReportFormat.EXCEL,
            requested_by="test",
        )
        result = service.generate(request, output_dir=tmp_path)
        # Even with no users in memory the export should succeed
        assert result.error is None or result.output_path is not None

    def test_generate_csv_report(self, service: ReportingService, tmp_path: Path, monkeypatch) -> None:
        # Use USER_CREATION (no DB access) to avoid requiring a live DB connection
        request = ReportRequest(
            report_type=ReportType.USER_CREATION,
            format=ReportFormat.CSV,
            requested_by="test",
        )
        result = service.generate(request, output_dir=tmp_path)
        assert result.error is None or result.output_path is not None
