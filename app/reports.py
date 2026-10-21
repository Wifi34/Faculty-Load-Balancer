import io
import datetime
import pandas as pd
from typing import Optional
from sqlalchemy.orm import Session
from app.workload import get_department_workload_summary
from app.models import Schedule, FacultyProfile, Classroom, Subject, AcademicClass

# ReportLab imports for institutional PDF generation
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

def generate_workload_excel(db: Session, department: Optional[str] = None, academic_week: Optional[int] = None) -> bytes:
    """Generates an Excel workbook (.xlsx) containing comprehensive workload reports."""
    summary_data = get_department_workload_summary(db, department=department, academic_week=academic_week)
    faculty_list = summary_data["faculty_list"]

    # 1. Faculty Workload DataFrame
    fac_records = []
    for f in faculty_list:
        fac_records.append({
            "Faculty Code": f["faculty_code"],
            "Faculty Name": f["name"],
            "Department": f["department"],
            "Designation": f["designation"],
            "Subjects Taught": f["subjects_taught"],
            "Regular Lectures": f["regular_lectures"],
            "Substitute Lectures": f["substitute_lectures"],
            "Lab Sessions": f["lab_duties"],
            "Exam Duties": f["exam_duties"],
            "College Duties": f["college_duties"],
            "Total Weekly Lectures": f["weekly_lectures"],
            "Total Duties": f["assigned_duties"],
            "Total Load (Hours)": f["total_load_hours"],
            "Weekly Limit (Hours)": f["weekly_lecture_limit"],
            "Workload Status": f["workload_status"],
            "Available Slots": f["available_slots"],
            "Can Take Extra Duties": "Yes" if f["can_take_extra"] else "No"
        })
    df_faculty = pd.DataFrame(fac_records)

    # 2. Detailed Schedule DataFrame
    sched_query = db.query(Schedule).filter(Schedule.status != "cancelled")
    if academic_week:
        sched_query = sched_query.filter(Schedule.academic_week == academic_week)
    all_schedules = sched_query.all()

    sched_records = []
    for s in all_schedules:
        faculty = db.query(FacultyProfile).filter(FacultyProfile.id == s.faculty_id).first()
        subj = db.query(Subject).filter(Subject.id == s.subject_id).first() if s.subject_id else None
        cls = db.query(AcademicClass).filter(AcademicClass.id == s.class_id).first() if s.class_id else None
        room = db.query(Classroom).filter(Classroom.id == s.classroom_id).first() if s.classroom_id else None

        sched_records.append({
            "Schedule ID": s.id,
            "Type": s.schedule_type.replace('_', ' ').title(),
            "Day": s.day_of_week,
            "Date": s.date,
            "Time": f"{s.start_time} - {s.end_time}",
            "Duration (Hrs)": s.duration_hours or 1.0,
            "Faculty Name": faculty.name if faculty else "N/A",
            "Subject": subj.name if subj else (s.duty_title or "Duty"),
            "Class / Semester": cls.name if cls else "N/A",
            "Classroom / Lab": room.room_no if room else "N/A",
            "HOD Instructions": s.instructions or "",
            "Status": s.status.title()
        })
    df_schedules = pd.DataFrame(sched_records)

    # 3. Department KPI Metrics DataFrame
    kpi_records = [{
        "Metric": "Total Faculty Members",
        "Value": summary_data["total_faculty"]
    }, {
        "Metric": "Total Lectures Scheduled This Week",
        "Value": summary_data["total_lectures_scheduled"]
    }, {
        "Metric": "Total Duties Assigned",
        "Value": summary_data["total_duties_assigned"]
    }, {
        "Metric": "Average Teaching Load (Hours/Faculty)",
        "Value": f"{summary_data['average_teaching_load']} hrs"
    }, {
        "Metric": "High Workload Faculty Count",
        "Value": summary_data["workload_breakdown"]["high"]
    }, {
        "Metric": "Balanced Workload Faculty Count",
        "Value": summary_data["workload_breakdown"]["balanced"]
    }, {
        "Metric": "Low Workload Faculty Count",
        "Value": summary_data["workload_breakdown"]["low"]
    }, {
        "Metric": "Faculty Available for Extra Duties",
        "Value": summary_data["available_faculty_count"]
    }]
    df_kpis = pd.DataFrame(kpi_records)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_faculty.to_excel(writer, sheet_name='Faculty Workloads', index=False)
        df_schedules.to_excel(writer, sheet_name='Detailed Schedules', index=False)
        df_kpis.to_excel(writer, sheet_name='Department KPIs', index=False)

    output.seek(0)
    return output.getvalue()


def generate_workload_pdf(db: Session, department: Optional[str] = None, academic_week: Optional[int] = None) -> bytes:
    """Generates a professional, institutionally formatted PDF workload report."""
    summary_data = get_department_workload_summary(db, department=department, academic_week=academic_week)
    faculty_list = summary_data["faculty_list"]

    buffer = io.BytesIO()
    # Landscape orientation for wide tabular data
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        'CollegeTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a')
    )
    subtitle_style = ParagraphStyle(
        'CollegeSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#475569')
    )
    meta_style = ParagraphStyle(
        'ReportMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#64748b')
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10
    )
    cell_bold_style = ParagraphStyle(
        'CellTextBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10
    )
    kpi_title_style = ParagraphStyle(
        'KpiTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1e3a8a')
    )

    elements = []

    # 1. Header Section
    elements.append(Paragraph("APEX INSTITUTE OF ENGINEERING & TECHNOLOGY", title_style))
    elements.append(Paragraph("FACULTY LOAD MANAGEMENT SYSTEM — DEPARTMENTAL WORKLOAD REPORT", subtitle_style))
    now_str = datetime.datetime.now().strftime("%d %b %Y, %I:%M %p")
    dept_label = department or "Computer Science & Engineering"
    elements.append(Paragraph(f"Department: <b>{dept_label}</b> | Academic Year: <b>2026-2027</b> | Generated: {now_str}", subtitle_style))
    elements.append(Spacer(1, 12))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=12))

    # 2. Executive KPI Summary Cards / Table
    kpis = summary_data["workload_breakdown"]
    kpi_table_data = [
        [
            Paragraph(f"<b>Total Faculty</b><br/>{summary_data['total_faculty']}", kpi_title_style),
            Paragraph(f"<b>Total Scheduled</b><br/>{summary_data['total_lectures_scheduled']} Lectures", kpi_title_style),
            Paragraph(f"<b>Total Duties</b><br/>{summary_data['total_duties_assigned']} Assigned", kpi_title_style),
            Paragraph(f"<b>Avg Department Load</b><br/>{summary_data['average_teaching_load']} Hours/Week", kpi_title_style),
            Paragraph(f"<b>High Load</b>: {kpis['high']}<br/><b>Balanced</b>: {kpis['balanced']} | <b>Low</b>: {kpis['low']}", kpi_title_style),
            Paragraph(f"<b>Available for Extra</b><br/>{summary_data['available_faculty_count']} Faculty", kpi_title_style)
        ]
    ]
    kpi_table = Table(kpi_table_data, colWidths=[120, 120, 120, 130, 120, 130])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#bfdbfe')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dbeafe')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 15))

    # 3. Faculty Workload Table
    table_headers = [
        "Faculty Code", "Faculty Name", "Designation",
        "Reg. Lec", "Sub. Lec", "Labs", "Duties",
        "Total Load", "Limit", "Status", "Available Slots"
    ]
    table_data = [[Paragraph(f"<b>{h}</b>", cell_bold_style) for h in table_headers]]

    for f in faculty_list:
        status_color = "#dc2626" if f["workload_status"] == "High" else ("#16a34a" if f["workload_status"] == "Balanced" else "#2563eb")
        table_data.append([
            Paragraph(f["faculty_code"], cell_style),
            Paragraph(f"<b>{f['name']}</b>", cell_style),
            Paragraph(f["designation"], cell_style),
            Paragraph(str(f["regular_lectures"]), cell_style),
            Paragraph(str(f["substitute_lectures"]), cell_style),
            Paragraph(str(f["lab_duties"]), cell_style),
            Paragraph(str(f["assigned_duties"]), cell_style),
            Paragraph(f"<b>{f['total_load_hours']} hrs</b>", cell_style),
            Paragraph(f"{f['weekly_lecture_limit']} hrs", cell_style),
            Paragraph(f"<font color='{status_color}'><b>{f['workload_status']}</b></font>", cell_style),
            Paragraph(f"{f['available_slots']} slots", cell_style)
        ])

    fac_table = Table(
        table_data,
        colWidths=[65, 140, 110, 45, 45, 40, 45, 65, 50, 60, 75]
    )
    fac_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a8a')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ('ALIGN', (3, 1), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(fac_table)
    elements.append(Spacer(1, 20))

    # 4. Sign-off / Verification section
    sig_data = [
        [
            Paragraph("Prepared by:<br/><b>Academic Coordinator</b>", cell_style),
            Paragraph("Verified & Recommended by:<br/><b>Head of Department (HOD)</b>", cell_style),
            Paragraph("Approved by:<br/><b>Dean Academics / Principal</b>", cell_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[240, 260, 240])
    sig_table.setStyle(TableStyle([
        ('LINEABOVE', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
