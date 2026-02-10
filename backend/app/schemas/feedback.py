"""
Feedback Services Schemas
---------------------------
Pydantic models defining the data structures for Feedback submissions and management.
These schemas handle data validation for Kiosk submissions and serialization for 
Admin Dashboard management.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# FEEDBACK (Submitted by Residents/Guests, Managed by Admin)
# =========================================================

class FeedbackBase(BaseModel):
    """
    Base attributes for feedback submission.
    """
    category: str = Field(..., pattern="^(Service Quality|Interface Design|System Speed|Accessibility|General Experience)$")
    rating: int = Field(..., ge=1, le=5)
    additional_comments: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    """
    Validation schema for incoming Kiosk feedback submissions.
    Includes the resident_id which can be None for guest submissions.
    """
    resident_id: Optional[int] = None


class FeedbackKioskResponse(BaseModel):
    """
    Immediate feedback confirmation for the Kiosk user.
    """
    message: str = "Thank you for your feedback!"


class FeedbackAdminOut(BaseModel):
    """
    Schema for Admin Dashboard feedback list views.
    Includes resident details if available, otherwise shows "Guest".
    """
    id: int
    category: str
    rating: int
    additional_comments: Optional[str]
    
    resident_id: Optional[int]
    resident_first_name: Optional[str]
    resident_middle_name: Optional[str]
    resident_last_name: Optional[str]
    resident_rfid: Optional[str]
    
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)