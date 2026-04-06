from datetime import datetime
from pydantic import BaseModel, Field

class FAQBase(BaseModel):
    question: str = Field(..., max_length=255)
    answer: str

class FAQCreate(FAQBase):
    pass

class FAQUpdate(FAQBase):
    pass

class FAQAdminOut(BaseModel):
    id: int
    question: str
    answer: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class FAQKioskOut(BaseModel):
    question: str
    answer: str

    model_config = {
        "from_attributes": True
    }