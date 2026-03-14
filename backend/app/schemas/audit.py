from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class AuditLogBase(BaseModel):
    action: str
    details: Optional[str] = None
    entity_type: Optional[str] = None

class AuditLogCreate(AuditLogBase):
    admin_id: Optional[int] = None

class AuditLogOut(AuditLogBase):
    id: int
    admin_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)