"""
Document Service Layer
---------------------------
Handles the business logic for document management, including administrative 
configuration of document types and resident-facing request processing.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.document import DocumentType, DocumentRequest
from app.models.resident import Resident
from app.schemas.document import (
    DocumentRequestCreate,
    DocumentRequestKioskResponse,
    DocumentTypeCreate,
    DocumentTypeUpdate,
)

# -------------------------------------------------
# Internal Helpers
# -------------------------------------------------

def _validate_document_type(db: Session, doctype_id: int) -> DocumentType:
    """
    Verifies the existence and availability of a specific document type.
    """
    doc_type = (
        db.query(DocumentType)
        .filter(
            DocumentType.id == doctype_id,
            DocumentType.is_available.is_(True)
        )
        .first()
    )

    if not doc_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not available"
        )

    return doc_type


def _validate_resident(db: Session, resident_id: int) -> Resident:
    """
    Ensures the resident exists in the database.
    """
    resident = db.query(Resident).filter(Resident.id == resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    return resident


def _validate_dynamic_fields(required_fields: list, submitted_data: dict):
    """
    Cross-references submitted form data against the required fields 
    defined in the document type template.
    """

    for field in required_fields:
        if field.get("required") is True:
            field_name = field.get("name")
            if field_name not in submitted_data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required field: {field_name}"
                )


def _check_existing_pending_request(db: Session, resident_id: int):
    """
    Enforces the single-pending-request policy to prevent system flooding.
    """
    exists = (
        db.query(DocumentRequest)
        .filter(
            DocumentRequest.resident_id == resident_id,
            DocumentRequest.status == "Pending"
        )
        .first()
    )

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a pending document request"
        )


# -------------------------------------------------
# Kiosk Service Functions
# -------------------------------------------------

def get_available_document_types(db: Session):
    """
    Retrieves all document types currently marked as available for the kiosk.
    """
    return (
        db.query(DocumentType)
        .filter(DocumentType.is_available.is_(True))
        .order_by(DocumentType.doctype_name.asc())
        .all()
    )


def create_document_request(db: Session, payload: DocumentRequestCreate) -> DocumentRequestKioskResponse:
    """
    Processes a new document request from the kiosk. Executes comprehensive 
    validation of the resident, document availability, and dynamic field data.
    """

    # 1. Validate resident existence
    _validate_resident(db, payload.resident_id)

    # 2. Validate document availability
    doc_type = _validate_document_type(db, payload.doctype_id)

    # 3. Validate submitted dynamic fields against admin-defined requirements
    _validate_dynamic_fields(
        required_fields=doc_type.fields or [],
        submitted_data=payload.form_data
    )

    # 4. Enforce single pending request policy
    _check_existing_pending_request(db, payload.resident_id)

    # 5. Persist the request
    request = DocumentRequest(
        resident_id=payload.resident_id,
        doctype_id=payload.doctype_id,
        form_data=payload.form_data
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return DocumentRequestKioskResponse(
        transaction_no=request.transaction_no
    )


def get_kiosk_request_history(db: Session, resident_id: int):
    """
    Retrieves the request history for a specific resident to display on the kiosk.
    """
    return (
        db.query(DocumentRequest)
        .join(DocumentType)
        .filter(DocumentRequest.resident_id == resident_id)
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )


# -------------------------------------------------
# Administrative Functions
# -------------------------------------------------

def get_all_document_types(db: Session):
    """
    Admin: Lists all document types regardless of availability.
    """
    return (
        db.query(DocumentType)
        .order_by(DocumentType.doctype_name.asc())
        .all()
    )


def create_document_type(db: Session, payload: DocumentTypeCreate,):
    """
    Admin: Configures a new document type template.
    """
    doc_type = DocumentType(
        doctype_name=payload.doctype_name,
        description=payload.description,
        price=payload.price,
        fields=payload.fields,
        file=payload.file,
        is_available=payload.is_available,
    )

    db.add(doc_type)
    db.commit()
    db.refresh(doc_type)

    return doc_type


def update_document_type(
    db: Session,
    doctype_id: int,
    payload: DocumentTypeUpdate,
):
    """
    Admin: Updates an existing document type template.
    """
    doc_type = db.query(DocumentType).filter(DocumentType.id == doctype_id).first()

    if not doc_type:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doc_type, field, value)

    db.commit()
    db.refresh(doc_type)

    return doc_type


def get_all_document_requests(db: Session):
    """
    Admin: Monitors all incoming document requests.
    """
    return (
        db.query(DocumentRequest)
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )


def get_document_request_by_id(db: Session, request_id: int,):
    """
    Admin: Fetches detailed information for a specific document request.
    """
    return (
        db.query(DocumentRequest)
        .filter(DocumentRequest.id == request_id)
        .first()
    )