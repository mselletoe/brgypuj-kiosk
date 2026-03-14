"""
Kiosk Authentication Schemas
---------------------------
Defines the Pydantic models used for data validation, serialization,
and documentation of the Kiosk authentication endpoints.

ADDED:
- VerifyPinResponse now includes optional attempts_left for wrong-PIN feedback.
- LockoutDetail for structured 423 error bodies (used by the frontend).
"""

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
    middle_name: Optional[str] = None
    last_name: str
    address: Optional[str] = None
    has_pin: bool


class SetPinRequest(BaseModel):
    resident_id: int
    pin: str
    rfid_uid: str


class VerifyPinRequest(BaseModel):
    resident_id: int
    pin: str


class VerifyPinResponse(BaseModel):
    """
    valid=True  → login granted, counters reset.
    valid=False → wrong PIN; attempts_left tells frontend how many tries remain.
    """
    valid: bool
    attempts_left: Optional[int] = None  # None when valid=True