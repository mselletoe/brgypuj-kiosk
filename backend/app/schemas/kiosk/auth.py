"""
app/schemas/kiosk/auth.py

Pydantic schemas for kiosk authentication flows:
guest sessions, RFID card scanning, and PIN setup/verification.
"""

from pydantic import BaseModel
from typing import Optional


# =================================================================================
# GUEST AUTHENTICATION
# =================================================================================
class GuestLoginResponse(BaseModel):
    """Response returned when a guest session is started."""

    mode: str = "guest"


# =================================================================================
# RFID AUTHENTICATION
# =================================================================================
class RFIDLoginRequest(BaseModel):
    """Request body for POST /rfid. Contains the scanned card's UID."""

    rfid_uid: str


class RFIDLoginResponse(BaseModel):
    """
    Response returned after a successful RFID scan.
    Includes the resident's profile and current address.
    has_pin indicates whether the resident has configured a custom PIN.
    """

    mode: str = "rfid"
    resident_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    address: Optional[str] = None
    has_pin: bool


# =================================================================================
# PIN SETUP
# =================================================================================
class SetPinRequest(BaseModel):
    """
    Request body for POST /set-pin.
    Requires the resident ID and RFID UID to confirm card ownership before setting the PIN.
    """

    resident_id: int
    pin: str
    rfid_uid: str


class VerifyPinRequest(BaseModel):
    """Request body for POST /verify-pin."""

    resident_id: int
    pin: str


class VerifyPinResponse(BaseModel):
    """
    Response returned after a PIN verification attempt.
    On failure, attempts_left indicates how many tries remain before lockout.
    """
    
    valid: bool
    attempts_left: Optional[int] = None