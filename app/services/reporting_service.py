"""
Reporting service – Excel and PDF export.

Dependencies: pandas, openpyxl, reportlab
"""
from __future__ import annotations

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models.audit import AuditAction
from app.models.report import ReportFormat, ReportRequest, ReportResult, ReportType
from app.services.base import audit
from app.storage.repositories import audit_repo

logger = logging.getLogger(__name__)


class ReportingService:
    # ------------------------------------------------------------------
    # Data collectors (stubs – replace with live queries / service calls)
    # ------------------------------------------------------------------

    def _collect_data(self, request: ReportRequest) -> list[dict[str, Any]]:
        """Route to the correct data collector based on report type."""
        collectors = {
            ReportType.USER_CREATION: self._collect_user_creation,
            ReportType.ROLE_ASSIGNMENT: self._collect_role_assignment,
            ReportType.ACCESS_CHANGE_HISTORY: self._collect_access_history,
            ReportType.AUDIT_TRAIL: self._collect_audit_trail,
            ReportType.INACTIVE_USERS: self._collect_inactive_users,
            ReportType.ORPHAN_ROLES: self._collect_orphan_roles,
            ReportType.SOD_VIOLATIONS: self._collect_sod_violations,
            ReportType.ELEVATED_ACCESS: self._collect_elevated_access,
            ReportType.DUPLICATE_ACCESS: self._collect_duplicate_access,
        }
        collector = collectors.get(request.report_type)
        if collector is None:
            return []
        return collector(request)

    def _collect_user_creation(self, request: ReportRequest) -> list[dict]:
        """TODO: Query Fusion HCM for user creation events."""
        from app.services.user_service import user_service

        return [
            {
                "Username": u.username,
                "Full Name": u.full_name,
                "Email": u.email,
                "Status": u.status.value,
                "Department": u.department or "",
                "Created At": str(u.created_at),
            }
            for u in user_service.list_users()
        ]

    def _collect_role_assignment(self, request: ReportRequest) -> list[dict]:
        """TODO: Query Fusion for role assignment history."""
        from app.services.role_service import role_service
        from app.services.user_service import user_service

        rows = []
        for user in user_service.list_users():
            for a in role_service.get_user_roles(user.username):
                rows.append(
                    {
                        "Username": user.username,
                        "Role Code": a.role_code,
                        "Status": a.status.value,
                        "Assigned By": a.assigned_by or "",
                        "Assigned At": str(a.assigned_at),
                        "Justification": a.justification or "",
                    }
                )
        return rows

    def _collect_access_history(self, request: ReportRequest) -> list[dict]:
        """TODO: Pull from Fusion audit log / operation_history."""
        return audit_repo.list(limit=1000, action=AuditAction.ASSIGN_ROLE.value)

    def _collect_audit_trail(self, request: ReportRequest) -> list[dict]:
        return audit_repo.list(limit=5000)

    def _collect_inactive_users(self, request: ReportRequest) -> list[dict]:
        from app.services.security_service import security_service

        return security_service.inactive_users_report()

    def _collect_orphan_roles(self, request: ReportRequest) -> list[dict]:
        from app.services.security_service import security_service

        return security_service.detect_orphan_roles()

    def _collect_sod_violations(self, request: ReportRequest) -> list[dict]:
        from app.services.security_service import security_service
        from app.services.user_service import user_service

        rows = []
        for user in user_service.list_users():
            rows.extend(security_service.sod_check(user.username))
        return rows

    def _collect_elevated_access(self, request: ReportRequest) -> list[dict]:
        from app.services.security_service import security_service

        return security_service.detect_elevated_access()

    def _collect_duplicate_access(self, request: ReportRequest) -> list[dict]:
        from app.services.security_service import security_service

        return security_service.detect_duplicate_access()

    # ------------------------------------------------------------------
    # Export drivers
    # ------------------------------------------------------------------

    def generate(self, request: ReportRequest, output_dir: str | Path = ".") -> ReportResult:
        """Generate a report and write it to *output_dir*."""
        rows = self._collect_data(request)
        result = ReportResult(request=request, rows=rows)

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        stem = request.report_type.value.replace(" ", "_")
        try:
            if request.format == ReportFormat.EXCEL:
                path = output_dir / f"{stem}_{timestamp}.xlsx"
                self._export_excel(rows, path, title=request.report_type.value)
            elif request.format == ReportFormat.PDF:
                path = output_dir / f"{stem}_{timestamp}.pdf"
                self._export_pdf(rows, path, title=request.report_type.value)
            elif request.format == ReportFormat.CSV:
                path = output_dir / f"{stem}_{timestamp}.csv"
                self._export_csv(rows, path)
            else:
                raise ValueError(f"Unsupported format: {request.format}")

            result.output_path = path
            audit(
                AuditAction.EXPORT_REPORT,
                performed_by=request.requested_by,
                description=f"Exported {request.report_type.value} as {request.format.value}",
                payload={"rows": len(rows), "path": str(path)},
            )
        except Exception as exc:  # noqa: BLE001
            result.error = str(exc)
            logger.error("Report generation failed: %s", exc)

        return result

    # ------------------------------------------------------------------
    # Format writers
    # ------------------------------------------------------------------

    def _export_excel(self, rows: list[dict], path: Path, title: str = "") -> None:
        import openpyxl
        from openpyxl.styles import Font, PatternFill

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = title[:31] if title else "Report"

        if not rows:
            ws.append(["No data available"])
            wb.save(path)
            return

        headers = list(rows[0].keys())
        header_row = ws.append  # reference before loop
        ws.append(headers)
        # Style header
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="003366")

        for row in rows:
            ws.append([str(row.get(h, "")) for h in headers])

        wb.save(path)
        logger.info("Excel report saved: %s", path)

    def _export_pdf(self, rows: list[dict], path: Path, title: str = "") -> None:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

        doc = SimpleDocTemplate(str(path), pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(title, styles["Title"]))
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(
            Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"])
        )
        elements.append(Spacer(1, 0.5 * cm))

        if not rows:
            elements.append(Paragraph("No data available.", styles["Normal"]))
        else:
            headers = list(rows[0].keys())
            data = [headers] + [[str(row.get(h, "")) for h in headers] for row in rows]
            table = Table(data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#EEF2F7")]),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            elements.append(table)

        doc.build(elements)
        logger.info("PDF report saved: %s", path)

    def _export_csv(self, rows: list[dict], path: Path) -> None:
        import csv

        if not rows:
            path.write_text("No data\n")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        logger.info("CSV report saved: %s", path)


reporting_service = ReportingService()
