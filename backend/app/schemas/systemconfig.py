"""
System Config Schemas
---------------------
Pydantic models for reading and updating system configuration.
All fields in SystemConfigUpdate are optional — PATCH semantics,
so each tab only sends the fields it manages.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SystemConfigRead(BaseModel):
    id: int

    # General
    brgy_name: Optional[str]
    brgy_subname: Optional[str]
    brgy_logo_path: Optional[str]

    # Security
    rfid_expiry_days: int
    auto_logout_minutes: int
    max_failed_attempts: int
    lockout_minutes: int

    # Preferences
    default_view: str
    maintenance_mode: bool

    # Backup
    backup_schedule: str
    backup_time: Optional[str]
    last_backup_at: Optional[datetime]

    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemConfigUpdate(BaseModel):
    # General
    brgy_name: Optional[str]   = Field(None, max_length=150)
    brgy_subname: Optional[str]   = Field(None, max_length=200)
    brgy_logo_path: Optional[str]   = Field(None, max_length=500)

    # Security
    rfid_expiry_days: Optional[int] = Field(None, ge=1)
    auto_logout_minutes: Optional[int] = Field(None, ge=1)
    max_failed_attempts: Optional[int] = Field(None, ge=1)
    lockout_minutes: Optional[int] = Field(None, ge=1)

    # Preferences
    default_view: Optional[str]  = Field(None, max_length=50)
    maintenance_mode: Optional[bool] = None

    # Backup
    backup_schedule: Optional[str] = Field(None, pattern="^(manual|daily|weekly)$")
    backup_time: Optional[str] = Field(None, pattern="^([01]\\d|2[0-3]):[0-5]\\d$")


class SystemConfigLogoUpdate(BaseModel):
    brgy_logo_path: str