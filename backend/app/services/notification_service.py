"""
app/services/notification_service.py
 
Service layer for in-app notification management.
Handles saving, retrieving, marking as read, and deleting notifications.
"""

from sqlalchemy.orm import Session
from app.models.notification import Notification


def save_notification(db: Session, type: str, msg: str, event: str = "") -> Notification:
    notif = Notification(type=type, msg=msg, event=event)
    db.add(notif)
    db.commit()
    db.refresh(notif)
    return notif


def get_all_notifications(db: Session) -> list[Notification]:
    return db.query(Notification).order_by(Notification.created_at.desc()).all()


def mark_read(db: Session, notification_id: int) -> bool:
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        return False
    notif.is_read = True
    db.commit()
    return True


def mark_many_read(db: Session, ids: list[int]) -> int:
    count = (
        db.query(Notification)
        .filter(Notification.id.in_(ids))
        .update({"is_read": True}, synchronize_session=False)
    )
    db.commit()
    return count


def delete_many(db: Session, ids: list[int]) -> int:
    count = (
        db.query(Notification)
        .filter(Notification.id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return count