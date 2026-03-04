from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional


# ================================================================
# PROFILE
# ================================================================

class AdminResidentInfo(BaseModel):
    """Resident details embedded in the admin profile — read-only on the frontend."""
    last_name: str
    first_name: str
    middle_name: Optional[str] = None
    suffix: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminProfileResponse(BaseModel):
    """
    Full profile returned to the admin settings page.
    Includes the read-only resident name block and all editable admin fields.
    """
    id: int
    username: str
    position: Optional[str] = None
    system_role: str
    is_active: bool
    has_photo: bool                   # True if a photo blob exists — frontend uses this to show avatar vs placeholder

    resident: AdminResidentInfo

    model_config = ConfigDict(from_attributes=True)


# ================================================================
# UPDATE PROFILE
# ================================================================

class AdminUpdateProfileRequest(BaseModel):
    """
    Fields the admin can edit on the settings page.
    All fields are optional so the frontend can send only what changed.
    username and position are the only editable text fields here;
    password has its own dedicated endpoint.
    """
    username: Optional[str] = None
    position: Optional[str] = None

    @field_validator('username')
    @classmethod
    def username_not_empty(cls, v):
        if v is not None and v.strip() == '':
            raise ValueError('Username cannot be blank')
        return v.strip() if v else v


class AdminUpdateProfileResponse(BaseModel):
    id: int
    username: str
    position: Optional[str] = None
    system_role: str

    model_config = ConfigDict(from_attributes=True)


# ================================================================
# CHANGE PASSWORD
# ================================================================

class AdminChangePasswordRequest(BaseModel):
    """
    Requires the current password for verification before accepting a new one.
    This prevents a stolen session from silently changing the password.
    """
    current_password: str
    new_password: str

    @field_validator('new_password')
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('New password must be at least 8 characters')
        return v


class AdminChangePasswordResponse(BaseModel):
    detail: str = "Password updated successfully"


# ================================================================
# AUTH
# ================================================================

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminCreateRequest(BaseModel):
    resident_id: int
    username: str
    password: str
    position: Optional[str] = None
    system_role: str = "admin"        # default to the least-privileged role


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"