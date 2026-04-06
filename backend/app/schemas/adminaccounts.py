from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class AdminAccountListItem(BaseModel):
    id: int
    username: str
    full_name: str
    position: Optional[str] = None
    system_role: str      
    is_active: bool
    has_photo: bool
    created_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminSetStatusRequest(BaseModel):
    is_active: bool


class AdminSetStatusResponse(BaseModel):
    id: int
    is_active: bool
    detail: str


class AdminSetRoleRequest(BaseModel):
    system_role: str    


class AdminSetRoleResponse(BaseModel):
    id: int
    system_role: str
    detail: str


class AdminDeleteResponse(BaseModel):
    detail: str