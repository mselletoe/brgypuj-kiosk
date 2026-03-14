"""
RFID Registration Schemas
--------------------------
Pydantic models for the RFID Registration workflow.
Consumed by the rfid_registration router and service layer.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# =========================================================
# 1. CHECK RFID STATUS
# =========================================================

class RFIDStatusResponse(BaseModel):
    """
    Result of scanning a card on the kiosk.
    is_new=True  → unregistered card; route to admin passcode → Register
    is_new=False → known card; continue to normal resident auth (PIN)
    """
    is_new: bool


# =========================================================
# 2. ADMIN PASSCODE
# =========================================================

class AdminPasscodeRequest(BaseModel):
    """4-digit passcode entered on the kiosk keypad by the barangay admin."""
    passcode: str


class AdminPasscodeResponse(BaseModel):
    """Result of passcode validation."""
    valid: bool


# =========================================================
# 3. APPROVED ID APPLICATIONS
# =========================================================

class ApprovedIDApplication(BaseModel):
    """
    A single row in the Register screen's transaction list.
    Contains everything needed to display the resident details panel.
    """
    transaction_no: str
    document_request_id: int
    resident_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    birthdate: Optional[str] = None       # ISO date string "YYYY-MM-DD"
    address: Optional[str] = None
    requested_at: datetime


# =========================================================
# 4. LINK RFID
# =========================================================

class LinkRFIDRequest(BaseModel):
    """
    Final submission to bind a scanned UID to the selected resident.
    Sent by the Register screen's Submit button.
    """
    rfid_uid: str              # The new card's hardware UID
    resident_id: int           # Applicant resident
    document_request_id: int   # The approved ID Application being fulfilled


class LinkRFIDResponse(BaseModel):
    """Confirmation returned after successful RFID linking."""
    success: bool
    rfid_uid: str
    resident_id: int
    resident_first_name: str
    resident_last_name: str
    transaction_no: str
    linked_at: datetime