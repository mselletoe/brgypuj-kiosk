"""
ID Service Layer
----------------
Business logic for the three ID Service workflows:
  1. apply_for_id        — creates a DocumentRequest of the special "ID Application" type
  2. change_pin          — verifies current PIN then stores a new bcrypt hash
  3. report_lost_card    — verifies PIN, deactivates RFID, creates an RFIDReport row

MODIFIED:
- apply_for_id now accepts `field_values: dict` (replaces manual_data/IDManualFormData).
  All form field values are stored flat in form_data alongside metadata keys.
  brgy_id_number is generated at apply time and stored in form_data.
  PDF is generated immediately at apply time (same as document_service).
- release_id_application no longer generates brgy_id_number or the PDF.
  It only creates the BarangayID row and marks the request as Released.
  Template context is built purely from form_data (minus metadata keys) —
  no hardcoded DB field injections.
"""

import random
import subprocess
import tempfile
import os
import platform
from io import BytesIO
from PIL import Image, ImageDraw
from datetime import date, datetime
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from passlib.context import CryptContext
from docxtpl import DocxTemplate
import base64
from app.db.session import SessionLocal
from app.models.resident import Resident, ResidentRFID
from app.models.document import DocumentRequest, DocumentType
from app.models.barangayid import BarangayID
from app.models.misc import RFIDReport

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_STORAGE_DIR = BASE_DIR / "storage" / "documents"

# -----------------------------------------------------------------------
# The document type that represents an "ID Application".
# This name MUST match exactly what is stored in the document_types table.
# -----------------------------------------------------------------------
ID_APPLICATION_DOCTYPE_NAME = "ID Application"

# Sentinel PIN set during migration (no real PIN configured yet)
RFID_PIN_DEFAULT = "0000"

# Metadata keys stored in form_data that must NOT be passed to the docx template
_FORM_DATA_META_KEYS = {
    "request_type",
    "request_for_id",
    "request_for_name",
    "session_rfid",
    "requested_date",
    "use_manual_data",
}


# =========================================================
# INTERNAL HELPERS
# =========================================================

def _get_resident_or_404(db: Session, resident_id: int) -> Resident:
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    return resident


def _get_active_rfid(resident: Resident) -> ResidentRFID | None:
    """Returns the currently active RFID record for a resident, or None."""
    return next((r for r in resident.rfids if r.is_active), None)


def _generate_transaction_no(db: Session) -> str:
    """Unique transaction number in the format ID-XXXX."""
    while True:
        number = random.randint(1000, 9999)
        tx_no = f"ID-{number}"
        exists = db.query(DocumentRequest).filter_by(transaction_no=tx_no).first()
        if not exists:
            return tx_no


def _generate_brgy_id_number(db: Session) -> str:
    """
    Generates the next sequential Barangay ID number in the format XXXXX.
    Finds the current MAX and increments by 1.  First card → "00001".
    """
    max_number = db.query(func.max(BarangayID.brgy_id_number)).scalar()
    if max_number is None:
        next_number = 1
    else:
        try:
            next_number = int(max_number) + 1
        except (ValueError, TypeError):
            next_number = 1
    return str(next_number).zfill(5)


def _convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    """
    Convert DOCX bytes to PDF bytes using LibreOffice.
    Identical to document_service._convert_docx_to_pdf.
    """
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
    """
    Crops photo_bytes into a circle and returns PNG bytes.
    The output is a square PNG with the face masked to a circle
    and a transparent background (alpha channel).
    """
    img = Image.open(BytesIO(photo_bytes)).convert("RGBA")

    # Crop to square from center
    w, h = img.size
    min_side = min(w, h)
    left = (w - min_side) // 2
    top = (h - min_side) // 2
    img = img.crop((left, top, left + min_side, top + min_side))
    img = img.resize((size, size), Image.LANCZOS)

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # Apply mask as alpha
    result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    result.paste(img, (0, 0), mask=mask)

    out = BytesIO()
    result.save(out, format="PNG")
    return out.getvalue()


def _generate_id_pdf(template_bytes: bytes, context: dict) -> bytes:
    """
    Renders the ID Application docx template using docxtpl (Jinja2 {{ var }} syntax)
    and converts it to PDF via LibreOffice.

    Photo is passed as a docxtpl InlineImage — the template must use
    {{ photo }} where the image should appear. The photo is automatically
    cropped into a circle before rendering.
    """
    from docxtpl import InlineImage
    from docx.shared import Mm

    tpl = DocxTemplate(BytesIO(template_bytes))

    # Bind the InlineImage to this specific DocxTemplate instance
    if context.get("photo") is not None:
        photo_bytes = context["photo"]  # raw bytes stored earlier
        if isinstance(photo_bytes, bytes):
            circle_bytes = _make_circle_photo(photo_bytes)
            context["photo"] = InlineImage(tpl, BytesIO(circle_bytes), width=Mm(25))

    tpl.render(context)

    docx_stream = BytesIO()
    tpl.save(docx_stream)
    docx_bytes = docx_stream.getvalue()

    return _convert_docx_to_pdf(docx_bytes)


def _save_id_pdf(transaction_no: str, pdf_bytes: bytes) -> str:
    """
    Saves the generated PDF to storage/documents/YYYY/MM/<transaction_no>.pdf.
    Returns the relative POSIX path for DocumentRequest.request_file_path.
    """
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")

    output_dir = PDF_STORAGE_DIR / year / month
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"{transaction_no}.pdf"
    with open(file_path, "wb") as f:
        f.write(pdf_bytes)

    return str(file_path.relative_to(BASE_DIR).as_posix())


# =========================================================
# PUBLIC: GENERATE BRGY ID NUMBER
# Called by the kiosk before the details phase so the number
# can be displayed on the camera screen and passed in field_values.
# =========================================================

def generate_brgy_id_number(db: Session) -> str:
    """
    Public wrapper around _generate_brgy_id_number.
    Returns the next sequential brgy_id_number without persisting anything.
    The frontend calls this when entering the details phase so the number
    can be shown on the camera screen and submitted with the application.
    """
    return _generate_brgy_id_number(db)


# =========================================================
# 1. RESIDENT SEARCH  (shared by Apply-for-ID & Report-Lost-Card)
# =========================================================

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

    # For each resident, check if they already have a pending ID application.
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


# =========================================================
# 2. BIRTHDATE VERIFICATION  (step 1 of Apply-for-ID)
# =========================================================

def verify_resident_birthdate(db: Session, resident_id: int, birthdate) -> bool:
    resident = _get_resident_or_404(db, resident_id)
    return resident.birthdate == birthdate


# =========================================================
# 3. APPLY FOR ID
# =========================================================

def apply_for_id(
    db: Session,
    resident_id: int | None,
    applicant_resident_id: int,
    rfid_uid: str | None,
    photo: str | None,
    use_manual_data: bool = False,
    field_values: dict = {},
) -> dict:
    """
    Creates a pending ID application DocumentRequest.

    field_values contains all admin-configured form field values
    (either autofilled from DB or manually entered by the user).
    They are stored flat in form_data and used directly as docx
    template placeholders at release time — no hardcoded field names.

    brgy_id_number is generated here and stored in form_data so it
    is available for template rendering at release time.
    """

    # Resolve the applicant (the resident the ID is being made for)
    applicant = _get_resident_or_404(db, applicant_resident_id)

    # Resolve the requester (the logged-in user, or fall back to applicant for guest)
    requester_id = resident_id if resident_id is not None else applicant_resident_id
    requester = _get_resident_or_404(db, requester_id)

    # Guard: one pending ID application per applicant at a time
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

    # Save photo to the applicant's profile if provided
    # Frontend sends a base64 data URL: "data:image/png;base64,<data>"
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

    # Resolve RFID display for the admin table
    # Priority: session RFID → requester's active RFID → "Guest Mode"
    active_rfid = _get_active_rfid(requester)
    display_rfid = rfid_uid or (active_rfid.rfid_uid if active_rfid else None) or "Guest Mode"

    tx_no = _generate_transaction_no(db)
    now = datetime.now()

    # Generate brgy_id_number now so it's available as a template placeholder
    brgy_id_number = _generate_brgy_id_number(db)

    # Fetch ID Application DocumentType once — used for both price and PDF generation
    id_doctype = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    request = DocumentRequest(
        transaction_no=tx_no,
        resident_id=requester_id,   # logged-in user (or applicant for guest)
        doctype_id=None,            # NULL — ID Applications are not a document type
        price=id_doctype.price if id_doctype else 0,  # read from DB, not hardcoded
        status="Pending",
        payment_status="unpaid",
        form_data={
            # ── Metadata (stripped at template-render time) ──────────────
            "request_type":    ID_APPLICATION_DOCTYPE_NAME,
            "request_for_id":  applicant_resident_id,
            "request_for_name": f"{applicant.first_name} {applicant.last_name}",
            "session_rfid":    display_rfid,
            "requested_date":  now.isoformat(),
            "use_manual_data": use_manual_data,
            # ── Template placeholders ────────────────────────────────────
            "brgy_id_number":  brgy_id_number,
            **field_values,    # all admin-configured fields, keyed by field name
        },
        requested_at=now,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    # ── Create BarangayID row immediately (is_active=False until released) ────
    # This ensures brgy_id_number is reserved in barangay_ids at application
    # time. is_active is set to True only when admin releases the application.
    barangay_id_row = BarangayID(
        resident_id=applicant.id,
        rfid_id=None,               # RFID not linked yet — set on release
        request_id=request.id,
        brgy_id_number=brgy_id_number,
        issued_date=date.today(),
        expiration_date=None,       # Set on release when RFID is linked
        is_active=False,            # Activated on release
    )
    db.add(barangay_id_row)
    db.commit()

    # ── Generate PDF immediately at application time ──────────────────────────
    # Build template context: strip metadata keys, inject photo separately.
    # id_doctype already fetched above

    if id_doctype and id_doctype.file:
        try:
            context = {
                k: v for k, v in request.form_data.items()
                if k not in _FORM_DATA_META_KEYS
            }
            # Alias brgy_id_number → id_num for the docx template placeholder
            context["id_num"] = context.get("brgy_id_number", "")
            context["photo"] = bytes(applicant.photo) if applicant.photo else None

            # Build full_name for the template: Lastname, Firstname Middlename
            name_parts = [applicant.first_name]
            if applicant.middle_name:
                name_parts.append(applicant.middle_name)
            context.setdefault("full_name", f"{applicant.last_name}, {' '.join(name_parts)}")
            context.setdefault("last_name", applicant.last_name.upper())

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


# =========================================================
# 4. RELEASE ID APPLICATION  (admin action)
# =========================================================

def release_id_application(db: Session, request_id: int) -> dict:
    """
    Admin: Releases an approved ID application.

    PDF is already generated at application submission time.
    This function only:
      1. Validates the request exists and is in "Approved" status.
      2. Reads brgy_id_number from form_data (generated at apply time).
      3. Guards against duplicate active BarangayID for the same resident.
      4. Creates a BarangayID row linking resident ↔ request ↔ active RFID.
      5. Marks the DocumentRequest status = "Released".

    Raises:
        404 — request not found
        400 — request is not in "Approved" status
        409 — resident already has an active BarangayID
    """
    # ── 1. Fetch the request ──────────────────────────────────────────────────
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

    # ── 2. Resolve applicant resident ────────────────────────────────────────
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

    # ── 3. Read brgy_id_number from form_data (generated at apply time) ───────
    brgy_id_number = form_data.get("brgy_id_number")

    # ── 4. Activate the existing BarangayID row (created at apply time) ───────
    # Link the resident's active RFID and set is_active = True.
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
        # Fallback: create the row if it doesn't exist (old applications)
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

    # ── 5. Mark the request as Released ──────────────────────────────────────
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


# =========================================================
# 5. CHANGE PIN  (authenticated residents only)
# =========================================================

def change_pin(db: Session, resident_id: int, current_pin: str, new_pin: str) -> dict:
    """
    Verifies the resident's current PIN then replaces it with a new bcrypt hash.

    Raises:
        404  — resident not found
        400  — no PIN configured yet (use set-pin instead)
        401  — current PIN mismatch
    """
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


# =========================================================
# 5b. VERIFY PIN  (step 1 of Change Passcode — no mutation)
# =========================================================

def verify_pin(db: Session, resident_id: int, pin: str) -> dict:
    """
    Checks that the supplied PIN matches the resident's stored bcrypt hash
    WITHOUT changing anything.  Used by the Change Passcode flow to gate
    step 1 before the user is allowed to set a new PIN.

    Raises:
        404  — resident not found
        400  — no PIN configured yet
        401  — PIN mismatch
    """
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


# =========================================================
# 6. REPORT LOST CARD
# =========================================================

def get_rfid_report_card_info(db: Session, resident_id: int) -> dict:
    """
    Returns card status info before the resident confirms the report.
    Used to decide whether the "Submit Report" button is enabled.
    """
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
    """
    Confirms the resident's identity via PIN, then:
      1. Marks their active RFID as inactive (is_active = False).
      2. Creates an RFIDReport record visible in the admin Reports dashboard.

    Raises:
        404 — resident not found
        400 — resident has no active RFID linked (nothing to report)
        401 — PIN mismatch
    """
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


# =========================================================
# 7. ADMIN — LIST REPORTS & ID APPLICATIONS
# =========================================================

def get_all_rfid_reports(db: Session) -> list:
    """
    Admin dashboard: returns all RFID lost-card reports with resident info.
    """
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


def get_all_id_applications(db: Session) -> list:
    """
    Admin dashboard: returns all DocumentRequests that are ID Applications.
    Identified by doctype_id IS NULL (set intentionally at submission time).
    brgy_id_number is read from form_data (assigned at application time).
    """
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
        # Read brgy_id_number from form_data (set at apply time)
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


# =========================================================
# 8. ADMIN — UNDO / DELETE RFID REPORTS
# =========================================================

def undo_rfid_report(db: Session, report_id: int) -> dict:
    """
    Admin: Undoes a lost-card report by reactivating the resident's RFID card.
    Sets the most recently deactivated RFID card back to is_active = True
    and marks the RFIDReport record as Resolved.

    Raises:
        404 — report not found
        400 — no deactivated RFID card found to restore
    """
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
    """
    Admin: Hard-deletes an RFID lost-card report record.
    Does NOT reactivate the RFID card — use undo_rfid_report for that.
    """
    report = db.query(RFIDReport).filter(RFIDReport.id == report_id).first()
    if not report:
        return False
    db.delete(report)
    db.commit()
    return True


def bulk_delete_rfid_reports(db: Session, ids: list[int]) -> int:
    """
    Admin: Bulk hard-delete multiple RFID report records.
    Returns the count of deleted records.
    """
    count = db.query(RFIDReport).filter(RFIDReport.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count

def check_id_requirements(db: Session, resident_id: int) -> dict:
    """
    Checks whether a resident meets the requirements configured on the
    ID Application document type.

    Differences from document_service.check_resident_eligibility:
    - Uses the is_id_application=True doctype (no doctype_id param needed).
    - clean_blotter is SKIPPED — not applicable to ID applications.
    - min_age is supported as an additional system_check type.
    - recent_id_request is included but always returns passed=None
      (feature not yet implemented).
    - document-type requirements are returned as informational items.

    Returns a dict with:
      eligible: bool          — False if any hard (system_check) requirement fails.
      checks:   list[dict]    — one entry per requirement with id/label/type/passed/message.
    """
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

        # ── Informational document requirements ───────────────────────────────
        if req_type == "document":
            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "document",
                "passed":  None,
                "message": "Must be presented at the barangay hall.",
            })
            continue

        # ── System checks ─────────────────────────────────────────────────────
        if req_type != "system_check":
            continue

        # clean_blotter — NOT applicable to ID applications; skip silently.
        if req_id == "clean_blotter":
            continue

        # --- min_age ---
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

        # --- min_residency ---
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

        # --- recent_id_request (not yet implemented) ---
        elif req_id == "recent_id_request":
            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "system_check",
                "passed":  None,
                "message": "Automatic check not yet available. Staff will verify manually.",
            })

        # --- unknown system_check ---
        else:
            checks.append({
                "id":      req_id,
                "label":   req_label,
                "type":    "system_check",
                "passed":  None,
                "message": f"Unknown check '{req_id}' — skipped.",
            })

    return {"eligible": all_passed, "checks": checks}


def preview_id_template(db: Session) -> bytes | None:
    """
    Converts the stored ID Application .docx template to PDF bytes
    for inline browser preview. Returns None if no template is uploaded.
    """
    from app.services.document_service import _convert_docx_to_pdf

    doc_type = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    if not doc_type or not doc_type.file:
        return None

    return _convert_docx_to_pdf(doc_type.file)