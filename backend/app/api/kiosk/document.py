"""
Kiosk Document Services API
---------------------------
Handles resident-facing operations for browsing available document types 
and submitting requests via the kiosk interface.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.document import (
    DocumentRequestCreate,
    DocumentRequestKioskResponse,
    DocumentTypeKioskOut,
    DocumentRequestKioskOut,
)
from app.services.document_service import (
    get_available_document_types,
    create_document_request,
    get_kiosk_request_history,
)

router = APIRouter(prefix="/documents")


# =========================================================
# DOCUMENT TYPES 
# =========================================================

@router.get(
    "/types",
    response_model=list[DocumentTypeKioskOut]
)
def list_available_document_types(db: Session = Depends(get_db)):
    """
    Lists document types available for resident requests at the kiosk.
    """
    return get_available_document_types(db)


# =========================================================
# DOCUMENT REQUESTS 
# =========================================================

@router.post(
    "/requests",
    response_model=DocumentRequestKioskResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_document_request(
    payload: DocumentRequestCreate,
    db: Session = Depends(get_db)
):
    """
    Processes a document request submission and returns a unique transaction number.
    """
    return create_document_request(db, payload)


@router.get(
    "/requests/{resident_id}",
    response_model=list[DocumentRequestKioskOut]
)
def get_my_document_requests(resident_id: int, db: Session = Depends(get_db)):
    """
    Retrieves the request history for a specific resident based on their ID.
    """
    return get_kiosk_request_history(db, resident_id)
