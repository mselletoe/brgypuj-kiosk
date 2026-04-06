"""
app/api/kiosk/id.py

Router for kiosk ID services.
Handles resident search, birthdate verification, ID applications,
PIN management, and lost card reporting. Broadcasts relevant events
to connected admin clients via WebSocket on submission.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.id import (
    ResidentSearchResult,
    BirthdateVerifyRequest,
    BirthdateVerifyResponse,
    IDApplicationRequest,
    IDApplicationResponse,
    ChangePinRequest,
    ChangePinResponse,
    VerifyPinRequest,
    VerifyPinResponse,
    ReportLostCardVerifyResponse,
    ReportLostCardRequest,
    ReportLostCardResponse,
)
from app.services.id_service import (
    search_residents_by_name,
    verify_resident_birthdate,
    apply_for_id,
    change_pin,
    verify_pin,
    get_rfid_report_card_info,
    report_lost_card,
    get_id_application_fields,
    generate_brgy_id_number,
    check_id_requirements,
)

router = APIRouter(prefix="/id-services")


# =================================================================================
# RESIDENT LOOKUP
# =================================================================================

@router.get(
    "/residents/search",
    response_model=list[ResidentSearchResult],
    summary="Search residents by name",
)
def search_residents(query: str, db: Session = Depends(get_db)):
    if not query or len(query.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query must be at least 2 characters."
        )
    return search_residents_by_name(db, query.strip())


# =================================================================================
# ID APPLICATION
# =================================================================================

@router.get(
    "/apply/fields",
    summary="Get ID application form fields",
)
def get_id_fields(db: Session = Depends(get_db)):
    return get_id_application_fields(db)


@router.get(
    "/apply/generate-brgy-id",
    summary="Generate next Barangay ID number",
)
def get_next_brgy_id(db: Session = Depends(get_db)):
    return {"brgy_id_number": generate_brgy_id_number(db)}


@router.get(
    "/apply/requirements-check/{resident_id}",
    summary="Check if a resident meets ID application requirements",
)
def requirements_check(resident_id: int, db: Session = Depends(get_db)):
    return check_id_requirements(db, resident_id)


@router.post(
    "/apply/verify-birthdate",
    response_model=BirthdateVerifyResponse,
    summary="Verify resident identity via birthdate",
)
def verify_birthdate(payload: BirthdateVerifyRequest, db: Session = Depends(get_db)):
    verified = verify_resident_birthdate(db, payload.resident_id, payload.birthdate)
    return {"verified": verified}


@router.post("/apply", response_model=IDApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply(payload: IDApplicationRequest, db: Session = Depends(get_db)):
    result = apply_for_id(
        db,
        payload.resident_id,
        payload.applicant_resident_id,
        payload.rfid_uid,
        payload.photo,
        use_manual_data=payload.use_manual_data,
        field_values=payload.field_values,
    )

    resident_name = None
    if payload.resident_id:
        from app.models.resident import Resident
        resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()
        if resident:
            resident_name = " ".join(filter(None, [resident.first_name, resident.last_name]))

    await ws_manager.broadcast_to_admin(
        "new_id_application",
        {
            "type": "ID Services",
            "event": "new_id_application",
            "resident_name": resident_name,
            "transaction_no": getattr(result, 'transaction_no', ''),
        },
        db=db
    )
    return result


# =================================================================================
# PIN MANAGEMENT
# =================================================================================

@router.post(
    "/verify-pin",
    response_model=VerifyPinResponse,
    summary="Verify current PIN without changing it",
)
def check_pin(payload: VerifyPinRequest, db: Session = Depends(get_db)):
    return verify_pin(db, payload.resident_id, payload.pin)


@router.post(
    "/change-pin",
    response_model=ChangePinResponse,
    summary="Change security PIN",
)
def update_pin(payload: ChangePinRequest, db: Session = Depends(get_db)):
    return change_pin(db, payload.resident_id, payload.current_pin, payload.new_pin)


# =================================================================================
# LOST CARD REPORTING
# =================================================================================

@router.get(
    "/report-lost/info/{resident_id}",
    response_model=ReportLostCardVerifyResponse,
    summary="Get resident RFID card status",
)
def get_report_card_info(resident_id: int, db: Session = Depends(get_db)):
    return get_rfid_report_card_info(db, resident_id)


@router.post("/report-lost", response_model=ReportLostCardResponse, status_code=status.HTTP_201_CREATED)
async def submit_lost_card_report(payload: ReportLostCardRequest, db: Session = Depends(get_db)):
    result = report_lost_card(db, payload.resident_id, payload.pin, payload.rfid_uid)

    resident_name = None
    if payload.resident_id:
        from app.models.resident import Resident
        resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()
        if resident:
            resident_name = " ".join(filter(None, [resident.first_name, resident.last_name]))

    await ws_manager.broadcast_to_admin(
        "new_lost_card_report",
        {
            "type": "ID Services",
            "event": "new_lost_card_report",
            "resident_name": resident_name,
        },
        db=db
    )
    return result