from pydantic import BaseModel
from datetime import datetime

class NotificationOut(BaseModel):
    id:         int
    type:       str
    msg:        str
    is_read:    bool
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationCreate(BaseModel):
    type: str
    msg:  str