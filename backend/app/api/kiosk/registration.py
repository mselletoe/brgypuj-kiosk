"""
app/api/kiosk/registration.py

Router for kiosk RFID card registration.
Handles the full registration flow: checking if a card is new,
verifying the admin passcode, listing approved ID applications,
and linking the scanned card to a resident record.
Broadcasts a notification to admin clients after a successful link.
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


# =================================================================================
# RFID STATUS CHECK
# =================================================================================

@router.get(
    "/check/{rfid_uid}",
    response_model=RFIDStatusResponse,
)
def check_rfid(rfid_uid: str, db: Session = Depends(get_db)):
    return check_rfid_status(db, rfid_uid)


# =================================================================================
# ADMIN PASSCODE
# =================================================================================

@router.post(
    "/verify-passcode",
    response_model=AdminPasscodeResponse,
)
def check_passcode(payload: AdminPasscodeRequest):
    return verify_admin_passcode(payload.passcode)


# =================================================================================
# APPROVED ID APPLICATIONS
# =================================================================================

@router.get(
    "/approved-applications",
    response_model=list[ApprovedIDApplication],
)
def get_approved_applications(db: Session = Depends(get_db)):
    return get_approved_id_applications(db)


# =================================================================================
# RFID LINKING
# =================================================================================

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