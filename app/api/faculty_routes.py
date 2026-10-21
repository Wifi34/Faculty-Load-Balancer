from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import FacultyProfile, User, Schedule, ReminderPreference, AuditLog
from app.schemas import FacultyCreate, FacultyUpdate, FacultyResponse
from app.auth import get_current_user, require_hod
from app.workload import calculate_faculty_metrics, get_department_workload_summary
from app.auth import hash_password

router = APIRouter(prefix="/api/faculty", tags=["Faculty Management"])

@router.get("/", response_model=List[FacultyResponse])
def get_all_faculty(
    q: Optional[str] = Query(None, description="Search by name, code or designation"),
    department: Optional[str] = Query(None, description="Filter by department"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(FacultyProfile).filter(FacultyProfile.is_active == True)
    if department:
        query = query.filter(FacultyProfile.department == department)
    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            (FacultyProfile.name.ilike(search_pattern)) |
            (FacultyProfile.faculty_code.ilike(search_pattern)) |
            (FacultyProfile.designation.ilike(search_pattern)) |
            (FacultyProfile.subjects_taught.ilike(search_pattern))
        )

    faculty_list = query.all()
    results = []

    for fac in faculty_list:
        schedules = db.query(Schedule).filter(
            Schedule.faculty_id == fac.id,
            Schedule.status != "cancelled"
        ).all()
        metrics = calculate_faculty_metrics(fac, schedules)
        results.append({
            "id": fac.id,
            "faculty_code": fac.faculty_code,
            "name": fac.name,
            "department": fac.department,
            "designation": fac.designation,
            "email": fac.email,
            "phone": fac.phone,
            "cabin_room": fac.cabin_room,
            "subjects_taught": fac.subjects_taught,
            "weekly_lecture_limit": fac.weekly_lecture_limit,
            "max_duties_limit": fac.max_duties_limit,
            "is_active": fac.is_active,
            "created_at": fac.created_at,
            "weekly_lectures": metrics["weekly_lectures"],
            "assigned_duties": metrics["assigned_duties"],
            "total_load_hours": metrics["total_load_hours"],
            "workload_status": metrics["workload_status"],
            "available_slots": metrics["available_slots"]
        })

    return results

@router.get("/workload/summary")
def get_workload_summary(
    department: Optional[str] = None,
    academic_week: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Provides departmental workload metrics, top loaded/available faculty, charts data."""
    return get_department_workload_summary(db, department=department, academic_week=academic_week)

@router.get("/{faculty_id}")
def get_faculty_by_id(
    faculty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Role-based protection: faculty can only view their own profile, HOD can view any
    if current_user.role != "hod" and current_user.faculty_id != faculty_id:
        raise HTTPException(status_code=403, detail="Unauthorized access to another faculty profile")

    fac = db.query(FacultyProfile).filter(FacultyProfile.id == faculty_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    schedules = db.query(Schedule).filter(
        Schedule.faculty_id == fac.id,
        Schedule.status != "cancelled"
    ).all()
    metrics = calculate_faculty_metrics(fac, schedules)

    return {
        "faculty": fac,
        "metrics": metrics,
        "schedules_count": len(schedules)
    }

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_faculty(
    payload: FacultyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    # Check duplicate code or email
    existing_code = db.query(FacultyProfile).filter(FacultyProfile.faculty_code == payload.faculty_code).first()
    if existing_code:
        raise HTTPException(status_code=400, detail="Faculty code already exists")

    existing_email = db.query(FacultyProfile).filter(FacultyProfile.email == payload.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_faculty = FacultyProfile(
        faculty_code=payload.faculty_code,
        name=payload.name,
        department=payload.department,
        designation=payload.designation,
        email=payload.email,
        phone=payload.phone,
        cabin_room=payload.cabin_room,
        subjects_taught=payload.subjects_taught,
        weekly_lecture_limit=payload.weekly_lecture_limit,
        max_duties_limit=payload.max_duties_limit,
        is_active=payload.is_active
    )
    db.add(new_faculty)
    db.commit()
    db.refresh(new_faculty)

    # Automatically create user login account
    default_username = payload.faculty_code.lower().replace("-", "_")
    new_user = User(
        username=default_username,
        password_hash=hash_password("faculty123"),
        role="faculty",
        email=payload.email,
        full_name=payload.name,
        faculty_id=new_faculty.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Default reminder preferences
    db.add(ReminderPreference(user_id=new_user.id, lead_time_minutes=15, browser_enabled=True, email_enabled=True))
    db.commit()

    # Log action
    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="CREATE_FACULTY",
        entity_type="FacultyProfile",
        entity_id=new_faculty.id,
        details=f"Created faculty profile for {new_faculty.name} ({new_faculty.faculty_code}) with login '{default_username}'"
    )
    db.add(log)
    db.commit()

    return {
        "message": f"Faculty profile for {new_faculty.name} created successfully",
        "faculty_id": new_faculty.id,
        "default_username": default_username,
        "default_password": "faculty123"
    }

@router.put("/{faculty_id}")
def update_faculty(
    faculty_id: int,
    payload: FacultyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    fac = db.query(FacultyProfile).filter(FacultyProfile.id == faculty_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(fac, field, val)

    # If name changed, update user account full_name
    if "name" in update_data:
        linked_user = db.query(User).filter(User.faculty_id == fac.id).first()
        if linked_user:
            linked_user.full_name = payload.name

    db.commit()
    db.refresh(fac)

    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="UPDATE_FACULTY",
        entity_type="FacultyProfile",
        entity_id=fac.id,
        details=f"Updated details for faculty {fac.name}"
    )
    db.add(log)
    db.commit()

    return {"message": "Faculty profile updated successfully", "faculty": fac}

@router.delete("/{faculty_id}")
def delete_faculty(
    faculty_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    fac = db.query(FacultyProfile).filter(FacultyProfile.id == faculty_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Faculty member not found")

    fac_name = fac.name
    fac.is_active = False  # Soft delete
    db.commit()

    log = AuditLog(
        user_id=current_user.id,
        username=current_user.username,
        action="DEACTIVATE_FACULTY",
        entity_type="FacultyProfile",
        entity_id=faculty_id,
        details=f"Deactivated faculty {fac_name}"
    )
    db.add(log)
    db.commit()

    return {"message": f"Faculty profile for {fac_name} deactivated successfully"}
