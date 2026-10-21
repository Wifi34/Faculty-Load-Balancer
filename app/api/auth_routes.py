from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, FacultyProfile
from app.schemas import LoginRequest, TokenResponse, UserResponse
from app.auth import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username.strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # Generate JWT
    token_data = {
        "sub": user.username,
        "role": user.role,
        "user_id": user.id,
        "faculty_id": user.faculty_id
    }
    access_token = create_access_token(token_data)

    faculty_info = None
    if user.faculty_id:
        fac = db.query(FacultyProfile).filter(FacultyProfile.id == user.faculty_id).first()
        if fac:
            faculty_info = {
                "id": fac.id,
                "faculty_code": fac.faculty_code,
                "name": fac.name,
                "department": fac.department,
                "designation": fac.designation
            }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "email": user.email,
            "full_name": user.full_name,
            "faculty_id": user.faculty_id,
            "faculty_details": faculty_info
        }
    }

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    faculty_info = None
    if current_user.faculty_id:
        fac = db.query(FacultyProfile).filter(FacultyProfile.id == current_user.faculty_id).first()
        if fac:
            faculty_info = {
                "id": fac.id,
                "faculty_code": fac.faculty_code,
                "name": fac.name,
                "department": fac.department,
                "designation": fac.designation,
                "email": fac.email,
                "cabin_room": fac.cabin_room,
                "subjects_taught": fac.subjects_taught,
                "weekly_lecture_limit": fac.weekly_lecture_limit
            }

    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "faculty_id": current_user.faculty_id,
        "faculty_details": faculty_info
    }

@router.get("/demo-accounts")
def get_demo_accounts():
    """Provides convenient test credentials for testing both HOD and Faculty roles."""
    return [
        {
            "role": "HOD (Admin)",
            "username": "hod_cs",
            "password": "admin123",
            "name": "Dr. Rajesh Sharma",
            "title": "Head of Department (CSE)",
            "description": "Full administrative control, faculty management, duty allocation, reports"
        },
        {
            "role": "Faculty (High Load)",
            "username": "prof_amit",
            "password": "faculty123",
            "name": "Dr. Amit Verma",
            "title": "Associate Professor",
            "description": "18 hrs/week load - view personal timetable, upcoming duties, notifications"
        },
        {
            "role": "Faculty (Balanced)",
            "username": "prof_priya",
            "password": "faculty123",
            "name": "Prof. Priya Patel",
            "title": "Assistant Professor",
            "description": "14 hrs/week balanced load - personal timetable & reminder settings"
        },
        {
            "role": "Faculty (Available/Low Load)",
            "username": "prof_vikram",
            "password": "faculty123",
            "name": "Prof. Vikram Singh",
            "title": "Lecturer",
            "description": "8 hrs/week load - eligible for substitute lectures and exam duties"
        }
    ]
