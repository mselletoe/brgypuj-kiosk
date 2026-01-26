from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


# ===== Requests =====

class AdminLoginRequest(BaseModel):
    username: str
    password: str


class AdminCreateRequest(BaseModel):
    resident_id: int
    username: str
    password: str
    role: str = "Admin"


# ===== Responses =====

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminProfileResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)