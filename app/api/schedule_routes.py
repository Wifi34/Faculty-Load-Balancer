from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import datetime
from app.database import get_db
from app.models import Schedule, FacultyProfile, Subject, AcademicClass, Classroom, User, AuditLog
from app.schemas import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    ConflictCheckRequest, ConflictCheckResponse
)
from app.auth import get_current_user, require_hod
from app.conflict import check_schedule_conflicts, time_to_minutes
from app.scheduler import create_assignment_notification, check_and_generate_reminders

router = APIRouter(prefix="/api/schedules", tags=["Lecture and Duty Schedules"])

def calculate_duration_hours(start_time: str, end_time: str) -> float:
    s_min = time_to_minutes(start_time)
    e_min = time_to_minutes(end_time)
    diff = max(0, e_min - s_min)
    return round(diff / 60.0, 2)

@router.post("/check-conflict", response_model=ConflictCheckResponse)
def check_conflict(
    payload: ConflictCheckRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Real-time conflict and overlap checker used before assigning or updating a slot."""
    result = check_schedule_conflicts(
        db=db,
        faculty_id=payload.faculty_id,
        date=payload.date,
        day_of_week=payload.day_of_week,
        start_time=payload.start_time,
        end_time=payload.end_time,
        classroom_id=payload.classroom_id,
        exclude_schedule_id=payload.exclude_schedule_id
    )
    return result

@router.get("/")
def get_schedules(
    faculty_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    classroom_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    day_of_week: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    schedule_type: Optional[str] = Query(None),
    academic_week: Optional[int] = Query(None),
    status_filter: Optional[str] = Query("scheduled"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Schedule)

    # Security: If current user is faculty, enforce viewing only their own schedules
    if current_user.role == "faculty":
        query = query.filter(Schedule.faculty_id == current_user.faculty_id)
    elif faculty_id:
        query = query.filter(Schedule.faculty_id == faculty_id)

    if subject_id:
        query = query.filter(Schedule.subject_id == subject_id)
    if classroom_id:
        query = query.filter(Schedule.classroom_id == classroom_id)
    if class_id:
        query = query.filter(Schedule.class_id == class_id)
    if day_of_week:
        query = query.filter(Schedule.day_of_week == day_of_week)
    if date:
        query = query.filter(Schedule.date == date)
    if schedule_type:
        query = query.filter(Schedule.schedule_type == schedule_type)
    if academic_week:
        query = query.filter(Schedule.academic_week == academic_week)
    if status_filter:
        query = query.filter(Schedule.status == status_filter)

    # Order chronologically
    schedules = query.order_by(Schedule.date, Schedule.start_time).all()

    results = []
    for s in schedules:
        fac = s.faculty
        subj = s.subject
        cls = s.target_class
        room = s.classroom

        results.append({
            "id": s.id,
            "schedule_type": s.schedule_type,
            "faculty_id": s.faculty_id,
            "faculty_name": fac.name if fac else None,
            "faculty_code": fac.faculty_code if fac else None,
            "subject_id": s.subject_id,
            "subject_name": subj.name if subj else None,
            "subject_code": subj.code if subj else None,
            "class_id": s.class_id,
            "class_name": cls.name if cls else None,
            "classroom_id": s.classroom_id,
            "classroom_name": room.room_no if room else None,
            "day_of_week": s.day_of_week,
            "date": s.date,
            "start_time": s.start_time,
            "end_time": s.end_time,
            "duration_hours": s.duration_hours,
            "academic_week": s.academic_week,
            "duty_title": s.duty_title or (subj.name if subj else "Duty"),
            "instructions": s.instructions,
            "assigned_by": s.assigned_by,
            "status": s.status,
            "created_at": s.created_at
        })
    return results

@router.get("/timetable")
def get_weekly_timetable(
    faculty_id: Optional[int] = Query(None),
    classroom_id: Optional[int] = Query(None),
    class_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns weekly timetable structured by days (Monday to Saturday)
    specifically designed for the weekly calendar/matrix view.
    """
    query = db.query(Schedule).filter(Schedule.status != "cancelled")

    # Faculty sees ONLY their own timetable
    if current_user.role == "faculty":
        query = query.filter(Schedule.faculty_id == current_user.faculty_id)
    elif faculty_id:
        query = query.filter(Schedule.faculty_id == faculty_id)

    if classroom_id:
        query = query.filter(Schedule.classroom_id == classroom_id)
    if class_id:
        query = query.filter(Schedule.class_id == class_id)
    if subject_id:
        query = query.filter(Schedule.subject_id == subject_id)

    schedules = query.order_by(Schedule.start_time).all()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    timetable = {day: [] for day in days}

    for s in schedules:
        day = s.day_of_week
        if day in timetable:
            timetable[day].append({
                "id": s.id,
                "schedule_type": s.schedule_type,
                "duty_title": s.duty_title or (s.subject.name if s.subject else "Duty"),
                "subject_code": s.subject.code if s.subject else "",
                "subject_name": s.subject.name if s.subject else "",
                "faculty_name": s.faculty.name if s.faculty else "",
                "faculty_id": s.faculty_id,
                "classroom": s.classroom.room_no if s.classroom else "N/A",
                "classroom_id": s.classroom_id,
                "class_name": s.target_class.name if s.target_class else "N/A",
                "start_time": s.start_time,
                "end_time": s.end_time,
                "duration_hours": s.duration_hours,
                "date": s.date,
                "instructions": s.instructions
            })

    return {
        "view_mode": "faculty" if current_user.role == "faculty" else "hod",
        "active_faculty_id": current_user.faculty_id if current_user.role == "faculty" else faculty_id,
        "days": days,
        "timetable": timetable
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_schedule(
    payload: ScheduleCreate,
    force: bool = Query(False, description="Force assignment despite warnings if HOD confirms"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    # 1. Conflict Check
    conflict_result = check_schedule_conflicts(
        db=db,
        faculty_id=payload.faculty_id,
        date=payload.date,
        day_of_week=payload.day_of_week,
        start_time=payload.start_time,
        end_time=payload.end_time,
        classroom_id=payload.classroom_id,
        class_id=payload.class_id
    )

    if conflict_result["has_conflict"] and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Schedule conflict detected!",
                "conflict_details": conflict_result
            }
        )

    # 2. Duration calculation
    duration = payload.duration_hours or calculate_duration_hours(payload.start_time, payload.end_time)

    # 3. Create Schedule record
    new_schedule = Schedule(
        schedule_type=payload.schedule_type,
        faculty_id=payload.faculty_id,
        subject_id=payload.subject_id,
        class_id=payload.class_id,
        classroom_id=payload.classroom_id,
        day_of_week=payload.day_of_week,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        duration_hours=duration,
        academic_week=payload.academic_week or 1,
        duty_title=payload.duty_title,
        instructions=payload.instructions,
        assigned_by=current_user.full_name,
        status="scheduled"
    )
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    # 4. Create immediate notification & trigger reminders
    notif = create_assignment_notification(db, new_schedule, action="assigned")

    # 5. Audit Log
    fac = db.query(FacultyProfile).filter(FacultyProfile.id == payload.faculty_id).first()
    fac_name = fac.name if fac else f"Faculty #{payload.faculty_id}"
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="ASSIGN_DUTY",
        entity_type="Schedule",
        entity_id=new_schedule.id,
        details=f"Assigned {payload.schedule_type} ({new_schedule.duty_title}) to {fac_name} on {new_schedule.date} {new_schedule.start_time}-{new_schedule.end_time}"
    )
    db.add(log)
    db.commit()

    return {
        "message": "Schedule and duty assigned successfully",
        "schedule_id": new_schedule.id,
        "notification_id": notif.id if notif else None
    }

@router.put("/{schedule_id}")
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdate,
    force: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    sched = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")

    target_faculty = payload.faculty_id or sched.faculty_id
    target_date = payload.date or sched.date
    target_day = payload.day_of_week or sched.day_of_week
    target_start = payload.start_time or sched.start_time
    target_end = payload.end_time or sched.end_time
    target_room = payload.classroom_id if payload.classroom_id is not None else sched.classroom_id

    # Conflict check
    conflict_result = check_schedule_conflicts(
        db=db,
        faculty_id=target_faculty,
        date=target_date,
        day_of_week=target_day,
        start_time=target_start,
        end_time=target_end,
        classroom_id=target_room,
        exclude_schedule_id=schedule_id
    )

    if conflict_result["has_conflict"] and not force:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "message": "Update creates a schedule conflict!",
                "conflict_details": conflict_result
            }
        )

    # Apply updates
    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(sched, field, val)

    sched.duration_hours = calculate_duration_hours(sched.start_time, sched.end_time)
    db.commit()
    db.refresh(sched)

    # Notify faculty
    create_assignment_notification(db, sched, action="updated")

    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="UPDATE_SCHEDULE",
        entity_type="Schedule",
        entity_id=sched.id,
        details=f"Updated schedule #{sched.id} ({sched.duty_title})"
    )
    db.add(log)
    db.commit()

    return {"message": "Schedule updated successfully", "schedule_id": sched.id}

@router.delete("/{schedule_id}")
def cancel_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    sched = db.query(Schedule).filter(Schedule.id == schedule_id).first()
    if not sched:
        raise HTTPException(status_code=404, detail="Schedule not found")

    sched.status = "cancelled"
    db.commit()

    # Log
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="CANCEL_SCHEDULE",
        entity_type="Schedule",
        entity_id=sched.id,
        details=f"Cancelled schedule #{sched.id} ({sched.duty_title})"
    )
    db.add(log)
    db.commit()

    return {"message": "Schedule cancelled successfully"}
