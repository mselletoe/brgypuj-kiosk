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