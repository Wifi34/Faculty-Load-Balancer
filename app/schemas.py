from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    email: str
    full_name: str
    faculty_id: Optional[int] = None

    class Config:
        from_attributes = True

# Faculty Schemas
class FacultyCreate(BaseModel):
    faculty_code: str
    name: str
    department: str = "Computer Science & Engineering"
    designation: str
    email: EmailStr
    phone: Optional[str] = None
    cabin_room: Optional[str] = None
    subjects_taught: Optional[str] = None
    weekly_lecture_limit: int = 16
    max_duties_limit: int = 6
    is_active: bool = True

class FacultyUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    cabin_room: Optional[str] = None
    subjects_taught: Optional[str] = None
    weekly_lecture_limit: Optional[int] = None
    max_duties_limit: Optional[int] = None
    is_active: Optional[bool] = None

class FacultyResponse(BaseModel):
    id: int
    faculty_code: str
    name: str
    department: str
    designation: str
    email: str
    phone: Optional[str] = None
    cabin_room: Optional[str] = None
    subjects_taught: Optional[str] = None
    weekly_lecture_limit: int
    max_duties_limit: int
    is_active: bool
    created_at: datetime
    # Computed metrics
    weekly_lectures: int = 0
    assigned_duties: int = 0
    total_load_hours: float = 0.0
    workload_status: str = "Balanced"  # "High", "Balanced", "Low"
    available_slots: int = 0

    class Config:
        from_attributes = True

# Schedule & Duty Schemas
class ScheduleCreate(BaseModel):
    schedule_type: str  # regular_lecture, substitute_lecture, exam_duty, lab_duty, college_duty
    faculty_id: int
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    classroom_id: Optional[int] = None
    day_of_week: str  # Monday - Saturday
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    duration_hours: Optional[float] = None
    academic_week: Optional[int] = 1
    duty_title: Optional[str] = None
    instructions: Optional[str] = None
    reminder_minutes: Optional[int] = 15  # 5, 15, 30, 60, 1440

class ScheduleUpdate(BaseModel):
    schedule_type: Optional[str] = None
    faculty_id: Optional[int] = None
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    classroom_id: Optional[int] = None
    day_of_week: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    duty_title: Optional[str] = None
    instructions: Optional[str] = None
    status: Optional[str] = None

class ScheduleResponse(BaseModel):
    id: int
    schedule_type: str
    faculty_id: int
    subject_id: Optional[int] = None
    class_id: Optional[int] = None
    classroom_id: Optional[int] = None
    day_of_week: str
    date: str
    start_time: str
    end_time: str
    duration_hours: float
    academic_week: int
    duty_title: Optional[str] = None
    instructions: Optional[str] = None
    assigned_by: str
    status: str
    created_at: datetime
    
    # Associated details
    faculty_name: Optional[str] = None
    faculty_code: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None
    class_name: Optional[str] = None
    classroom_name: Optional[str] = None

    class Config:
        from_attributes = True

# Conflict Check
class ConflictCheckRequest(BaseModel):
    faculty_id: int
    classroom_id: Optional[int] = None
    date: str
    day_of_week: str
    start_time: str
    end_time: str
    exclude_schedule_id: Optional[int] = None

class ConflictCheckResponse(BaseModel):
    has_conflict: bool
    conflict_type: Optional[str] = None  # "faculty", "classroom", "both", None
    message: str
    conflicting_schedules: List[Dict[str, Any]] = []

# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    user_id: int
    schedule_id: Optional[int] = None
    title: str
    message: str
    notification_type: str
    is_read: bool
    reminder_minutes: Optional[int] = None
    channel: str
    created_at: datetime
    schedule_details: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# Reminder Preference Schemas
class ReminderPrefUpdate(BaseModel):
    lead_time_minutes: int
    browser_enabled: bool = True
    email_enabled: bool = True
    notify_on_assignment: bool = True

class ReminderPrefResponse(BaseModel):
    id: int
    user_id: int
    lead_time_minutes: int
    browser_enabled: bool
    email_enabled: bool
    notify_on_assignment: bool
    updated_at: datetime

    class Config:
        from_attributes = True
