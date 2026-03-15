"""
app/services/document_service.py

Service layer for document type configuration and document request management.
Handles PDF generation via LibreOffice, eligibility checks, request lifecycle
(approve, reject, release, payment, undo), and blotter summaries.
"""

import random
import subprocess
import tempfile
import os
import platform
from io import BytesIO
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from docxtpl import DocxTemplate
from app.models.document import DocumentType, DocumentRequest
from app.models.resident import Resident
from app.models.blotter import BlotterRecord
from app.schemas.document import (
    DocumentRequestCreate,
    DocumentRequestKioskResponse,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    EligibilityCheckResult, 
    RequirementCheckResult
)
from pathlib import Path
from app.services.transaction_service import record_document_transaction

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_STORAGE_DIR = BASE_DIR / "storage" / "documents"


# =================================================================================
# PDF GENERATION
# =================================================================================

def _convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    with tempfile.TemporaryDirectory() as temp_dir:
        docx_path = os.path.join(temp_dir, "document.docx")
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        
        system = platform.system()
        if system == "Windows":
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
        else:
            soffice_cmd = "soffice"
        
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
        
        pdf_path = os.path.join(temp_dir, "document.pdf")
        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not generated")
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        return pdf_bytes


def _prepare_template_data(form_data: dict) -> dict:
    now = datetime.now()
    
    def get_ordinal_suffix(day: int) -> str:
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        return f"{day}{suffix}"
    
    template_data = form_data.copy()
    
    template_data.update({
        'date_today': now.strftime("%B %d, %Y"),
        'day': get_ordinal_suffix(now.day),
        'month': now.strftime("%B"),
        'year': str(now.year),
    })
    
    return template_data


def _generate_pdf_from_template(
    template_bytes: bytes,
    form_data: dict
) -> bytes:
    try:
        tpl = DocxTemplate(BytesIO(template_bytes))
        template_data = _prepare_template_data(form_data)
        tpl.render(template_data)
        docx_stream = BytesIO()
        tpl.save(docx_stream)
        docx_bytes = docx_stream.getvalue()
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

    return str(file_path.relative_to(BASE_DIR).as_posix())


# =================================================================================
# INTERNAL VALIDATION HELPERS
# =================================================================================

def _validate_document_type(db: Session, doctype_id: int) -> DocumentType:
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
    resident = db.query(Resident).filter(Resident.id == resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    return resident


def _validate_dynamic_fields(required_fields: list, submitted_data: dict):
    for field in required_fields:
        if field.get("required") is True:
            field_name = field.get("name")
            if field_name not in submitted_data:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Missing required field: {field_name}"
                )


def _check_existing_pending_request(db: Session, resident_id: int, doctype_id: int):
    exists = (
        db.query(DocumentRequest)
        .filter(
            DocumentRequest.resident_id == resident_id,
            DocumentRequest.doctype_id == doctype_id,
            DocumentRequest.status == "Pending"
        )
        .first()
    )

    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You already have a pending request for this document type. "
                   "Please wait for it to be processed before submitting a new one."
        )


def _generate_transaction_no(db: Session) -> str:
    while True:
        number = random.randint(1000, 9999)
        transaction_no = f"DR-{number}"
        exists = db.query(DocumentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


# =================================================================================
# ELIGIBILITY CHECKS
# =================================================================================

def _check_clean_blotter(db: Session, resident_id: int) -> bool:
    record = db.query(BlotterRecord).filter(
        BlotterRecord.respondent_id == resident_id
    ).first()
    return record is None


def _check_min_residency(resident: Resident, years: int = 0, months: int = 0) -> bool:
    from datetime import date
    if not resident.residency_start_date:
        return False
    today = date.today()
    total_months = (
        (today.year - resident.residency_start_date.year) * 12
        + (today.month - resident.residency_start_date.month)
    )
    if today.day < resident.residency_start_date.day:
        total_months -= 1
    required_months = years * 12 + months
    return total_months >= required_months


def _validate_system_requirements(db: Session, resident: Resident, requirements: list):
    for req in (requirements or []):
        if req.get("type") != "system_check":
            continue

        check_id = req.get("id")
        params = req.get("params") or {}

        if check_id == "clean_blotter":
            if not _check_clean_blotter(db, resident.id):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Requirement not met: {req.get('label', 'Clean Blotter Record')}"
                )

        elif check_id == "min_residency":
            years = params.get("years", 0)
            months = params.get("months", 0)
            if not _check_min_residency(resident, years, months):
                parts = []
                if years:
                    parts.append(f"{years} year{'s' if years != 1 else ''}")
                if months:
                    parts.append(f"{months} month{'s' if months != 1 else ''}")
                duration = " and ".join(parts) or "required duration"
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Requirement not met: {req.get('label', f'Minimum {duration} of residency')}"
                )


def check_resident_eligibility(
    db, resident_id: int, doctype_id: int
) -> dict:
    doc_type = db.query(DocumentType).filter(DocumentType.id == doctype_id).first()
    if not doc_type:
        return {
            "eligible": False,
            "resident_id": resident_id,
            "doctype_id": doctype_id,
            "checks": [{
                "id": "doctype_exists",
                "label": "Document type exists",
                "type": "system_check",
                "passed": False,
                "message": "Document type not found."
            }]
        }

    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        return {
            "eligible": False,
            "resident_id": resident_id,
            "doctype_id": doctype_id,
            "checks": [{
                "id": "resident_exists",
                "label": "Resident exists",
                "type": "system_check",
                "passed": False,
                "message": "Resident not found."
            }]
        }

    requirements = doc_type.requirements or []
    checks = []
    all_passed = True

    for req in requirements:
        req_id = req.get("id", "unknown")
        req_label = req.get("label", req_id)
        req_type = req.get("type", "document")
        params = req.get("params") or {}

        if req_type == "document":
            checks.append({
                "id": req_id,
                "label": req_label,
                "type": "document",
                "passed": None,
                "message": "Must be presented at the barangay hall."
            })

        elif req_type == "system_check":

            if req_id == "clean_blotter":
                blotter_records = db.query(BlotterRecord).filter(
                    BlotterRecord.respondent_id == resident_id
                ).all()

                if blotter_records:
                    record_nos = ", ".join(r.blotter_no for r in blotter_records)
                    checks.append({
                        "id": req_id,
                        "label": req_label,
                        "type": "system_check",
                        "passed": False,
                        "message": (
                            f"Resident is a respondent in {len(blotter_records)} blotter record(s): "
                            f"{record_nos}. Clean blotter record is required."
                        )
                    })
                    all_passed = False
                else:
                    checks.append({
                        "id": req_id,
                        "label": req_label,
                        "type": "system_check",
                        "passed": True,
                        "message": "No blotter records found as respondent."
                    })

            elif req_id == "min_residency":
                years_required = params.get("years", 0)
                months_required = params.get("months", 0)
                passed = _check_min_residency(resident, years_required, months_required)
                parts = []
                if years_required:
                    parts.append(f"{years_required} year{'s' if years_required != 1 else ''}")
                if months_required:
                    parts.append(f"{months_required} month{'s' if months_required != 1 else ''}")
                duration = " and ".join(parts) or "required duration"
                checks.append({
                    "id": req_id,
                    "label": req_label,
                    "type": "system_check",
                    "passed": passed,
                    "message": (
                        f"Minimum {duration} of residency required. "
                        + ("Passed." if passed else "Requirement not met.")
                    )
                })
                if not passed:
                    all_passed = False

            else:
                checks.append({
                    "id": req_id,
                    "label": req_label,
                    "type": "system_check",
                    "passed": None,
                    "message": f"Unknown check '{req_id}' — skipped."
                })

    return {
        "eligible": all_passed,
        "resident_id": resident_id,
        "doctype_id": doctype_id,
        "checks": checks
    }


# =================================================================================
# KIOSK
# =================================================================================

def get_available_document_types(db: Session):
    return (
        db.query(DocumentType)
        .filter(
            DocumentType.is_available.is_(True),
            DocumentType.is_id_application.is_(False),
        )
        .order_by(DocumentType.doctype_name.asc())
        .all()
    )


def create_document_request(db: Session, payload: DocumentRequestCreate) -> DocumentRequestKioskResponse:
    doc_type = _validate_document_type(db, payload.doctype_id)

    is_rfid_request = doc_type.doctype_name.upper() == "RFID"

    if payload.resident_id is not None:
        resident = _validate_resident(db, payload.resident_id)
        _check_existing_pending_request(db, payload.resident_id, payload.doctype_id)
    elif not is_rfid_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest mode is only allowed for RFID requests"
        )
    _validate_dynamic_fields(
        required_fields=doc_type.fields or [],
        submitted_data=payload.form_data
    )

    if payload.resident_id is not None:
        _validate_system_requirements(
            db=db,
            resident=resident, 
            requirements=doc_type.requirements or []
        )

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

    if doc_type.file:
        try:
            pdf_bytes = _generate_pdf_from_template(
                template_bytes=doc_type.file,
                form_data=payload.form_data
            )
            
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

    return DocumentRequestKioskResponse(
        transaction_no=request.transaction_no
    )


def get_kiosk_request_history(db: Session, resident_id: int):
    return (
        db.query(DocumentRequest)
        .join(DocumentType)
        .filter(DocumentRequest.resident_id == resident_id)
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )


# =================================================================================
# ADMIN — DOCUMENT TYPES
# =================================================================================

def get_all_document_types(db: Session):
    return (
        db.query(DocumentType)
        .order_by(DocumentType.doctype_name.asc())
        .all()
    )


def create_document_type(db: Session, payload: DocumentTypeCreate,):
    doc_type = DocumentType(
        doctype_name=payload.doctype_name,
        description=payload.description,
        price=payload.price,
        fields=payload.fields,
        is_available=payload.is_available,
        is_id_application=payload.is_id_application,
    )

    db.add(doc_type)
    db.commit()
    db.refresh(doc_type)

    return doc_type


def update_document_type( db: Session, doctype_id: int, payload: DocumentTypeUpdate,):
    doc_type = db.query(DocumentType).filter(DocumentType.id == doctype_id).first()

    if not doc_type:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(doc_type, field, value)

    db.commit()
    db.refresh(doc_type)

    return doc_type


def delete_document_type(db: Session, doctype_id: int):
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


# =================================================================================
# ADMIN — DOCUMENT REQUESTS
# =================================================================================

def _get_request(db: Session, request_id: int):
    return (
        db.query(DocumentRequest)
        .options(joinedload(DocumentRequest.resident).joinedload(Resident.rfids))
        .filter(DocumentRequest.id == request_id)
        .first()
    )


def get_all_document_requests(db: Session):
    from sqlalchemy.orm import joinedload

    return (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident).joinedload(Resident.rfids),
            joinedload(DocumentRequest.doctype)
        )
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )


def get_document_request_by_id(db: Session, request_id: int,):
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


def get_resident_blotter_summary(db, resident_id: int) -> dict:

    complainant_records = db.query(BlotterRecord).filter(
        BlotterRecord.complainant_id == resident_id
    ).all()

    respondent_records = db.query(BlotterRecord).filter(
        BlotterRecord.respondent_id == resident_id
    ).all()

    combined = []

    for r in complainant_records:
        combined.append({
            "id": r.id,
            "blotter_no": r.blotter_no,
            "role": "complainant",
            "incident_date": r.incident_date.isoformat() if r.incident_date else None,
            "incident_type": r.incident_type,
            "created_at": r.created_at.isoformat()
        })

    for r in respondent_records:
        combined.append({
            "id": r.id,
            "blotter_no": r.blotter_no,
            "role": "respondent",
            "incident_date": r.incident_date.isoformat() if r.incident_date else None,
            "incident_type": r.incident_type,
            "created_at": r.created_at.isoformat()
        })

    combined.sort(key=lambda x: x["created_at"], reverse=True)

    return {
        "resident_id": resident_id,
        "has_blotter": len(combined) > 0,
        "total_count": len(combined),
        "as_complainant": len(complainant_records),
        "as_respondent": len(respondent_records),
        "records": combined
    }


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


# =================================================================================
# ADMIN — REQUEST LIFECYCLE
# =================================================================================

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
    db.refresh(req)
    record_document_transaction(db, req)
    return True


def release_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    req.status = "Released"
    db.commit()
    db.refresh(req)
    record_document_transaction(db, req)
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
    req = _get_request(db, request_id)
    if not req:
        return False
    
    status_undo_map = {
        "Approved": "Pending",
        "Released": "Approved",
        "Rejected": "Pending",
    }
    
    if req.status not in status_undo_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Undo is not available for status: {req.status}"
        )
    
    req.status = status_undo_map[req.status]
    db.commit()
    return True


def bulk_undo_requests(db: Session, ids: list[int]):
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