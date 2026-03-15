"""
app/services/announcement_service.py

Service layer for announcement management.
Handles business logic for both admin CRUD operations
and kiosk display functionality.
"""

import base64
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from app.models.announcement import Announcement
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementUpdate
)


# =================================================================================
# INTERNAL HELPERS
# =================================================================================

def _get_announcement(db: Session, announcement_id: int) -> Optional[Announcement]:
    return db.query(Announcement).filter(Announcement.id == announcement_id).first()


def _encode_image_to_base64(image_data: bytes) -> str:
    return base64.b64encode(image_data).decode('utf-8')


def _format_announcement_for_kiosk(announcement: Announcement) -> dict:
    return {
        "id": announcement.id,
        "title": announcement.title,
        "description": announcement.description,
        "event_date": announcement.event_date,
        "event_time": announcement.event_time,
        "location": announcement.location,
        "image_base64": _encode_image_to_base64(announcement.image) if announcement.image else None,
        "created_at": announcement.created_at,
    }


def _format_announcement_for_admin(announcement: Announcement) -> dict:
    return {
        "id": announcement.id,
        "title": announcement.title,
        "description": announcement.description,
        "event_date": announcement.event_date,
        "event_time": announcement.event_time,
        "location": announcement.location,
        "is_active": announcement.is_active,
        "has_image": announcement.image is not None,
        "created_at": announcement.created_at,
    }


def _format_announcement_detail_for_admin(announcement: Announcement) -> dict:
    base_data = _format_announcement_for_admin(announcement)
    base_data["image_base64"] = _encode_image_to_base64(announcement.image) if announcement.image else None
    return base_data


# =================================================================================
# KIOSK
# =================================================================================
def get_active_announcements(db: Session) -> list[dict]:

    announcements = (
        db.query(Announcement)
        .filter(Announcement.is_active == True)
        .order_by(Announcement.event_date.asc())
        .all()
    )
    
    return [_format_announcement_for_kiosk(a) for a in announcements]


# =================================================================================
# ADMIN
# =================================================================================
def get_all_announcements(db: Session) -> list[dict]:
    announcements = (
        db.query(Announcement)
        .order_by(Announcement.created_at.desc())
        .all()
    )
    
    return [_format_announcement_for_admin(a) for a in announcements]


def get_announcement_by_id(db: Session, announcement_id: int) -> dict:
    announcement = _get_announcement(db, announcement_id)
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    return _format_announcement_detail_for_admin(announcement)


def create_announcement(
    db: Session,
    payload: AnnouncementCreate,
    image_file: Optional[UploadFile] = None
) -> dict:
    image_data = None
    if image_file:
        image_data = image_file.file.read()
    
    announcement = Announcement(
        title=payload.title,
        description=payload.description,
        event_date=payload.event_date,
        event_time=payload.event_time,
        location=payload.location,
        is_active=payload.is_active,
        image=image_data
    )
    
    db.add(announcement)
    db.commit()
    db.refresh(announcement)
    
    return _format_announcement_detail_for_admin(announcement)


def update_announcement(
    db: Session,
    announcement_id: int,
    payload: AnnouncementUpdate,
    image_file: Optional[UploadFile] = None,
    remove_image: bool = False
) -> dict:
    announcement = _get_announcement(db, announcement_id)
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(announcement, field, value)
    
    if remove_image:
        announcement.image = None
    elif image_file:
        announcement.image = image_file.file.read()
    
    db.commit()
    db.refresh(announcement)
    
    return _format_announcement_detail_for_admin(announcement)


def delete_announcement(db: Session, announcement_id: int) -> bool:
    announcement = _get_announcement(db, announcement_id)
    
    if not announcement:
        return False
    
    db.delete(announcement)
    db.commit()
    return True


def bulk_delete_announcements(db: Session, ids: list[int]) -> int:
    count = db.query(Announcement).filter(Announcement.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count


def toggle_announcement_status(db: Session, announcement_id: int) -> dict:
    announcement = _get_announcement(db, announcement_id)
    
    if not announcement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Announcement not found"
        )
    
    announcement.is_active = not announcement.is_active
    db.commit()
    db.refresh(announcement)
    
    return _format_announcement_for_admin(announcement)