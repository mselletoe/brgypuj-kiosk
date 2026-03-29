"""
app/api/kiosk/documents.py

Router for kiosk-facing document services.
Handles document type listing, request submission, request history,
and resident eligibility checks. Broadcasts new transactions to
connected admin clients via WebSocket on submission.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.document import (
    DocumentRequestCreate,
    DocumentRequestKioskResponse,
    DocumentTypeKioskOut,
    DocumentRequestKioskOut,
    EligibilityCheckResult
)
from app.services.document_service import (
    get_available_document_types,
    create_document_request,
    get_kiosk_request_history,
    check_resident_eligibility
)

router = APIRouter(prefix="/documents")


# =================================================================================
# DOCUMENT TYPES
# =================================================================================
@router.get("/types", response_model=list[DocumentTypeKioskOut])
def list_available_document_types(db: Session = Depends(get_db)):
    return get_available_document_types(db)


@router.get("/types/{doctype_id}/eligibility", response_model=EligibilityCheckResult)
def check_eligibility(doctype_id: int, resident_id: int, db: Session = Depends(get_db)):
    return check_resident_eligibility(db, resident_id=resident_id, doctype_id=doctype_id)


# =================================================================================
# DOCUMENT REQUESTS
# =================================================================================
@router.post("/requests", response_model=DocumentRequestKioskResponse, status_code=status.HTTP_201_CREATED)
async def submit_document_request(
    payload: DocumentRequestCreate,
    db: Session = Depends(get_db)
):
    result = create_document_request(db, payload)

    resident_name = None
    if payload.resident_id:
        from app.models.resident import Resident
        resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()
        if resident:
            resident_name = " ".join(filter(None, [resident.first_name, resident.last_name]))

    await ws_manager.broadcast_to_admin(
        "new_transaction",
        {
            "type": "Document",
            "resident_name": resident_name,
            "document_type": "Document",
            "transaction_no": getattr(result, 'transaction_no', ''),
        },
        db=db
    )
    return result


@router.get("/requests/{resident_id}", response_model=list[DocumentRequestKioskOut])
def get_my_document_requests(resident_id: int, db: Session = Depends(get_db)):
    return get_kiosk_request_history(db, resident_id)