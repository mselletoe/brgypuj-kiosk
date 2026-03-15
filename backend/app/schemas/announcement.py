"""
app/schemas/announcement.py

Pydantic schemas for announcements.
Shared across both the admin management router and the kiosk display router.
"""

from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# =================================================================================
# BASE / SHARED
# =================================================================================
class AnnouncementBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: date
    event_time: Optional[str] = Field(None, max_length=32)
    location: str = Field(..., min_length=1, max_length=255)
    is_active: bool = True


# =================================================================================
# CREATE / UPDATE
# =================================================================================
class AnnouncementCreate(AnnouncementBase):
    pass


class AnnouncementUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    event_date: Optional[date] = None
    event_time: Optional[str] = Field(None, max_length=32)
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    is_active: Optional[bool] = None


# =================================================================================
# KIOSK RESPONSES
# =================================================================================
class AnnouncementKioskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    event_date: date
    event_time: Optional[str]
    location: str
    image_base64: Optional[str] 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# ADMIN RESPONSES
# =================================================================================
class AnnouncementAdminOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    event_date: date
    event_time: Optional[str]
    location: str
    is_active: bool
    has_image: bool 
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnnouncementAdminDetail(AnnouncementAdminOut):
    image_base64: Optional[str]