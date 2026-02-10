"""
Announcement Schemas
---------------------------
Pydantic models defining the data structures for Announcement management.
These schemas handle data validation for Admin Dashboard operations and 
serialization for Kiosk display.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# ANNOUNCEMENTS (Created by Admin, Viewed by Residents)
# =========================================================

class AnnouncementBase(BaseModel):
    """
    Base attributes for announcement.
    """
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: date
    event_time: Optional[str] = Field(None, max_length=32)
    location: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


class AnnouncementCreate(AnnouncementBase):
    """
    Schema for creating a new announcement (Admin Dashboard).
    Image is handled separately via multipart/form-data upload.
    """
    pass


class AnnouncementUpdate(BaseModel):
    """
    Schema for updating an existing announcement (Admin Dashboard).
    All fields are optional to support partial updates.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = Field(None, max_length=32)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


class AnnouncementKioskOut(BaseModel):
    """
    Schema for Kiosk announcement display.
    Includes all essential information for residents.
    Image is returned as base64 string for easy display.
    """
    id: int
    title: str
    description: Optional[str]
    event_date: date
    event_time: Optional[str]
    location: str
    image_base64: Optional[str]  # Base64 encoded image
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementAdminOut(BaseModel):
    """
    Schema for Admin Dashboard announcement list/detail views.
    Includes management-relevant fields.
    """
    id: int
    title: str
    description: Optional[str]
    event_date: date
    event_time: Optional[str]
    location: str
    is_active: bool
    has_image: bool  # Indicates if announcement has an image
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementAdminDetail(AnnouncementAdminOut):
    """
    Detailed schema for Admin Dashboard single announcement view.
    Includes the image data for editing purposes.
    """
    image_base64: Optional[str]  # Base64 encoded image for editing