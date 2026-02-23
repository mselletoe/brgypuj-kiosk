"""
Kiosk Authentication Schemas
---------------------------
Defines the Pydantic models used for data validation, serialization, 
and documentation of the Kiosk authentication endpoints.
"""

from pydantic import BaseModel
from typing import Optional

class GuestLoginResponse(BaseModel):
    """
    Schema for a successful guest session initialization.
    """
    mode: str = "guest"

class RFIDLoginRequest(BaseModel):
    """
    Schema for the incoming RFID authentication request.
    Captured from hardware scanner input.
    """
    rfid_uid: str

class RFIDLoginResponse(BaseModel):
    """
    Schema for the resident profile returned after a successful RFID scan.
    This data is used to populate the Kiosk Header and determine security flow.
    """
    mode: str = "rfid"
    resident_id: int
    first_name: str
    last_name: str
    has_pin: bool

class SetPinRequest(BaseModel):
    """
    Schema for the first-time PIN setup request.
    Called when a resident has the default '0000' sentinel PIN and needs to set a real one.
    """
    resident_id: int
    pin: str
    rfid_uid: str


class VerifyPinRequest(BaseModel):
    """
    Schema for PIN verification during standard login.
    Called when a resident already has a configured (hashed) PIN.
    """
    resident_id: int
    pin: str


class VerifyPinResponse(BaseModel):
    """
    Schema for the PIN verification result.
    The frontend checks response.data.valid to determine login success.
    """
    valid: bool