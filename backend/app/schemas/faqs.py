from datetime import datetime
from pydantic import BaseModel, Field

# Base schema
class FAQBase(BaseModel):
    question: str = Field(..., max_length=255)
    answer: str

# Schema for Admin Create/Update
class FAQCreate(FAQBase):
    pass

class FAQUpdate(FAQBase):
    pass

# Admin output schema
class FAQAdminOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# Kiosk output schema (similar to AdminOut but only needed fields)
class FAQKioskOut(BaseModel):
    question: str
    answer: str

    model_config = {
        "from_attributes": True
    }