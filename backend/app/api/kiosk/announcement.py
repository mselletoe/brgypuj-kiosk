"""
app/api/kiosk/announcements.py

Router for kiosk-facing announcement display.
Exposes only active announcements to the public kiosk interface.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.announcement import AnnouncementKioskOut
from app.services.announcement_service import get_active_announcements

router = APIRouter(prefix="/announcements")


@router.get( "", response_model=list[AnnouncementKioskOut] )
def list_active_announcements(db: Session = Depends(get_db)):
    """Returns all currently active announcements for kiosk display."""
    return get_active_announcements(db)