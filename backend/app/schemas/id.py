"""
ID Services Schemas
-------------------
Pydantic models for the three ID Service workflows:
  1. Apply for ID          (kiosk + guest)
  2. Change Passcode / PIN (logged-in residents only)
  3. Report Lost Card      (kiosk + guest)

MODIFIED:
- IDApplicationRequest now includes `manual_data` (Optional[IDManualFormData])
  for guest sessions or when the resident opts to override DB-fetched values.
- IDFormData documents all template placeholder keys used in the ID docx.
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
    first_name:  str
    middle_name: Optional[str] = None
    last_name:   str
    suffix:      Optional[str] = None
    has_rfid:    bool             # True if an active RFID is currently linked
    has_pending: bool = False     # True if a pending ID application already exists


# =========================================================
# ID TEMPLATE FORM DATA
# =========================================================

class IDManualFormData(BaseModel):
    """
    Manual / guest entry fields for the ID card template.

    All fields are optional — only provided values override the DB-fetched data.
    This is used when:
      a) The session is Guest mode (no resident login), OR
      b) The resident opts to manually edit their info via the checkbox toggle.

    These keys map directly to docx template placeholders:
        {{last_name}}, {{first_name}}, {{middle_name}},
        {{birthdate}}, {{address}}, {{contact_number}}
    """
    last_name:      Optional[str] = None
    first_name:     Optional[str] = None
    middle_name:    Optional[str] = None
    birthdate:      Optional[str] = None   # "YYYY-MM-DD" or formatted string
    address:        Optional[str] = None
    contact_number: Optional[str] = None


# =========================================================
# 1. APPLY FOR ID
# =========================================================

class BirthdateVerifyRequest(BaseModel):
    """Step 1 of the Apply-for-ID flow: verify identity using birthdate."""
    resident_id: int
    birthdate:   date


class BirthdateVerifyResponse(BaseModel):
    """Returned after birthdate check."""
    verified: bool


class IDApplicationRequest(BaseModel):
    """
    Submitted after the resident selects their name and passes
    the birthdate identity check.

    resident_id           — the logged-in user's ID (None for guest sessions).
    applicant_resident_id — the resident selected via "Request for" form field.
    rfid_uid              — None for guest sessions.
    photo                 — base64-encoded PNG from the kiosk camera.
    use_manual_data       — if True, `manual_data` overrides DB-fetched resident info.
    manual_data           — explicit field values (required for guest; optional for RFID).
    """
    resident_id:           Optional[int] = None    # logged-in user; None → guest
    applicant_resident_id: int                     # the resident the ID is for
    rfid_uid:              Optional[str] = None    # None → guest session
    photo:                 Optional[str] = None    # base64 PNG
    use_manual_data:       bool = False            # checkbox: "use manually entered info"
    manual_data:           Optional[IDManualFormData] = None


class IDApplicationResponse(BaseModel):
    """Confirmation returned after a successful ID application."""
    transaction_no:       str
    resident_first_name:  str
    resident_last_name:   str
    requested_at:         datetime


# =========================================================
# 2. CHANGE PASSCODE / PIN
# =========================================================

class ChangePinRequest(BaseModel):
    """
    Requires the resident's current PIN for verification before
    committing the new one. Only available to authenticated sessions.
    """
    resident_id:  int
    current_pin:  str
    new_pin:      str


class ChangePinResponse(BaseModel):
    success: bool
    message: str


# =========================================================
# 3. REPORT LOST CARD
# =========================================================

class ReportLostCardVerifyRequest(BaseModel):
    resident_id: int


class ReportLostCardVerifyResponse(BaseModel):
    resident_id: int
    first_name:  str
    last_name:   str
    rfid_uid:    Optional[str]
    has_rfid:    bool


class ReportLostCardRequest(BaseModel):
    """
    Final submission for a lost-card report.
    PIN verification happens server-side; submitting deactivates the linked RFID
    and the linked BarangayID record.
    """
    resident_id: int
    pin:         str
    rfid_uid:    Optional[str] = None   # None → guest session (informational)


class ReportLostCardResponse(BaseModel):
    report_id:            int
    resident_first_name:  str
    resident_last_name:   str
    rfid_uid:             Optional[str]
    reported_at:          datetime


# =========================================================
# ADMIN DASHBOARD — ID APPLICATION DISPLAY
# =========================================================

class IDApplicationAdminOut(BaseModel):
    id:                   int
    transaction_no:       str
    resident_id:          Optional[int]
    resident_first_name:  Optional[str]
    resident_last_name:   Optional[str]
    resident_rfid:        str              # "Guest Mode" or the active RFID UID
    brgy_id_number:       Optional[str]    # assigned on card release; None until then
    requested_at:         datetime
    status:               str
    payment_status:       str


# =========================================================
# ADMIN DASHBOARD — RFID REPORT DISPLAY
# =========================================================

class RFIDReportAdminOut(BaseModel):
    id:                   int
    resident_id:          Optional[int]
    resident_first_name:  Optional[str]
    resident_last_name:   Optional[str]
    rfid_uid:             Optional[str] = None   # not on model; always None currently
    status:               str
    reported_at:          datetime               # mapped from created_at in service


# =========================================================
# REGISTRATION — LINK RFID RESPONSE (extended)
# =========================================================

class LinkRFIDResponse(BaseModel):
    """
    Extended from registration schema to include brgy_id_number and expiration.
    Returned by registration_service.link_rfid_to_resident.
    """
    success:             bool
    rfid_uid:            str
    resident_id:         int
    resident_first_name: str
    resident_last_name:  str
    transaction_no:      str
    brgy_id_number:      str
    expiration_date:     str     # ISO date string "YYYY-MM-DD"
    linked_at:           datetime


# =========================================================
# VERIFY PIN (used by id-services/verify-pin endpoint)
# =========================================================

class VerifyPinRequest(BaseModel):
    resident_id: int
    pin:         str


class VerifyPinResponse(BaseModel):
    verified: bool