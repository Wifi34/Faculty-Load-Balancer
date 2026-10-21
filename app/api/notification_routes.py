from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import datetime
from app.database import get_db
from app.models import Notification, ReminderPreference, User, Schedule
from app.schemas import NotificationResponse, ReminderPrefUpdate, ReminderPrefResponse
from app.auth import get_current_user
from app.scheduler import check_and_generate_reminders

router = APIRouter(prefix="/api/notifications", tags=["Notifications & Reminders"])

@router.get("/")
def get_user_notifications(
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        query = query.filter(Notification.is_read == False)

    notifs = query.order_by(Notification.created_at.desc()).limit(50).all()

    unread_count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()

    results = []
    for n in notifs:
        results.append({
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "is_read": n.is_read,
            "channel": n.channel,
            "reminder_minutes": n.reminder_minutes,
            "schedule_id": n.schedule_id,
            "created_at": n.created_at
        })

    return {
        "unread_count": unread_count,
        "notifications": results
    }

@router.put("/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    notif = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")

    notif.is_read = True
    db.commit()
    return {"message": "Notification marked as read"}

@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"message": "All notifications marked as read"}

@router.get("/preferences", response_model=ReminderPrefResponse)
def get_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(ReminderPreference).filter(ReminderPreference.user_id == current_user.id).first()
    if not pref:
        # Create default
        pref = ReminderPreference(
            user_id=current_user.id,
            lead_time_minutes=15,
            browser_enabled=True,
            email_enabled=True,
            notify_on_assignment=True
        )
        db.add(pref)
        db.commit()
        db.refresh(pref)
    return pref

@router.put("/preferences", response_model=ReminderPrefResponse)
def update_preferences(
    payload: ReminderPrefUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    pref = db.query(ReminderPreference).filter(ReminderPreference.user_id == current_user.id).first()
    if not pref:
        pref = ReminderPreference(user_id=current_user.id)
        db.add(pref)

    pref.lead_time_minutes = payload.lead_time_minutes
    pref.browser_enabled = payload.browser_enabled
    pref.email_enabled = payload.email_enabled
    pref.notify_on_assignment = payload.notify_on_assignment
    pref.updated_at = datetime.datetime.utcnow()

    db.commit()
    db.refresh(pref)
    return pref

@router.post("/trigger-scheduler-now")
def trigger_scheduler(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allows manual scan of upcoming schedules to instantly generate pending reminders."""
    check_and_generate_reminders(db)
    return {"message": "Automated reminder check executed successfully"}

@router.post("/send-test-alert")
def send_test_alert(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sends a live test alert to verify in-app notifications and browser notifications."""
    test_notif = Notification(
        user_id=current_user.id,
        title="🔔 Test Alert: System Notification Active",
        message=f"Hi {current_user.full_name}, your notification channel is working perfectly. Reminders will be triggered automatically.",
        notification_type="reminder",
        reminder_minutes=15,
        channel="in_app, browser",
        is_read=False,
        created_at=datetime.datetime.utcnow()
    )
    db.add(test_notif)
    db.commit()
    return {"message": "Test alert dispatched", "notification_id": test_notif.id}
