from pydantic import BaseModel
from datetime import date
from typing import Optional

class ResidentBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str]
    suffix: Optional[str]
    gender: str
    birthdate: date
    email: Optional[str]
    phone_number: Optional[str]

class ResidentCreate(ResidentBase):
    pass

class ResidentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]
    suffix: Optional[str]
    gender: str
    birthdate: date
    email: Optional[str]
    phone_number: Optional[str]

    class Config:
        orm_mode = True