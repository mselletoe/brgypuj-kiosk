"""
app/schemas/admin/auth.py

Pydantic schemas for admin authentication and profile management.
Used for request validation and response serialization across
the admin auth router.
"""

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

# =================================================================================
# ADMIN RESIDENT INFO SHARED
# =================================================================================
class AdminResidentInfo(BaseModel):
    """Minimal resident name info embedded in admin profile responses."""

    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AdminProfileResponse(BaseModel):
    """Full admin profile returned by GET /me and related endpoints."""

    id: int
    username: str
    position: Optional[str] = None
    system_role: str
    is_active: bool
    has_photo: bool
    resident: AdminResidentInfo

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# LOGIN
# =================================================================================
class AdminLoginRequest(BaseModel):
    """Request body for POST /login."""

    username: str
    password: str


class AdminTokenResponse(BaseModel):
    """JWT token envelope returned on successful login."""
    
    access_token: str
    token_type: str = "bearer"


# =================================================================================
# CREATE ACCOUNT
# =================================================================================
class AdminCreateRequest(BaseModel):
    """
    Request body for POST /register.
    Links the new admin account to an existing resident record.
    system_role defaults to 'admin' if not explicitly provided.
    """

    resident_id: int
    username: str
    password: str
    position: Optional[str] = None
    system_role: str = "admin" 
    

# =================================================================================
# UPDATE PROFILE
# =================================================================================
class AdminUpdateProfileRequest(BaseModel):
    """Request body for PATCH /me. All fields are optional — only provided fields are updated."""

    username: Optional[str] = None
    position: Optional[str] = None

    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v):
        """Rejects usernames that are blank or whitespace-only."""
        if v is not None and v.strip() == '':
            raise ValueError('Username cannot be blank')
        return v.strip() if v else v


class AdminUpdateProfileResponse(BaseModel):
    """Trimmed profile snapshot returned after a successful profile update."""

    id: int
    username: str
    position: Optional[str] = None
    system_role: str

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# CHANGE PASSWORD
# =================================================================================
class AdminChangePasswordRequest(BaseModel):
    """Request body for PATCH /me/password. Requires the current password for verification."""

    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def password_min_length(cls, v):
        """Enforces a minimum password length of 8 characters."""
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters')
        return v


class AdminChangePasswordResponse(BaseModel):
    """Confirmation envelope returned after a successful password change."""

    detail: str = "Password updated successfully"


# =================================================================================
# RELINK RESIDENT - SUPERADMIN
# =================================================================================
class AdminRelinkResidentRequest(BaseModel):
    """Request body for PATCH /me/resident. Superadmin-only."""

    resident_id: int