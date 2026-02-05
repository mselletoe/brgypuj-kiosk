"""
Document Service Layer
---------------------------
Handles the business logic for document management, including administrative 
configuration of document types and resident-facing request processing.
"""
import random
import subprocess
import tempfile
import os
import platform
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from docxtpl import DocxTemplate
from app.models.document import DocumentType, DocumentRequest
from app.models.resident import Resident
from app.schemas.document import (
    DocumentRequestCreate,
    DocumentRequestKioskResponse,
    DocumentTypeCreate,
    DocumentTypeUpdate,
)
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_STORAGE_DIR = BASE_DIR / "storage" / "documents"


# -------------------------------------------------
# PDF Generation Helper
# -------------------------------------------------

def _convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    """
    Convert DOCX bytes to PDF bytes using LibreOffice.
    Works on both Windows and Linux (Raspberry Pi).
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save DOCX to temp file
        docx_path = os.path.join(temp_dir, "document.docx")
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        
        # Determine LibreOffice command based on platform
        system = platform.system()
        if system == "Windows":
            # Common LibreOffice paths on Windows
            libreoffice_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
            soffice_cmd = None
            for path in libreoffice_paths:
                if os.path.exists(path):
                    soffice_cmd = path
                    break
            if not soffice_cmd:
                raise Exception("LibreOffice not found on Windows. Please install it.")
        else:  # Linux (Raspberry Pi)
            soffice_cmd = "soffice"
        
        # Convert DOCX to PDF using LibreOffice
        try:
            subprocess.run(
                [
                    soffice_cmd,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", temp_dir,
                    docx_path
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"LibreOffice conversion failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise Exception("LibreOffice not found. Install with: sudo apt-get install libreoffice")
        
        # Read the generated PDF
        pdf_path = os.path.join(temp_dir, "document.pdf")
        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not generated")
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        return pdf_bytes


def _prepare_template_data(form_data: dict) -> dict:
    """
    Prepares template data by auto-filling date-related placeholders.
    
    Automatically detects and fills:
    - {{ date_today }} - Full date (e.g., "January 4, 2026")
    - {{ day }} - Day with ordinal suffix (e.g., "4th")
    - {{ month }} - Full month name (e.g., "January")
    - {{ year }} - Full year (e.g., "2026")
    """
    now = datetime.now()
    
    # Helper function to get ordinal suffix
    def get_ordinal_suffix(day: int) -> str:
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix}"
    
    # Create a copy of form_data to avoid modifying original
    template_data = form_data.copy()
    
    # Auto-fill date placeholders
    template_data.update({
        'date_today': now.strftime("%B %d, %Y"),  # January 04, 2026
        'day': get_ordinal_suffix(now.day),        # 4th
        'month': now.strftime("%B"),               # January
        'year': str(now.year),                     # 2026
    })
    
    return template_data


def _generate_pdf_from_template(
    template_bytes: bytes,
    form_data: dict
) -> bytes:
    """
    Generates a PDF from a DOCX template by:
    1. Auto-filling date placeholders
    2. Rendering the template with form data
    3. Converting DOCX to PDF using LibreOffice
    """
    try:
        # Load template
        tpl = DocxTemplate(BytesIO(template_bytes))
        
        # Prepare data with auto-filled dates
        template_data = _prepare_template_data(form_data)
        
        # Render template
        tpl.render(template_data)
        
        # Save rendered DOCX to bytes
        docx_stream = BytesIO()
        tpl.save(docx_stream)
        docx_bytes = docx_stream.getvalue()
        
        # Convert to PDF
        pdf_bytes = _convert_docx_to_pdf(docx_bytes)
        
        return pdf_bytes
        
    except Exception as e:
        raise Exception(f"PDF generation failed: {str(e)}")


def _save_request_pdf(transaction_no: str, pdf_bytes: bytes) -> str:
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")

    output_dir = PDF_STORAGE_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"{transaction_no}.pdf"

    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    # store RELATIVE path in DB
    return str(file_path.relative_to(BASE_DIR))


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


def _generate_transaction_no(db: Session) -> str:
    """
    Generates a unique transaction number in the format DR-XXXX
    """
    while True:
        number = random.randint(1000, 9999)
        transaction_no = f"DR-{number}"
        exists = db.query(DocumentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


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
    
    Special handling for RFID requests:
    - RFID requests can be made in guest mode (resident_id = None)
    - All other document types require a valid resident_id
    
    Auto-generates PDF from template with form data.
    """

    # 1. Validate document availability
    doc_type = _validate_document_type(db, payload.doctype_id)

    # 2. Check if this is an RFID request
    is_rfid_request = doc_type.doctype_name.upper() == "RFID"

    # 3. Validate resident based on document type
    if payload.resident_id is not None:
        # If resident_id is provided, validate it exists
        _validate_resident(db, payload.resident_id)
    elif not is_rfid_request:
        # If resident_id is None and it's NOT an RFID request, reject
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest mode is only allowed for RFID requests"
        )
    # If resident_id is None and it IS an RFID request, allow (guest mode)

    # 4. Validate submitted dynamic fields against admin-defined requirements
    _validate_dynamic_fields(
        required_fields=doc_type.fields or [],
        submitted_data=payload.form_data
    )

    # 5. Persist the request
    request = DocumentRequest(
        resident_id=payload.resident_id,
        doctype_id=payload.doctype_id,
        price=doc_type.price,
        form_data=payload.form_data,
        transaction_no=_generate_transaction_no(db)
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    # 6. Auto-generate PDF if template exists
    if doc_type.file:
        try:
            pdf_bytes = _generate_pdf_from_template(
                template_bytes=doc_type.file,
                form_data=payload.form_data
            )
            
            # Save PDF to request
            relative_path = _save_request_pdf(
                request.transaction_no,
                pdf_bytes
            )
            request.request_file_path = relative_path
            db.commit()
            db.refresh(request)
            
            print(f"✅ PDF auto-generated for request {request.transaction_no}")
            
        except Exception as e:
            print(f"❌ PDF generation failed for request {request.transaction_no}: {str(e)}")
            # Don't fail the request if PDF generation fails
            # Admin can regenerate manually if needed

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
        is_available=payload.is_available,
    )

    db.add(doc_type)
    db.commit()
    db.refresh(doc_type)

    return doc_type


def update_document_type( db: Session, doctype_id: int, payload: DocumentTypeUpdate,):
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


def delete_document_type(db: Session, doctype_id: int):
    """
    Admin: Actually deletes a document type from the database.
    """
    doc_type = db.query(DocumentType).filter(DocumentType.id == doctype_id).first()

    if not doc_type:
        return None

    in_use = (
        db.query(DocumentRequest)
        .filter(DocumentRequest.doctype_id == doctype_id)
        .count()
    )

    if in_use > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete document type: it is used by existing requests."
        )
    
    db.delete(doc_type)
    db.commit()

    return True


def _get_request(db: Session, request_id: int):
    return db.query(DocumentRequest).filter(DocumentRequest.id == request_id).first()


def get_all_document_requests(db: Session):
    """
    Admin: Monitors all incoming document requests with resident information.
    """
    from sqlalchemy.orm import joinedload
    
    return (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident),
            joinedload(DocumentRequest.doctype)
        )
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )


def get_document_request_by_id(db: Session, request_id: int,):
    """
    Admin: Fetches detailed information for a specific document request.
    """
    from sqlalchemy.orm import joinedload
    
    return (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident),
            joinedload(DocumentRequest.doctype)
        )
        .filter(DocumentRequest.id == request_id)
        .first()
    )


def get_document_type_with_file(db: Session, doctype_id: int):
    return (
        db.query(DocumentType)
        .filter(DocumentType.id == doctype_id)
        .first()
    )


def upload_document_type_file(
    db: Session,
    doctype_id: int,
    file_bytes: bytes,
):
    doc = db.query(DocumentType).filter(DocumentType.id == doctype_id).first()
    if not doc:
        return None

    doc.file = file_bytes
    db.commit()
    return True


def approve_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    req.status = "Approved"
    db.commit()
    return True


def reject_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    req.status = "Rejected"
    db.commit()
    return True


def release_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    req.status = "Released"
    db.commit()
    return True


def mark_request_paid(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    req.payment_status = "paid"
    db.commit()
    return True


def mark_request_unpaid(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    req.payment_status = "unpaid"
    db.commit()
    return True


def undo_request(db: Session, request_id: int):
    """
    Moves a request back to its previous status based on current status:
    - Approved → Pending
    - Released → Approved
    - Rejected → Pending
    - Pending → No change (undo disabled)
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    # Define status transitions for undo
    status_undo_map = {
        "Approved": "Pending",
        "Released": "Approved",
        "Rejected": "Pending",
    }
    
    # Check if undo is allowed for current status
    if req.status not in status_undo_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Undo is not available for status: {req.status}"
        )
    
    # Update to previous status
    req.status = status_undo_map[req.status]
    db.commit()
    return True


def bulk_undo_requests(db: Session, ids: list[int]):
    """
    Bulk undo operation for multiple requests.
    Only processes requests that are in undoable states.
    """
    requests = db.query(DocumentRequest).filter(DocumentRequest.id.in_(ids)).all()
    
    status_undo_map = {
        "Approved": "Pending",
        "Released": "Approved",
        "Rejected": "Pending",
    }
    
    updated_count = 0
    for req in requests:
        if req.status in status_undo_map:
            req.status = status_undo_map[req.status]
            updated_count += 1
    
    db.commit()
    return updated_count


def delete_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    db.delete(req)
    db.commit()
    return True


def bulk_delete_requests(db: Session, ids: list[int]):
    count = db.query(DocumentRequest).filter(DocumentRequest.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count


def get_request_notes(db: Session, request_id: int) -> str:
    req = _get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req.notes or ""


def update_request_notes(db: Session, request_id: int, notes: str) -> str:
    req = _get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.notes = notes
    db.commit()
    db.refresh(req)
    return req.notes


def regenerate_request_pdf(db: Session, request_id: int) -> bool:
    """
    Admin: Manually regenerate PDF for a specific request.
    Useful if auto-generation failed or template was updated.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    doc_type = db.query(DocumentType).filter(DocumentType.id == req.doctype_id).first()
    if not doc_type or not doc_type.file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No template file found for this document type"
        )
    
    try:
        pdf_bytes = _generate_pdf_from_template(
            template_bytes=doc_type.file,
            form_data=req.form_data
        )
        
        relative_path = _save_request_pdf(
            req.transaction_no,
            pdf_bytes
        )
        req.request_file_path = relative_path
        db.commit()
        
        return True
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF regeneration failed: {str(e)}"
        )