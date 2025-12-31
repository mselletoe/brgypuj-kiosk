from pydantic import BaseModel
from typing import Optional

class GuestLoginResponse(BaseModel):
    mode: str = "guest"

class RFIDLoginRequest(BaseModel):
    rfid_uid: str

class RFIDLoginResponse(BaseModel):
    mode: str = "rfid"
    resident_id: int
    first_name: str
    last_name: str
    has_pin: bool