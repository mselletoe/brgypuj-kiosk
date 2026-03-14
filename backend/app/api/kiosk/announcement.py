"""
Kiosk Announcements API
---------------------------
Handles resident-facing operations for viewing announcements
via the kiosk interface.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.announcement import AnnouncementKioskOut
from app.services.announcement_service import get_active_announcements

router = APIRouter(prefix="/announcements")


# =========================================================
# ANNOUNCEMENT VIEWING
# =========================================================

@router.get(
    "",
    response_model=list[AnnouncementKioskOut]
)
def list_active_announcements(db: Session = Depends(get_db)):
    """
    Retrieves all active announcements for kiosk display.
    Returns announcements ordered by event date (soonest first).
    Includes image data as base64 encoded strings.
    """
    return get_active_announcements(db)