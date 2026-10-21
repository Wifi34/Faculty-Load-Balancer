import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime, Date
)
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # 'hod' or 'faculty'
    faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"), nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    faculty_profile = relationship("FacultyProfile", back_populates="user_account", uselist=False)
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    reminder_preference = relationship("ReminderPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")


class FacultyProfile(Base):
    __tablename__ = "faculty_profiles"

    id = Column(Integer, primary_key=True, index=True)
    faculty_code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    department = Column(String(100), nullable=False, default="Computer Science & Engineering")
    designation = Column(String(100), nullable=False)  # Professor, Associate Professor, Assistant Professor, Lecturer
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    cabin_room = Column(String(50), nullable=True)
    subjects_taught = Column(Text, nullable=True)  # Comma-separated or JSON list of subjects
    weekly_lecture_limit = Column(Integer, default=16)  # Standard workload threshold (e.g., 16 hrs/week)
    max_duties_limit = Column(Integer, default=6)       # Weekly duties threshold
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_account = relationship("User", back_populates="faculty_profile", uselist=False)
    schedules = relationship("Schedule", back_populates="faculty", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    department = Column(String(100), nullable=False, default="Computer Science & Engineering")
    semester = Column(Integer, default=5)
    credits = Column(Integer, default=4)
    lecture_hours_per_week = Column(Integer, default=4)


class AcademicClass(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # e.g., "B.Tech CSE - 5th Sem - Sec A"
    department = Column(String(100), nullable=False, default="Computer Science & Engineering")
    semester = Column(Integer, default=5)
    section = Column(String(10), default="A")
    academic_year = Column(String(20), default="2026-2027")


class Classroom(Base):
    __tablename__ = "classrooms"

    id = Column(Integer, primary_key=True, index=True)
    room_no = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "LH-201", "Lab-3"
    building = Column(String(100), default="Main Academic Block")
    capacity = Column(Integer, default=60)
    room_type = Column(String(50), default="Lecture Hall")  # Lecture Hall, Computer Lab, Electronics Lab, Seminar Hall


class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    # Types: regular_lecture, substitute_lecture, exam_duty, lab_duty, college_duty
    schedule_type = Column(String(30), nullable=False, default="regular_lecture")
    faculty_id = Column(Integer, ForeignKey("faculty_profiles.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    classroom_id = Column(Integer, ForeignKey("classrooms.id"), nullable=True)
    
    day_of_week = Column(String(20), nullable=False)  # Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    start_time = Column(String(10), nullable=False)  # HH:MM format e.g., "09:00"
    end_time = Column(String(10), nullable=False)  # HH:MM format e.g., "10:00"
    duration_hours = Column(Float, default=1.0)
    
    academic_week = Column(Integer, default=1)
    duty_title = Column(String(200), nullable=True)  # Title for exam, substitute or college duty
    instructions = Column(Text, nullable=True)  # Special instructions from HOD
    assigned_by = Column(String(100), default="HOD")
    status = Column(String(20), default="scheduled")  # scheduled, completed, cancelled
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    faculty = relationship("FacultyProfile", back_populates="schedules")
    subject = relationship("Subject")
    target_class = relationship("AcademicClass")
    classroom = relationship("Classroom")
    notifications = relationship("Notification", back_populates="schedule", cascade="all, delete-orphan")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    schedule_id = Column(Integer, ForeignKey("schedules.id"), nullable=True)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(30), default="assignment")  # assignment, reminder, substitute, cancellation
    is_read = Column(Boolean, default=False)
    reminder_minutes = Column(Integer, nullable=True)  # 5, 15, 30, 60, 1440 (1 day)
    channel = Column(String(50), default="in_app")  # in_app, browser, email
    scheduled_reminder_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="notifications")
    schedule = relationship("Schedule", back_populates="notifications")


class ReminderPreference(Base):
    __tablename__ = "reminder_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    lead_time_minutes = Column(Integer, default=15)  # 5, 15, 30, 60, 1440
    browser_enabled = Column(Boolean, default=True)
    email_enabled = Column(Boolean, default=True)
    notify_on_assignment = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="reminder_preference")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), nullable=True)
    action = Column(String(50), nullable=False)  # CREATE_ASSIGNMENT, UPDATE_SCHEDULE, DELETE_SCHEDULE, UPDATE_FACULTY, etc.
    entity_type = Column(String(50), nullable=False)  # Schedule, Faculty, Reminder, etc.
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
