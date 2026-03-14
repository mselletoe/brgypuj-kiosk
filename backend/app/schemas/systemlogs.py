"""
System Log Schemas
------------------
Pydantic models for validating and serializing system log data.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.systemlogs import LogSource, LogLevel, LogCategory


# ── Internal schema used by log_action() service ──────────────────────────────

class SystemLogCreate(BaseModel):
    actor_id: Optional[int] = None
    actor_name: Optional[str] = None
    actor_role: Optional[str] = None

    action: str
    category: LogCategory = LogCategory.SYSTEM
    level: LogLevel = LogLevel.INFO
    source: LogSource = LogSource.SYSTEM

    target_type: Optional[str] = None
    target_id: Optional[int] = None
    details: Optional[str] = None

    ip_address: Optional[str] = None
    endpoint: Optional[str] = None
    http_method: Optional[str] = None
    status_code: Optional[int] = None


# ── Response schema returned to admin dashboard ────────────────────────────────

class SystemLogRead(BaseModel):
    id: int
    actor_id: Optional[int]
    actor_name: Optional[str]
    actor_role: Optional[str]

    action: str
    category: LogCategory
    level: LogLevel
    source: LogSource

    target_type: Optional[str]
    target_id: Optional[int]
    details: Optional[str]

    ip_address: Optional[str]
    endpoint: Optional[str]
    http_method: Optional[str]
    status_code: Optional[int]

    created_at: datetime

    model_config = {"from_attributes": True}


# ── Paginated response wrapper ─────────────────────────────────────────────────

class SystemLogListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    results: list[SystemLogRead]