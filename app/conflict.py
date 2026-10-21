from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from app.models import Schedule, FacultyProfile, Classroom, AcademicClass, Subject

def time_to_minutes(time_str: str) -> int:
    """Convert 'HH:MM' string to minutes from midnight."""
    try:
        parts = time_str.strip().split(":")
        return int(parts[0]) * 60 + int(parts[1])
    except Exception:
        return 0

def has_time_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
    """Returns True if [start1, end1) overlaps with [start2, end2)."""
    s1, e1 = time_to_minutes(start1), time_to_minutes(end1)
    s2, e2 = time_to_minutes(start2), time_to_minutes(end2)
    return max(s1, s2) < min(e1, e2)

def check_schedule_conflicts(
    db: Session,
    faculty_id: int,
    date: str,
    day_of_week: str,
    start_time: str,
    end_time: str,
    classroom_id: Optional[int] = None,
    class_id: Optional[int] = None,
    exclude_schedule_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Checks if assigning this slot produces:
    1. Faculty Conflict (faculty already busy)
    2. Classroom Conflict (classroom already booked)
    3. Class/Student Group Conflict (students already have another class)
    """
    conflicting_schedules = []
    conflict_types = []
    messages = []

    # 1. Check Faculty Conflict
    faculty_query = db.query(Schedule).filter(
        Schedule.faculty_id == faculty_id,
        Schedule.status != "cancelled",
        (Schedule.date == date) | (Schedule.day_of_week == day_of_week)
    )
    if exclude_schedule_id:
        faculty_query = faculty_query.filter(Schedule.id != exclude_schedule_id)
    
    faculty_schedules = faculty_query.all()
    faculty_obj = db.query(FacultyProfile).filter(FacultyProfile.id == faculty_id).first()
    faculty_name = faculty_obj.name if faculty_obj else f"Faculty #{faculty_id}"

    for sched in faculty_schedules:
        if has_time_overlap(start_time, end_time, sched.start_time, sched.end_time):
            title = sched.duty_title or (sched.subject.name if sched.subject else "Scheduled Duty")
            room = sched.classroom.room_no if sched.classroom else "Designated Room"
            msg = (
                f"Faculty Conflict: {faculty_name} is already assigned to '{title}' "
                f"({sched.schedule_type.replace('_', ' ').title()}) from {sched.start_time} to {sched.end_time} in {room}."
            )
            messages.append(msg)
            conflict_types.append("faculty")
            conflicting_schedules.append({
                "id": sched.id,
                "type": "faculty_conflict",
                "title": title,
                "time": f"{sched.start_time} - {sched.end_time}",
                "location": room,
                "faculty_name": faculty_name
            })
            break  # one primary conflict report is sufficient

    # 2. Check Classroom Conflict (if classroom specified)
    if classroom_id:
        room_query = db.query(Schedule).filter(
            Schedule.classroom_id == classroom_id,
            Schedule.status != "cancelled",
            (Schedule.date == date) | (Schedule.day_of_week == day_of_week)
        )
        if exclude_schedule_id:
            room_query = room_query.filter(Schedule.id != exclude_schedule_id)

        room_schedules = room_query.all()
        room_obj = db.query(Classroom).filter(Classroom.id == classroom_id).first()
        room_no = room_obj.room_no if room_obj else f"Room #{classroom_id}"

        for sched in room_schedules:
            if has_time_overlap(start_time, end_time, sched.start_time, sched.end_time):
                other_faculty = sched.faculty.name if sched.faculty else "Another faculty"
                title = sched.duty_title or (sched.subject.name if sched.subject else "Lecture")
                msg = (
                    f"Classroom Conflict: {room_no} is already occupied by {other_faculty} "
                    f"for '{title}' from {sched.start_time} to {sched.end_time}."
                )
                messages.append(msg)
                conflict_types.append("classroom")
                conflicting_schedules.append({
                    "id": sched.id,
                    "type": "classroom_conflict",
                    "title": title,
                    "time": f"{sched.start_time} - {sched.end_time}",
                    "location": room_no,
                    "faculty_name": other_faculty
                })
                break

    # 3. Check Class/Student Group Conflict (if class specified)
    if class_id:
        class_query = db.query(Schedule).filter(
            Schedule.class_id == class_id,
            Schedule.status != "cancelled",
            (Schedule.date == date) | (Schedule.day_of_week == day_of_week)
        )
        if exclude_schedule_id:
            class_query = class_query.filter(Schedule.id != exclude_schedule_id)

        class_schedules = class_query.all()
        class_obj = db.query(AcademicClass).filter(AcademicClass.id == class_id).first()
        class_name = class_obj.name if class_obj else f"Class #{class_id}"

        for sched in class_schedules:
            if has_time_overlap(start_time, end_time, sched.start_time, sched.end_time):
                other_faculty = sched.faculty.name if sched.faculty else "Faculty"
                title = sched.duty_title or (sched.subject.name if sched.subject else "Lecture")
                msg = (
                    f"Class Timetable Conflict: {class_name} already has '{title}' "
                    f"conducted by {other_faculty} from {sched.start_time} to {sched.end_time}."
                )
                messages.append(msg)
                conflict_types.append("class")
                conflicting_schedules.append({
                    "id": sched.id,
                    "type": "class_conflict",
                    "title": title,
                    "time": f"{sched.start_time} - {sched.end_time}",
                    "location": sched.classroom.room_no if sched.classroom else "",
                    "faculty_name": other_faculty
                })
                break

    has_conflict = len(conflicting_schedules) > 0
    conflict_type_summary = "_and_".join(sorted(list(set(conflict_types)))) if conflict_types else None
    combined_message = "\n".join(messages) if messages else "No schedule conflicts detected. Slot is available."

    return {
        "has_conflict": has_conflict,
        "conflict_type": conflict_type_summary,
        "message": combined_message,
        "conflicting_schedules": conflicting_schedules
    }
