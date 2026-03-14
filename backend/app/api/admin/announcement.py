"""
Announcement Administration API
---------------------------
Provides management endpoints for creating, editing, and managing announcements
within the administrative dashboard.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.announcement import (
    AnnouncementCreate,
    AnnouncementUpdate,
    AnnouncementAdminOut,
    AnnouncementAdminDetail
)
from app.services.announcement_service import (
    get_all_announcements,
    get_announcement_by_id,
    create_announcement,
    update_announcement,
    delete_announcement,
    bulk_delete_announcements,
    toggle_announcement_status
)
from datetime import date

router = APIRouter(prefix="/announcements")


# =========================================================
# ANNOUNCEMENT MANAGEMENT
# =========================================================

@router.get(
    "",
    response_model=list[AnnouncementAdminOut]
)
def list_announcements(db: Session = Depends(get_db)):
    """
    Lists all announcements (active and inactive) for administrative management.
    Returns announcements ordered by creation date (newest first).
    """
    return get_all_announcements(db)


@router.get(
    "/{announcement_id}",
    response_model=AnnouncementAdminDetail
)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """
    Retrieves detailed information for a specific announcement.
    Includes full image data for editing purposes.
    """
    return get_announcement_by_id(db, announcement_id)


@router.post(
    "",
    response_model=AnnouncementAdminDetail,
    status_code=status.HTTP_201_CREATED
)
async def create_new_announcement(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    event_date: date = Form(...),
    event_time: Optional[str] = Form(None),
    location: str = Form(...),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Creates a new announcement with optional image upload.
    Uses multipart/form-data to support file upload.
    """
    # Validate image file type if provided
    if image:
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed types: {', '.join(allowed_types)}"
            )
    
    # Create announcement payload
    announcement_data = AnnouncementCreate(
        title=title,
        description=description,
        event_date=event_date,
        event_time=event_time,
        location=location,
        is_active=is_active
    )
    
    return create_announcement(db, announcement_data, image)


@router.put(
    "/{announcement_id}",
    response_model=AnnouncementAdminDetail
)
async def update_existing_announcement(
    announcement_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    event_date: Optional[date] = Form(None),
    event_time: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    remove_image: bool = Form(False),
    db: Session = Depends(get_db)
):
    """
    Updates an existing announcement.
    Supports partial updates and image replacement/removal.
    Set remove_image=true to delete the current image.
    """
    # Validate image file type if provided
    if image:
        allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image type. Allowed types: {', '.join(allowed_types)}"
            )
    
    # Build update payload with only provided fields
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if event_date is not None:
        update_data["event_date"] = event_date
    if event_time is not None:
        update_data["event_time"] = event_time
    if location is not None:
        update_data["location"] = location
    if is_active is not None:
        update_data["is_active"] = is_active
    
    announcement_update = AnnouncementUpdate(**update_data)
    
    return update_announcement(db, announcement_id, announcement_update, image, remove_image)


@router.patch(
    "/{announcement_id}/toggle-status",
    response_model=AnnouncementAdminOut
)
def toggle_status(announcement_id: int, db: Session = Depends(get_db)):
    """
    Toggles the is_active status of an announcement.
    Convenience endpoint for quick activation/deactivation.
    """
    return toggle_announcement_status(db, announcement_id)


@router.delete("/{announcement_id}")
def delete_announcement_record(announcement_id: int, db: Session = Depends(get_db)):
    """
    Deletes a specific announcement record.
    """
    success = delete_announcement(db, announcement_id)
    if not success:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return {"detail": "Announcement deleted"}


@router.post("/bulk-delete")
def bulk_delete_announcement_records(
    ids: list[int] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Bulk delete operation for multiple announcement records.
    Returns count of successfully deleted records.
    """
    deleted_count = bulk_delete_announcements(db, ids)
    return {"detail": f"{deleted_count} announcements deleted"}