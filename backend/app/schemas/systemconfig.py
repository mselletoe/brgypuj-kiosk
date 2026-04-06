from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SystemConfigRead(BaseModel):
    id: int

    brgy_name:    Optional[str]
    brgy_subname: Optional[str]
    has_logo:     bool = False

    rfid_expiry_days:    int
    rfid_reminder_days:  int  
    auto_logout_duration: int
    max_failed_attempts: int
    lockout_minutes:     int

    default_view:     str
    maintenance_mode: bool

    backup_schedule: str
    backup_time:     Optional[str]
    last_backup_at:  Optional[datetime]

    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemConfigUpdate(BaseModel):
    brgy_name:    Optional[str] = Field(None, max_length=150)
    brgy_subname: Optional[str] = Field(None, max_length=200)

    rfid_expiry_days:     Optional[int] = Field(None, ge=1)
    rfid_reminder_days:   Optional[int] = Field(None, ge=1) 
    auto_logout_duration: Optional[int] = Field(None, ge=10)
    max_failed_attempts:  Optional[int] = Field(None, ge=1)
    lockout_minutes:      Optional[int] = Field(None, ge=1)

    default_view:     Optional[str]  = Field(None, max_length=50)
    maintenance_mode: Optional[bool] = None

    backup_schedule: Optional[str] = Field(None, pattern="^(manual|daily|weekly)$")
    backup_time:     Optional[str] = Field(None, pattern="^([01]\\d|2[0-3]):[0-5]\\d$")


class KioskSystemConfigRead(BaseModel):
    brgy_name:            Optional[str]
    brgy_subname:         Optional[str]
    has_logo:             bool = False
    rfid_expiry_days:     int  = 365  
    rfid_reminder_days:   int  = 30  
    auto_logout_duration: int  = 1800
    max_failed_attempts:  int  = 5
    lockout_minutes:      int  = 15
    maintenance_mode:     bool = False
    maintenance_message:  Optional[str] = None

    model_config = {"from_attributes": True}