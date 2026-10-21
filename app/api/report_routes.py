from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from app.database import get_db
from app.models import User
from app.auth import get_current_user, require_hod
from app.workload import get_department_workload_summary
from app.reports import generate_workload_excel, generate_workload_pdf

router = APIRouter(prefix="/api/reports", tags=["Reports & Analytics"])

@router.get("/summary")
def get_reports_summary(
    department: Optional[str] = Query(None),
    academic_week: Optional[int] = Query(None),
    period: str = Query("weekly", description="weekly or monthly"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    """Provides departmental workload metrics, averages, high/low workload breakdowns."""
    summary = get_department_workload_summary(db, department=department, academic_week=academic_week)
    summary["report_period"] = period
    summary["generated_at"] = datetime.datetime.now().isoformat()
    return summary

@router.get("/export/excel")
def export_excel_report(
    department: Optional[str] = Query(None),
    academic_week: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    """Exports multi-sheet Excel spreadsheet with workloads, schedules, and metrics."""
    excel_bytes = generate_workload_excel(db, department=department, academic_week=academic_week)
    filename = f"faculty_workload_report_{datetime.date.today().strftime('%Y%m%d')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.get("/export/pdf")
def export_pdf_report(
    department: Optional[str] = Query(None),
    academic_week: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    """Exports official institutionally styled PDF document."""
    pdf_bytes = generate_workload_pdf(db, department=department, academic_week=academic_week)
    filename = f"faculty_workload_report_{datetime.date.today().strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
