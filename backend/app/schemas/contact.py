from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ContactInformationUpdate(BaseModel):
    emergency_number: Optional[str] = None
    emergency_desc:   Optional[str] = None
    phone:            Optional[str] = None
    email:            Optional[str] = None
    office_hours:     Optional[str] = None
    address:          Optional[str] = None
    tech_support:     Optional[str] = None

class ContactInformationOut(BaseModel):
    id:               int
    emergency_number: str
    emergency_desc:   str
    phone:            str
    email:            str
    office_hours:     str
    address:          str
    tech_support:     str
    updated_at:       datetime

    class Config:
        from_attributes = True