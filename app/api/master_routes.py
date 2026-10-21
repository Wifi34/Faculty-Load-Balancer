from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import Subject, AcademicClass, Classroom, AuditLog, User
from app.auth import get_current_user, require_hod

router = APIRouter(prefix="/api/master", tags=["Master Data"])

@router.get("/subjects")
def get_subjects(department: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Subject)
    if department:
        query = query.filter(Subject.department == department)
    return query.order_by(Subject.code).all()

@router.get("/classes")
def get_classes(department: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(AcademicClass)
    if department:
        query = query.filter(AcademicClass.department == department)
    return query.order_by(AcademicClass.name).all()

@router.get("/classrooms")
def get_classrooms(db: Session = Depends(get_db)):
    return db.query(Classroom).order_by(Classroom.room_no).all()

@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_hod)
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return logs
