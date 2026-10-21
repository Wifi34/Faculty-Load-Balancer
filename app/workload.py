from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from app.models import FacultyProfile, Schedule, Classroom, Subject, AcademicClass

# Standard college teaching slots: Mon-Sat, 9 AM to 5 PM (excluding 1-2 PM lunch) = 7 teaching hours per day * 6 days = 42 potential slots/week
STANDARD_HOURS_PER_WEEK = 42

def calculate_faculty_metrics(faculty: FacultyProfile, schedules: List[Schedule]) -> Dict[str, Any]:
    """Calculates weekly lectures, duties, total load, and status for a single faculty member."""
    regular_lectures = 0
    substitute_lectures = 0
    lab_duties = 0
    exam_duties = 0
    college_duties = 0
    total_hours = 0.0

    for s in schedules:
        if s.status == "cancelled":
            continue
        duration = s.duration_hours or 1.0
        total_hours += duration

        if s.schedule_type == "regular_lecture":
            regular_lectures += 1
        elif s.schedule_type == "substitute_lecture":
            substitute_lectures += 1
        elif s.schedule_type == "lab_duty":
            lab_duties += 1
        elif s.schedule_type == "exam_duty":
            exam_duties += 1
        elif s.schedule_type == "college_duty":
            college_duties += 1

    total_lectures = regular_lectures + substitute_lectures + lab_duties
    total_duties = exam_duties + college_duties

    # Determine Workload Status
    # Limit default is 16 hours/week
    limit = faculty.weekly_lecture_limit or 16
    if total_hours >= limit:
        status = "High"
    elif total_hours >= (limit * 0.625):  # e.g., >= 10 hours
        status = "Balanced"
    else:
        status = "Low"

    # Estimate available hours/slots (42 working slots minus busy hours)
    available_slots = max(0, int(STANDARD_HOURS_PER_WEEK - total_hours))
    # Available for extra assignments: can take more if not High workload
    can_take_extra = (status != "High") and (total_hours < limit)
    remaining_capacity = max(0.0, limit - total_hours)

    return {
        "faculty_id": faculty.id,
        "faculty_code": faculty.faculty_code,
        "name": faculty.name,
        "department": faculty.department,
        "designation": faculty.designation,
        "email": faculty.email,
        "phone": faculty.phone,
        "cabin_room": faculty.cabin_room,
        "subjects_taught": faculty.subjects_taught,
        "weekly_lecture_limit": limit,
        "max_duties_limit": faculty.max_duties_limit or 6,
        "is_active": faculty.is_active,
        # Breakdown
        "regular_lectures": regular_lectures,
        "substitute_lectures": substitute_lectures,
        "lab_duties": lab_duties,
        "exam_duties": exam_duties,
        "college_duties": college_duties,
        "weekly_lectures": total_lectures,
        "assigned_duties": total_duties,
        "total_load_hours": round(total_hours, 1),
        "workload_status": status,
        "available_slots": available_slots,
        "can_take_extra": can_take_extra,
        "remaining_capacity": round(remaining_capacity, 1)
    }

def get_department_workload_summary(
    db: Session,
    department: Optional[str] = None,
    academic_week: Optional[int] = None
) -> Dict[str, Any]:
    """Generates complete workload analytics for HOD dashboard & reports."""
    faculty_query = db.query(FacultyProfile).filter(FacultyProfile.is_active == True)
    if department:
        faculty_query = faculty_query.filter(FacultyProfile.department == department)
    all_faculty = faculty_query.all()

    faculty_metrics_list = []
    total_lectures_count = 0
    total_duties_count = 0
    total_department_hours = 0.0

    for fac in all_faculty:
        sched_query = db.query(Schedule).filter(
            Schedule.faculty_id == fac.id,
            Schedule.status != "cancelled"
        )
        if academic_week:
            sched_query = sched_query.filter(Schedule.academic_week == academic_week)
        schedules = sched_query.all()

        metrics = calculate_faculty_metrics(fac, schedules)
        faculty_metrics_list.append(metrics)
        total_lectures_count += metrics["weekly_lectures"]
        total_duties_count += metrics["assigned_duties"]
        total_department_hours += metrics["total_load_hours"]

    # Sort faculty by total load
    sorted_by_load = sorted(faculty_metrics_list, key=lambda x: x["total_load_hours"], reverse=True)

    highest_load_faculty = sorted_by_load[0] if sorted_by_load else None
    lowest_load_faculty = sorted_by_load[-1] if sorted_by_load else None

    # Available faculty: sorted by lowest load and high remaining capacity
    available_faculty = [f for f in sorted_by_load if f["can_take_extra"]]
    available_faculty.sort(key=lambda x: x["remaining_capacity"], reverse=True)

    # Status counts
    high_count = sum(1 for f in faculty_metrics_list if f["workload_status"] == "High")
    balanced_count = sum(1 for f in faculty_metrics_list if f["workload_status"] == "Balanced")
    low_count = sum(1 for f in faculty_metrics_list if f["workload_status"] == "Low")

    faculty_count = len(faculty_metrics_list)
    average_teaching_load = round(total_department_hours / faculty_count, 1) if faculty_count > 0 else 0.0

    return {
        "total_faculty": faculty_count,
        "total_lectures_scheduled": total_lectures_count,
        "total_duties_assigned": total_duties_count,
        "total_department_hours": round(total_department_hours, 1),
        "average_teaching_load": average_teaching_load,
        "workload_breakdown": {
            "high": high_count,
            "balanced": balanced_count,
            "low": low_count
        },
        "highest_load_faculty": highest_load_faculty,
        "lowest_load_faculty": lowest_load_faculty,
        "available_faculty_count": len(available_faculty),
        "available_faculty": available_faculty,
        "faculty_list": sorted_by_load
    }
