"""
ID Services Router
------------------
Exposes the three ID Service workflows as REST endpoints consumed
by the Barangay Kiosk and Admin Dashboard.

Kiosk-facing (guest + RFID sessions):
  POST /id-services/residents/search             — name search for resident selection
  POST /id-services/apply/verify-birthdate       — identity check before applying
  POST /id-services/apply                        — submit ID application
  GET  /id-services/report-lost/info/{rid}       — check if resident has an active card
  POST /id-services/report-lost                  — confirm & submit lost card report

Authenticated kiosk (RFID session only):
  POST /id-services/change-pin                   — change security PIN
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.id import (
    ResidentSearchResult,
    BirthdateVerifyRequest,
    BirthdateVerifyResponse,
    IDApplicationRequest,
    IDApplicationResponse,
    ChangePinRequest,
    ChangePinResponse,
    ReportLostCardVerifyResponse,
    ReportLostCardRequest,
    ReportLostCardResponse,
)
from app.services.id_service import (
    search_residents_by_name,
    verify_resident_birthdate,
    apply_for_id,
    change_pin,
    get_rfid_report_card_info,
    report_lost_card,
)

router = APIRouter(prefix="/id-services")


# =========================================================
# SHARED — RESIDENT SEARCH
# =========================================================

@router.get(
    "/residents/search",
    response_model=list[ResidentSearchResult],
    summary="Search residents by name",
    description=(
        "Returns up to 20 residents whose first or last name matches the query. "
        "Available to both guest and authenticated sessions. "
        "Used by Apply-for-ID and Report-Lost-Card flows."
    ),
)
def search_residents(query: str, db: Session = Depends(get_db)):
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters."
        )
    return search_residents_by_name(db, query.strip())


# =========================================================
# APPLY FOR ID
# =========================================================

@router.post(
    "/apply/verify-birthdate",
    response_model=BirthdateVerifyResponse,
    summary="Verify resident identity via birthdate",
    description=(
        "Step 1 of the Apply-for-ID flow. "
        "Checks if the supplied birthdate matches the resident's record. "
        "The frontend should only proceed to /apply if verified=true."
    ),
)
def verify_birthdate(payload: BirthdateVerifyRequest, db: Session = Depends(get_db)):
    verified = verify_resident_birthdate(db, payload.resident_id, payload.birthdate)
    return {"verified": verified}


@router.post(
    "/apply",
    response_model=IDApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an ID application",
    description=(
        "Creates a DocumentRequest of type 'ID Application'. "
        "Available to both guest (rfid_uid=null) and authenticated sessions. "
        "The request appears in the admin Document Requests dashboard."
    ),
)
def apply(payload: IDApplicationRequest, db: Session = Depends(get_db)):
    return apply_for_id(db, payload.resident_id, payload.rfid_uid, payload.photo)


# =========================================================
# CHANGE PASSCODE / PIN  (authenticated sessions only)
# =========================================================

@router.post(
    "/change-pin",
    response_model=ChangePinResponse,
    summary="Change security PIN",
    description=(
        "Verifies the resident's current 4-digit PIN, then replaces it with a new one. "
        "Only available to residents who are logged in via RFID. "
        "Guest users cannot access this endpoint."
    ),
)
def update_pin(payload: ChangePinRequest, db: Session = Depends(get_db)):
    return change_pin(db, payload.resident_id, payload.current_pin, payload.new_pin)


# =========================================================
# REPORT LOST CARD
# =========================================================

@router.get(
    "/report-lost/info/{resident_id}",
    response_model=ReportLostCardVerifyResponse,
    summary="Get resident RFID card status",
    description=(
        "Returns whether the selected resident has an active RFID card linked. "
        "The frontend uses has_rfid to enable or disable the 'Submit Report' button. "
        "Available to both guest and authenticated sessions."
    ),
)
def get_report_card_info(resident_id: int, db: Session = Depends(get_db)):
    return get_rfid_report_card_info(db, resident_id)


@router.post(
    "/report-lost",
    response_model=ReportLostCardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Report a lost RFID card",
    description=(
        "Verifies the resident's PIN, deactivates their active RFID card (is_active=False), "
        "and creates an RFIDReport record visible in the admin Reports dashboard. "
        "Available to both guest and authenticated sessions."
    ),
)
def submit_lost_card_report(payload: ReportLostCardRequest, db: Session = Depends(get_db)):
    return report_lost_card(db, payload.resident_id, payload.pin, payload.rfid_uid)