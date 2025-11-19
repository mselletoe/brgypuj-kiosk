"""
================================================================================
File: schemas.py
...
"""

from pydantic import BaseModel, EmailStr
from typing import Optional

# ==============================================================================
# Schema: Resident
# ==============================================================================

class ResidentSimple(BaseModel):
    """A simplified resident model for dropdown lists."""
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str] = None

    class Config:
        from_attributes = True

# ==============================================================================
# Schema: BrgyStaff (Admin Auth)
# ==============================================================================

class StaffCreate(BaseModel):
    """Schema for creating a new staff account."""
    resident_id: int  # <-- Changed back
    email: EmailStr
    password: str
    role: str           # <-- We'll send 'Admin' from the frontend

class StaffDisplay(BaseModel):
    """Schema for displaying staff information safely (no password)."""
    id: int
    resident_id: int # <-- No longer optional
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# ==============================================================================
# Schema: Authentication
# ==============================================================================

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"