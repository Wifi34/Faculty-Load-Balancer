import time
import threading
import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import (
    Schedule, FacultyProfile, User, Notification, ReminderPreference, AuditLog
)

# Flag to control background thread lifecycle
_SCHEDULER_RUNNING = False
_SCHEDULER_THREAD = None

def parse_schedule_datetime(date_str: str, time_str: str) -> datetime.datetime:
    """Parses date 'YYYY-MM-DD' and time 'HH:MM' into a datetime object."""
    try:
        combined = f"{date_str} {time_str}"
        return datetime.datetime.strptime(combined, "%Y-%m-%d %H:%M")
    except Exception:
        return datetime.datetime.utcnow()

def create_assignment_notification(
    db: Session,
    schedule: Schedule,
    action: str = "assigned"
) -> Optional[Notification]:
    """
    Creates an immediate in-app & channel notification when HOD assigns or updates a lecture/duty.
    """
    faculty = db.query(FacultyProfile).filter(FacultyProfile.id == schedule.faculty_id).first()
    if not faculty:
        return None

    user = db.query(User).filter(User.faculty_id == faculty.id).first()
    if not user:
        return None

    duty_name = schedule.duty_title or (schedule.subject.name if schedule.subject else "Duty")
    type_label = schedule.schedule_type.replace('_', ' ').title()
    location = schedule.classroom.room_no if schedule.classroom else "Designated Hall/Lab"

    if action == "assigned":
        title = f"New {type_label} Assigned: {duty_name}"
        msg = (
            f"Dear {faculty.name}, you have been assigned a {type_label} for '{duty_name}' "
            f"on {schedule.day_of_week}, {schedule.date} from {schedule.start_time} to {schedule.end_time} "
            f"at {location}."
        )
    elif action == "updated":
        title = f"Schedule Updated: {duty_name}"
        msg = (
            f"Dear {faculty.name}, your schedule for '{duty_name}' has been updated to "
            f"{schedule.day_of_week}, {schedule.date} ({schedule.start_time} - {schedule.end_time}) "
            f"at {location}."
        )
    else:
        title = f"Schedule Notification: {duty_name}"
        msg = f"Schedule update regarding {duty_name} on {schedule.date}."

    if schedule.instructions:
        msg += f"\nHOD Instructions: {schedule.instructions}"

    pref = db.query(ReminderPreference).filter(ReminderPreference.user_id == user.id).first()
    channels = ["in_app"]
    if pref and pref.browser_enabled:
        channels.append("browser")
    if pref and pref.email_enabled:
        channels.append("email")

    notif = Notification(
        user_id=user.id,
        schedule_id=schedule.id,
        title=title,
        message=msg,
        notification_type="assignment",
        is_read=False,
        channel=", ".join(channels),
        created_at=datetime.datetime.utcnow()
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)

    # Log to audit table
    log = AuditLog(
        user_id=user.id,
        username=user.username,
        action="NOTIFICATION_SENT",
        entity_type="Notification",
        entity_id=notif.id,
        details=f"Sent {action} notification for schedule #{schedule.id} ({duty_name}) to {faculty.name}"
    )
    db.add(log)
    db.commit()

    return notif

def check_and_generate_reminders(db: Session):
    """
    Scans upcoming schedules and creates automated reminder notifications
    based on faculty/college reminder preferences.
    """
    now = datetime.datetime.now()
    # Check all scheduled events in the next 48 hours and today
    schedules = db.query(Schedule).filter(Schedule.status == "scheduled").all()

    for sched in schedules:
        faculty = db.query(FacultyProfile).filter(FacultyProfile.id == sched.faculty_id).first()
        if not faculty:
            continue
        user = db.query(User).filter(User.faculty_id == faculty.id).first()
        if not user:
            continue

        # Get reminder preference
        pref = db.query(ReminderPreference).filter(ReminderPreference.user_id == user.id).first()
        lead_time = pref.lead_time_minutes if pref else 15

        event_dt = parse_schedule_datetime(sched.date, sched.start_time)
        trigger_dt = event_dt - datetime.timedelta(minutes=lead_time)

        # If trigger time has arrived and event is either upcoming or started less than 30 mins ago
        if trigger_dt <= now <= (event_dt + datetime.timedelta(minutes=30)):
            # Check if reminder already exists
            existing_reminder = db.query(Notification).filter(
                Notification.schedule_id == sched.id,
                Notification.user_id == user.id,
                Notification.notification_type == "reminder",
                Notification.reminder_minutes == lead_time
            ).first()

            if not existing_reminder:
                duty_name = sched.duty_title or (sched.subject.name if sched.subject else "Upcoming Lecture")
                location = sched.classroom.room_no if sched.classroom else "Designated Room"
                time_display = f"{sched.start_time} - {sched.end_time}"

                time_str = f"{lead_time} minutes" if lead_time < 60 else (f"{lead_time // 60} hour(s)" if lead_time < 1440 else "1 day")
                title = f"⏰ Upcoming Reminder: {duty_name} in {time_str}"
                msg = (
                    f"Reminder for {faculty.name}:\n"
                    f"Event: {duty_name} ({sched.schedule_type.replace('_', ' ').title()})\n"
                    f"Date: {sched.date} ({sched.day_of_week})\n"
                    f"Time: {time_display}\n"
                    f"Location: {location}\n"
                    f"Instructions: {sched.instructions or 'None'}"
                )

                channels = ["in_app"]
                if pref and pref.browser_enabled:
                    channels.append("browser")
                if pref and pref.email_enabled:
                    channels.append("email_simulated")

                new_reminder = Notification(
                    user_id=user.id,
                    schedule_id=sched.id,
                    title=title,
                    message=msg,
                    notification_type="reminder",
                    reminder_minutes=lead_time,
                    channel=", ".join(channels),
                    is_read=False,
                    created_at=datetime.datetime.utcnow()
                )
                db.add(new_reminder)

                audit = AuditLog(
                    user_id=user.id,
                    username=user.username,
                    action="AUTO_REMINDER_DISPATCHED",
                    entity_type="Notification",
                    details=f"Automated reminder generated for {faculty.name}: {duty_name} at {time_display} via {new_reminder.channel}"
                )
                db.add(audit)
                db.commit()

def background_scheduler_loop():
    """Background loop that runs check_and_generate_reminders every 30 seconds."""
    global _SCHEDULER_RUNNING
    while _SCHEDULER_RUNNING:
        try:
            db = SessionLocal()
            try:
                check_and_generate_reminders(db)
            finally:
                db.close()
        except Exception as e:
            print(f"[Scheduler Exception]: {e}")
        time.sleep(30)

def start_background_scheduler():
    global _SCHEDULER_RUNNING, _SCHEDULER_THREAD
    if not _SCHEDULER_RUNNING:
        _SCHEDULER_RUNNING = True
        _SCHEDULER_THREAD = threading.Thread(target=background_scheduler_loop, daemon=True)
        _SCHEDULER_THREAD.start()
        print("[FacultyLoadScheduler] Background reminder scheduler service started.")

def stop_background_scheduler():
    global _SCHEDULER_RUNNING
    _SCHEDULER_RUNNING = False
