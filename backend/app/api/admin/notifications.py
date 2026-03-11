from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.notification import NotificationOut
from app.services.notification_service import (
    get_all_notifications,
    mark_read,
    mark_many_read,
    delete_many,
)

router = APIRouter(prefix="/notifications")

@router.get("", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db)):
    """Fetch all notifications ordered by newest first."""
    return get_all_notifications(db)

@router.patch("/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    mark_read(db, notification_id)
    return {"detail": "Marked as read"}

@router.post("/mark-read")
def bulk_mark_read(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    count = mark_many_read(db, ids)
    return {"detail": f"{count} notifications marked as read"}

@router.post("/bulk-delete")
def bulk_delete_notifications(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    count = delete_many(db, ids)
    return {"detail": f"{count} notifications deleted"}