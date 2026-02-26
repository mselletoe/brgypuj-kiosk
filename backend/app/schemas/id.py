"""
ID Services Schemas
-------------------
Pydantic models for the three ID Service workflows:
  1. Apply for ID          (kiosk + guest)
  2. Change Passcode / PIN (logged-in residents only)
  3. Report Lost Card      (kiosk + guest)

These schemas live alongside the other kiosk schemas and are consumed by
the ID Services router and service layer.
"""

from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


# =========================================================
# SHARED / UTILITY
# =========================================================

class ResidentSearchResult(BaseModel):
    """
    Minimal resident info returned when a user searches by name.
    Used by both Apply-for-ID and Report-Lost-Card flows.
    """
    resident_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    has_rfid: bool            # True if an active RFID is currently linked


# =========================================================
# 1. APPLY FOR ID
# =========================================================

class IDApplicationRequest(BaseModel):
    """
    Submitted after the resident selects their name and passes
    the birthdate identity check.

    Available to both guest and authenticated (RFID) sessions.
    The rfid_uid field is set by the frontend from the active session;
    it is None when the request comes from a guest user.
    The photo field is a base64-encoded PNG string captured from the kiosk camera.

    resident_id       — the logged-in user's ID (None for guest sessions).
    applicant_resident_id — the resident selected via the form ("Request for").
    """
    resident_id: Optional[int] = None       # logged-in user; None → guest session
    applicant_resident_id: int              # the resident the ID is being applied for
    rfid_uid: Optional[str] = None          # None → guest session
    photo: Optional[str] = None             # base64 PNG, saved to residents.photo


class BirthdateVerifyRequest(BaseModel):
    """
    Step 1 of the Apply-for-ID flow: verify identity using birthdate.
    """
    resident_id: int
    birthdate: date


class BirthdateVerifyResponse(BaseModel):
    """Returned after birthdate check."""
    verified: bool


class IDApplicationResponse(BaseModel):
    """
    Confirmation returned after a successful ID application.
    The transaction appears in the admin Document Requests dashboard.
    """
    transaction_no: str
    resident_first_name: str
    resident_last_name: str
    requested_at: datetime


# =========================================================
# 2. CHANGE PASSCODE / PIN
# =========================================================

class ChangePinRequest(BaseModel):
    """
    Requires the resident's current PIN for verification before
    committing the new one.  Only available to authenticated sessions.
    """
    resident_id: int
    current_pin: str
    new_pin: str


class ChangePinResponse(BaseModel):
    success: bool
    message: str


# =========================================================
# 3. REPORT LOST CARD
# =========================================================

class ReportLostCardVerifyRequest(BaseModel):
    """
    Step 1 of the Report-Lost-Card flow.
    The resident selects their name; we return whether they have an active RFID
    so the frontend can decide whether the "Submit Report" button is clickable.
    """
    resident_id: int


class ReportLostCardVerifyResponse(BaseModel):
    resident_id: int
    first_name: str
    last_name: str
    rfid_uid: Optional[str]    # The active UID, or None if no card linked
    has_rfid: bool


class ReportLostCardRequest(BaseModel):
    """
    Final submission for a lost-card report.
    Pin verification happens server-side; submitting deactivates the linked RFID.

    rfid_uid is nullable to match guest path — the API will reject it gracefully
    if no RFID is found on the resident anyway.
    """
    resident_id: int
    pin: str                   # Current PIN for identity confirmation
    rfid_uid: Optional[str] = None          # None → guest session (informational only)


class ReportLostCardResponse(BaseModel):
    """
    Confirms submission. The report appears in the admin Reports dashboard.
    """
    report_id: int
    resident_first_name: str
    resident_last_name: str
    rfid_uid: Optional[str]    # The UID that was deactivated
    reported_at: datetime


# =========================================================
# ADMIN DASHBOARD — ID APPLICATION DISPLAY
# =========================================================

class IDApplicationAdminOut(BaseModel):
    """
    Row data for the admin Document Requests table when filtering
    by the special 'ID Application' document type.
    """
    id: int
    transaction_no: str
    resident_id: Optional[int]
    resident_first_name: Optional[str]
    resident_last_name: Optional[str]
    resident_rfid: str          # "Guest Mode" or the active RFID UID
    requested_at: datetime
    status: str
    payment_status: str


# =========================================================
# ADMIN DASHBOARD — RFID REPORT DISPLAY
# =========================================================

class RFIDReportAdminOut(BaseModel):
    """
    Row data for the admin Reports page.
    """
    id: int
    resident_id: Optional[int]
    resident_first_name: Optional[str]
    resident_last_name: Optional[str]
    rfid_uid: Optional[str]     # The UID that was reported lost; "Guest Mode" if no session
    status: str
    reported_at: datetime