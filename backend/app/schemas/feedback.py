from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FeedbackBase(BaseModel):
    category: str = Field(..., pattern="^(Service Quality|Interface Design|System Speed|Accessibility|General Experience)$")
    rating: int = Field(..., ge=1, le=5)
    additional_comments: Optional[str] = None


class FeedbackCreate(FeedbackBase):
    resident_id: Optional[int] = None


class FeedbackKioskResponse(BaseModel):
    message: str = "Thank you for your feedback!"


class FeedbackAdminOut(BaseModel):
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