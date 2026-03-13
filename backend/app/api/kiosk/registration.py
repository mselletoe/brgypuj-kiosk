"""
RFID Registration Router
------------------------
Exposes the new-RFID registration workflow as REST endpoints.

All routes are prefixed with /kiosk/rfid-registration and consumed
exclusively by the Kiosk interface (ScanRFID.vue, AdminPasscode.vue, Register.vue).

Endpoints:
  GET  /rfid-registration/check/{rfid_uid}    — is this UID new or already linked?
  POST /rfid-registration/verify-passcode     — validate admin passcode gate
  GET  /rfid-registration/approved-applications — list approved ID apps awaiting linking
  POST /rfid-registration/link                — bind a new RFID UID to a resident
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.registration import (
    RFIDStatusResponse,
    AdminPasscodeRequest,
    AdminPasscodeResponse,
    ApprovedIDApplication,
    LinkRFIDRequest,
    LinkRFIDResponse,
)
from app.services.registration_service import (
    check_rfid_status,
    verify_admin_passcode,
    get_approved_id_applications,
    link_rfid_to_resident,
)

router = APIRouter(prefix="/rfid-registration")


# =========================================================
# 1. CHECK RFID STATUS
# =========================================================

@router.get(
    "/check/{rfid_uid}",
    response_model=RFIDStatusResponse,
    summary="Check if RFID UID is new or already registered",
    description=(
        "Called immediately after a card is scanned on the Kiosk. "
        "Returns is_new=true if the UID has never been registered, "
        "triggering the admin passcode → Register flow instead of normal auth."
    ),
)
def check_rfid(rfid_uid: str, db: Session = Depends(get_db)):
    return check_rfid_status(db, rfid_uid)


# =========================================================
# 2. VERIFY ADMIN PASSCODE
# =========================================================

@router.post(
    "/verify-passcode",
    response_model=AdminPasscodeResponse,
    summary="Validate admin passcode before Register screen",
    description=(
        "The kiosk prompts for an admin passcode when a new RFID is detected. "
        "Returns valid=true if the passcode matches the configured value. "
        "The frontend should only navigate to /register on valid=true."
    ),
)
def check_passcode(payload: AdminPasscodeRequest):
    return verify_admin_passcode(payload.passcode)


# =========================================================
# 3. GET APPROVED ID APPLICATIONS
# =========================================================

@router.get(
    "/approved-applications",
    response_model=list[ApprovedIDApplication],
    summary="List approved ID applications awaiting RFID linking",
    description=(
        "Returns all ID Application DocumentRequests that have been Approved "
        "and have not yet been linked to an RFID card. "
        "Displayed in the Register screen's left panel as selectable transaction cards."
    ),
)
def get_approved_applications(db: Session = Depends(get_db)):
    return get_approved_id_applications(db)


# =========================================================
# 4. LINK RFID TO RESIDENT
# =========================================================

@router.post("/link", response_model=LinkRFIDResponse, status_code=status.HTTP_201_CREATED)
async def link_rfid(payload: LinkRFIDRequest, db: Session = Depends(get_db)):
    result = link_rfid_to_resident(
        db,
        rfid_uid=payload.rfid_uid,
        resident_id=payload.resident_id,
        document_request_id=payload.document_request_id,
    )
    await ws_manager.broadcast_to_admin(
        "new_rfid_linked",
        {
            "type": "Document",
            "resident_name": f"Resident #{payload.resident_id}",
        },
        db=db
    )
    return result