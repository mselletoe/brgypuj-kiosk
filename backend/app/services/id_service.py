
"""
app/services/id_service.py
 
Service layer for barangay ID applications and RFID card management.
Handles ID application submission, PDF generation, release lifecycle,
PIN management, lost-card reporting, RFID report operations,
and ID requirement eligibility checks.
"""

import random
import subprocess
import tempfile
import os
import platform
import base64
from docxtpl import InlineImage
from docx.shared import Mm
from io import BytesIO
from PIL import Image, ImageDraw
from datetime import date, datetime, timedelta
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from passlib.context import CryptContext
from docxtpl import DocxTemplate
from app.db.session import SessionLocal
from app.models.resident import Resident, ResidentRFID
from app.models.document import DocumentRequest, DocumentType
from app.models.barangayid import BarangayID
from app.models.misc import RFIDReport
from app.models.systemconfig import SystemConfig
from app.services.document_service import _convert_docx_to_pdf

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_STORAGE_DIR = BASE_DIR / "storage" / "documents"

ID_APPLICATION_DOCTYPE_NAME = "ID Application"

RFID_PIN_DEFAULT = "0000"

# Form data keys that are metadata, not template context variables
_FORM_DATA_META_KEYS = {
    "request_type",
    "request_for_id",
    "request_for_name",
    "session_rfid",
    "requested_date",
    "use_manual_data",
    "validity",
}


# =================================================================================
# INTERNAL HELPERS
# =================================================================================

def _get_resident_or_404(db: Session, resident_id: int) -> Resident:
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    return resident


def _get_active_rfid(resident: Resident) -> ResidentRFID | None:
    return next((r for r in resident.rfids if r.is_active), None)


def _generate_transaction_no(db: Session) -> str:
    while True:
        number = random.randint(1000, 9999)
        tx_no = f"ID-{number}"
        exists = db.query(DocumentRequest).filter_by(transaction_no=tx_no).first()
        if not exists:
            return tx_no


def _generate_brgy_id_number(db: Session) -> str:
    max_number = db.query(func.max(BarangayID.brgy_id_number)).scalar()
    if max_number is None:
        next_number = 1
    else:
        try:
            next_number = int(max_number) + 1
        except (ValueError, TypeError):
            next_number = 1
    return str(next_number).zfill(5)


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
                [soffice_cmd, "--headless", "--convert-to", "pdf",
                 "--outdir", temp_dir, docx_path],
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
            return f.read()


def _make_circle_photo(photo_bytes: bytes, size: int = 300) -> bytes:
    img = Image.open(BytesIO(photo_bytes)).convert("RGBA")

    w, h = img.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    img = img.crop((left, top, left + min_side, top + min_side))
    img = img.resize((size, size), Image.LANCZOS)

    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)

    out = BytesIO()
    result.save(out, format="PNG")
    return out.getvalue()


def _generate_id_pdf(template_bytes: bytes, context: dict) -> bytes:

    tpl = DocxTemplate(BytesIO(template_bytes))

    if context.get("photo") is not None:
        photo_bytes = context["photo"] 
        if isinstance(photo_bytes, bytes):
            circle_bytes = _make_circle_photo(photo_bytes)
            context["photo"] = InlineImage(tpl, BytesIO(circle_bytes), width=Mm(24))

    tpl.render(context)

    docx_stream = BytesIO()
    tpl.save(docx_stream)
    docx_bytes = docx_stream.getvalue()

    return _convert_docx_to_pdf(docx_bytes)


def _save_id_pdf(transaction_no: str, pdf_bytes: bytes) -> str:
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")

    output_dir = PDF_STORAGE_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"{transaction_no}.pdf"
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    return str(file_path.relative_to(BASE_DIR).as_posix())


# =================================================================================
# KIOSK — ID LOOKUP & SEARCH
# =================================================================================

def generate_brgy_id_number(db: Session) -> str:
    return _generate_brgy_id_number(db)


def get_id_application_fields(db: Session) -> list:
    doc_type = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()
    return doc_type.fields or [] if doc_type else []


def search_residents_by_name(db: Session, query: str) -> list[dict]:
    parts = [p.strip() for p in query.split(",")]
    last_prefix = parts[0] if len(parts) > 0 else ""
    first_prefix = parts[1] if len(parts) > 1 else ""

    filters = [Resident.last_name.ilike(f"{last_prefix}%")]

    if first_prefix:
        filters.append(Resident.first_name.ilike(f"{first_prefix}%"))

    residents = (
        db.query(Resident)
        .options(joinedload(Resident.rfids))
        .filter(*filters)
        .order_by(Resident.last_name, Resident.first_name)
        .limit(20)
        .all()
    )

    # Flag residents who already have a pending application
    pending_applicant_ids = set()
    for r in residents:
        exists = (
            db.query(DocumentRequest.id)
            .filter(
                DocumentRequest.form_data["request_for_id"].astext == str(r.id),
                DocumentRequest.doctype_id.is_(None),
                DocumentRequest.status == "Pending",
            )
            .first()
        )
        if exists:
            pending_applicant_ids.add(r.id)

    return [
        {
            "resident_id": r.id,
            "first_name": r.first_name,
            "middle_name": r.middle_name,
            "last_name": r.last_name,
            "suffix": r.suffix,
            "has_rfid": any(rfid.is_active for rfid in r.rfids),
            "has_pending": r.id in pending_applicant_ids,
        }
        for r in residents
    ]


def verify_resident_birthdate(db: Session, resident_id: int, birthdate) -> bool:
    resident = _get_resident_or_404(db, resident_id)
    return resident.birthdate == birthdate


# =================================================================================
# KIOSK — ID APPLICATION SUBMISSION
# =================================================================================

def apply_for_id(
    db: Session,
    resident_id: int | None,
    applicant_resident_id: int,
    rfid_uid: str | None,
    photo: str | None,
    use_manual_data: bool = False,
    field_values: dict = {},
) -> dict:
    applicant = _get_resident_or_404(db, applicant_resident_id)

    requester_id = resident_id if resident_id is not None else applicant_resident_id
    requester = _get_resident_or_404(db, requester_id)

    # Prevent duplicate pending applications for the same resident
    duplicate = (
        db.query(DocumentRequest)
        .filter(
            DocumentRequest.form_data["request_for_id"].astext == str(applicant_resident_id),
            DocumentRequest.doctype_id.is_(None),
            DocumentRequest.status == "Pending",
        )
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This resident already has a pending ID application."
        )

    if photo:
        try:
            if "," in photo:
                photo = photo.split(",", 1)[1]
            applicant.photo = base64.b64decode(photo)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid photo data."
            )

    active_rfid = _get_active_rfid(requester)
    display_rfid = rfid_uid or (active_rfid.rfid_uid if active_rfid else None) or "Guest Mode"

    tx_no = _generate_transaction_no(db)
    now = datetime.now()

    brgy_id_number = _generate_brgy_id_number(db)

    id_doctype = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    request = DocumentRequest(
        transaction_no=tx_no,
        resident_id=requester_id,  
        doctype_id=None, 
        price=id_doctype.price if id_doctype else 0,
        status="Pending",
        payment_status="unpaid",
        form_data={
            "request_type":    ID_APPLICATION_DOCTYPE_NAME,
            "request_for_id":  applicant_resident_id,
            "request_for_name": f"{applicant.first_name} {applicant.last_name}",
            "session_rfid":    display_rfid,
            "requested_date":  now.isoformat(),
            "use_manual_data": use_manual_data,
            "brgy_id_number":  brgy_id_number,
            **field_values, 
        },
        requested_at=now,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    barangay_id_row = BarangayID(
        resident_id=applicant.id,
        rfid_id=None, 
        request_id=request.id,
        brgy_id_number=brgy_id_number,
        issued_date=date.today(),
        expiration_date=None,  
        is_active=False,
    )
    db.add(barangay_id_row)
    db.commit()

    if id_doctype and id_doctype.file:
        try:
            context = {
                k: v for k, v in request.form_data.items()
                if k not in _FORM_DATA_META_KEYS
            }
            context["id_num"] = context.get("brgy_id_number", "")
            context["photo"] = bytes(applicant.photo) if applicant.photo else None

            name_parts = [applicant.first_name]
            if applicant.middle_name:
                name_parts.append(applicant.middle_name)
            context.setdefault("full_name", f"{applicant.last_name}, {' '.join(name_parts)}")
            context.setdefault("last_name", applicant.last_name.upper())

            try:
                sys_config = db.query(SystemConfig).filter(SystemConfig.id == 1).first()
                expiry_days = (sys_config.rfid_expiry_days if sys_config else None) or 365
                context["validity"] = (date.today() + timedelta(days=expiry_days)).strftime("%B %d, %Y")
            except Exception as ve:
                print(f"⚠️ Could not compute validity date: {ve}")
                context["validity"] = ""

            pdf_bytes = _generate_id_pdf(bytes(id_doctype.file), context)
            relative_path = _save_id_pdf(request.transaction_no, pdf_bytes)
            request.request_file_path = relative_path
            db.commit()
            print(f"✅ ID PDF generated for {request.transaction_no}")
        except Exception as e:
            print(f"❌ ID PDF generation failed for {request.transaction_no}: {str(e)}")

    return {
        "transaction_no": request.transaction_no,
        "resident_first_name": applicant.first_name,
        "resident_last_name": applicant.last_name,
        "requested_at": request.requested_at,
    }


# =================================================================================
# ADMIN — ID APPLICATION RELEASE
# =================================================================================

def release_id_application(db: Session, request_id: int) -> dict:
    req = (
        db.query(DocumentRequest)
        .options(joinedload(DocumentRequest.resident).joinedload(Resident.rfids))
        .filter(DocumentRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Application not found")

    if req.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Application must be in 'Approved' status to release (currently '{req.status}')."
        )

    form_data = req.form_data or {}
    applicant_id = form_data.get("request_for_id")
    if applicant_id is None:
        raise HTTPException(status_code=400, detail="Application is missing request_for_id.")

    applicant = (
        db.query(Resident)
        .options(joinedload(Resident.rfids))
        .filter(Resident.id == int(applicant_id))
        .first()
    )
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant resident not found.")

    brgy_id_number = form_data.get("brgy_id_number")

    barangay_id_row = (
        db.query(BarangayID)
        .filter(
            BarangayID.request_id == req.id,
            BarangayID.is_active.is_(False),
        )
        .first()
    )

    if barangay_id_row:
        active_rfid = _get_active_rfid(applicant)
        barangay_id_row.rfid_id = active_rfid.id if active_rfid else None
        barangay_id_row.expiration_date = active_rfid.expiration_date if active_rfid else None
        barangay_id_row.is_active = True
        if not brgy_id_number:
            brgy_id_number = barangay_id_row.brgy_id_number
    else:
        if not brgy_id_number:
            brgy_id_number = _generate_brgy_id_number(db)
        active_rfid = _get_active_rfid(applicant)
        barangay_id_row = BarangayID(
            resident_id=applicant.id,
            rfid_id=active_rfid.id if active_rfid else None,
            request_id=req.id,
            brgy_id_number=brgy_id_number,
            issued_date=date.today(),
            expiration_date=active_rfid.expiration_date if active_rfid else None,
            is_active=True,
        )
        db.add(barangay_id_row)

    req.status = "Released"

    db.commit()
    db.refresh(barangay_id_row)

    return {
        "request_id": req.id,
        "transaction_no": req.transaction_no,
        "brgy_id_number": brgy_id_number,
        "resident_first_name": applicant.first_name,
        "resident_last_name": applicant.last_name,
        "issued_date": str(date.today()),
        "has_filled_template": req.request_file_path is not None,
    }


# =================================================================================
# KIOSK — PIN MANAGEMENT
# =================================================================================

def change_pin(db: Session, resident_id: int, current_pin: str, new_pin: str) -> dict:
    resident = _get_resident_or_404(db, resident_id)

    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured yet. Please set your PIN first."
        )

    if not pwd_context.verify(current_pin, resident.rfid_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current PIN is incorrect."
        )

    resident.rfid_pin = pwd_context.hash(new_pin)
    db.commit()

    return {"success": True, "message": "PIN updated successfully."}


def verify_pin(db: Session, resident_id: int, pin: str) -> dict:
    resident = _get_resident_or_404(db, resident_id)

    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured yet. Please set your PIN first."
        )

    if not pwd_context.verify(pin, resident.rfid_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current PIN is incorrect."
        )

    return {"verified": True}


# =================================================================================
# KIOSK — LOST CARD REPORTING
# =================================================================================

def get_rfid_report_card_info(db: Session, resident_id: int) -> dict:
    resident = (
        db.query(Resident)
        .options(joinedload(Resident.rfids))
        .filter(Resident.id == resident_id)
        .first()
    )
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    active_rfid = _get_active_rfid(resident)

    return {
        "resident_id": resident.id,
        "first_name": resident.first_name,
        "last_name": resident.last_name,
        "rfid_uid": active_rfid.rfid_uid if active_rfid else None,
        "has_rfid": active_rfid is not None,
    }


def report_lost_card(db: Session, resident_id: int, pin: str, rfid_uid: str | None) -> dict:
    resident = (
        db.query(Resident)
        .options(joinedload(Resident.rfids))
        .filter(Resident.id == resident_id)
        .first()
    )
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    active_rfid = _get_active_rfid(resident)
    if not active_rfid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This resident has no active RFID card to report."
        )

    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured. Please set a PIN before reporting a lost card."
        )
    if not pwd_context.verify(pin, resident.rfid_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect PIN."
        )

    deactivated_uid = active_rfid.rfid_uid
    active_rfid.is_active = False

    report = RFIDReport(
        resident_id=resident_id,
        status="Pending",
        created_at=datetime.now(),
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report.id,
        "resident_first_name": resident.first_name,
        "resident_last_name": resident.last_name,
        "rfid_uid": deactivated_uid,
        "reported_at": report.created_at,
    }


# =================================================================================
# ADMIN — RFID REPORTS
# =================================================================================

def get_all_rfid_reports(db: Session) -> list:
    reports = (
        db.query(RFIDReport)
        .options(joinedload(RFIDReport.resident).joinedload(Resident.rfids))
        .order_by(RFIDReport.created_at.desc())
        .all()
    )

    result = []
    for r in reports:
        all_rfids = sorted(r.resident.rfids, key=lambda x: x.created_at, reverse=True) if r.resident else []
        last_rfid = all_rfids[0].rfid_uid if all_rfids else None

        result.append({
            "id": r.id,
            "resident_id": r.resident_id,
            "resident_first_name": r.resident.first_name if r.resident else None,
            "resident_last_name": r.resident.last_name if r.resident else None,
            "rfid_uid": last_rfid,
            "status": r.status,
            "reported_at": r.created_at,
        })

    return result


def undo_rfid_report(db: Session, report_id: int) -> dict:
    report = (
        db.query(RFIDReport)
        .options(joinedload(RFIDReport.resident).joinedload(Resident.rfids))
        .filter(RFIDReport.id == report_id)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if not report.resident:
        raise HTTPException(status_code=400, detail="No resident linked to this report")

    inactive_rfids = sorted(
        [r for r in report.resident.rfids if not r.is_active],
        key=lambda x: x.created_at,
        reverse=True
    )
    if not inactive_rfids:
        raise HTTPException(
            status_code=400,
            detail="No deactivated RFID card found to restore for this resident."
        )

    card_to_restore = inactive_rfids[0]
    card_to_restore.is_active = True
    report.status = "Resolved"

    db.commit()

    return {"success": True, "rfid_uid": card_to_restore.rfid_uid}


def delete_rfid_report(db: Session, report_id: int) -> bool:
    report = db.query(RFIDReport).filter(RFIDReport.id == report_id).first()
    if not report:
        return False
    db.delete(report)
    db.commit()
    return True


def bulk_delete_rfid_reports(db: Session, ids: list[int]) -> int:
    count = db.query(RFIDReport).filter(RFIDReport.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count


# =================================================================================
# ADMIN — ID APPLICATION
# =================================================================================

def get_all_id_applications(db: Session) -> list:
    requests = (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident).joinedload(Resident.rfids),
            joinedload(DocumentRequest.barangay_id),
        )
        .filter(DocumentRequest.doctype_id.is_(None))
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )

    result = []
    for req in requests:
        fd = req.form_data or {}
        session_rfid = fd.get("session_rfid", "Guest Mode")
        brgy_id_number = fd.get("brgy_id_number") or (
            req.barangay_id.brgy_id_number if req.barangay_id else None
        )

        result.append({
            "id": req.id,
            "transaction_no": req.transaction_no,
            "resident_id": req.resident_id,
            "resident_first_name": req.resident.first_name if req.resident else None,
            "resident_last_name": req.resident.last_name if req.resident else None,
            "resident_rfid": session_rfid,
            "brgy_id_number": brgy_id_number,
            "requested_at": req.requested_at,
            "status": req.status,
            "payment_status": req.payment_status,
        })

    return result

# =================================================================================
# ELIGIBILITY CHECKS
# =================================================================================

def check_id_requirements(db: Session, resident_id: int) -> dict:
    doc_type = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    if not doc_type:
        return {"eligible": True, "checks": []}

    requirements = doc_type.requirements or []
    if not requirements:
        return {"eligible": True, "checks": []}

    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")

    today = date.today()
    checks = []
    all_passed = True

    for req in requirements:
        req_id    = req.get("id", "unknown")
        req_label = req.get("label", req_id)
        req_type  = req.get("type", "document")
        params    = req.get("params") or {}

        if req_type == "document":
            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "document",
                "passed":  None,
                "message": "Must be presented at the barangay hall.",
            })
            continue

        if req_type != "system_check":
            continue

        if req_id == "clean_blotter":
            continue

        if req_id == "min_age":
            min_years = params.get("years", 0)
            age = (
                today.year - resident.birthdate.year
                - ((today.month, today.day) < (resident.birthdate.month, resident.birthdate.day))
            ) if resident.birthdate else None

            if age is None:
                passed = False
                message = "Birthdate not on record — age cannot be verified."
            else:
                passed = age >= min_years
                message = (
                    f"Must be at least {min_years} year{'s' if min_years != 1 else ''} old. "
                    f"Applicant is {age} year{'s' if age != 1 else ''} old. "
                    + ("✓ Passed." if passed else "✗ Requirement not met.")
                )

            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "system_check",
                "passed":  passed,
                "message": message,
            })
            if not passed:
                all_passed = False

        elif req_id == "min_residency":
            years_required  = params.get("years", 0)
            months_required = params.get("months", 0)

            if not resident.residency_start_date:
                passed = False
                message = "Residency start date not on record."
            else:
                total_months = (
                    (today.year  - resident.residency_start_date.year)  * 12
                    + (today.month - resident.residency_start_date.month)
                )
                if today.day < resident.residency_start_date.day:
                    total_months -= 1
                required_months = years_required * 12 + months_required
                passed = total_months >= required_months

                parts = []
                if years_required:
                    parts.append(f"{years_required} year{'s' if years_required != 1 else ''}")
                if months_required:
                    parts.append(f"{months_required} month{'s' if months_required != 1 else ''}")
                duration = " and ".join(parts) or "required duration"
                actual_years  = total_months // 12
                actual_months = total_months % 12
                actual_parts  = []
                if actual_years:
                    actual_parts.append(f"{actual_years} year{'s' if actual_years != 1 else ''}")
                if actual_months:
                    actual_parts.append(f"{actual_months} month{'s' if actual_months != 1 else ''}")
                actual_str = " and ".join(actual_parts) or "less than 1 month"
                message = (
                    f"Minimum {duration} of residency required. "
                    f"Resident has been registered for {actual_str}. "
                    + ("✓ Passed." if passed else "✗ Requirement not met.")
                )

            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "system_check",
                "passed":  passed,
                "message": message,
            })
            if not passed:
                all_passed = False

        elif req_id == "recent_id_request":
            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "system_check",
                "passed":  None,
                "message": "Automatic check not yet available. Staff will verify manually.",
            })

        else:
            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "system_check",
                "passed":  None,
                "message": f"Unknown check '{req_id}' — skipped.",
            })

    return {"eligible": all_passed, "checks": checks}


# =================================================================================
# ADMIN — TEMPLATE PREVIEW
# =================================================================================

def preview_id_template(db: Session) -> bytes | None:
    doc_type = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    if not doc_type or not doc_type.file:
        return None

    return _convert_docx_to_pdf(doc_type.file)