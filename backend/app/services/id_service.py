"""
ID Service Layer
----------------
Business logic for the three ID Service workflows:
  1. apply_for_id        — creates a DocumentRequest of the special "ID Application" type
  2. change_pin          — verifies current PIN then stores a new bcrypt hash
  3. report_lost_card    — verifies PIN, deactivates RFID, creates an RFIDReport row

Helper utilities:
  - search_residents_by_name
  - verify_resident_birthdate
  - get_rfid_report_card_info
  - get_all_rfid_reports  (admin dashboard)
  - get_all_id_applications (admin dashboard, thin wrapper around DocumentRequest)

Release logic:
  - release_id_application — generates brgy_id_number, fills docx template,
                              creates BarangayID row, stores filled file
"""

import random
import subprocess
import tempfile
import os
import platform
from io import BytesIO
from datetime import date, datetime
from pathlib import Path
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from passlib.context import CryptContext
from docxtpl import DocxTemplate
import base64

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


def _generate_id_pdf(template_bytes: bytes, context: dict) -> bytes:
    """
    Renders the ID Application docx template using docxtpl (Jinja2 {{ var }} syntax)
    and converts it to PDF via LibreOffice.

    Photo is passed as a docxtpl InlineImage — the template must use
    {{ photo }} where the image should appear.
    """
    from docxtpl import InlineImage
    from docx.shared import Mm

    tpl = DocxTemplate(BytesIO(template_bytes))

    # Bind the InlineImage to this specific DocxTemplate instance
    if context.get("photo") is not None:
        photo_bytes = context["photo"]  # raw bytes stored earlier
        if isinstance(photo_bytes, bytes):
            context["photo"] = InlineImage(tpl, BytesIO(photo_bytes), width=Mm(30))

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
# 1. RESIDENT SEARCH  (shared by Apply-for-ID & Report-Lost-Card)
# =========================================================

def get_id_application_fields(db: Session) -> list:
    """
    Kiosk: Returns the admin-configured fields for the ID Application form.
    These are the extra fields the admin added in IDTemplateSettings.
    Returns an empty list if no ID Application doctype exists yet.
    """
    doc_type = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()
    return doc_type.fields or [] if doc_type else []


def search_residents_by_name(db: Session, query: str) -> list[dict]:
    """
    Expects input in the format "LastPrefix, FirstPrefix"
    e.g. "del, max" → matches "del Valle, Maxwell Laurent"

    If only one term is provided (no comma), filters by last name prefix only.
    Result includes whether the resident currently has an active RFID linked.
    """
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
    """
    Checks that the supplied birthdate matches the resident's record.
    Returns True on match, False on mismatch.
    Does NOT raise — the API layer decides how to respond to False.
    """
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
    manual_data=None,
) -> dict:
    """
    Creates a DocumentRequest for an ID Application.

    doctype_id is intentionally NULL — ID Applications are a special built-in
    feature and do not depend on any row in the document_types table.
    The type is identified by form_data["request_type"] = "ID Application".

    resident_id            — the logged-in user (None for guest). Stored as
                             DocumentRequest.resident_id so "Request from" resolves
                             correctly in the admin dashboard (same as other doc types).
                             For guests, falls back to applicant_resident_id so the
                             FK is never NULL.
    applicant_resident_id  — the resident selected via the form. Stored in form_data
                             as request_for_id / request_for_name ("Request for").

    - Saves the base64 photo to the *applicant* resident's profile (residents.photo).
    - Prevents duplicate pending ID applications for the same applicant.
    - Works for both guest (resident_id=None) and authenticated sessions.
    - If use_manual_data=True, manual_data fields are merged into form_data so the
      admin can use them when generating the ID card.
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

    # Build manual data overrides (stored so admin can use them at release time)
    manual_overrides = {}
    if use_manual_data and manual_data:
        manual_overrides = {
            k: v for k, v in manual_data.model_dump().items() if v is not None
        }

    request = DocumentRequest(
        transaction_no=tx_no,
        resident_id=requester_id,   # logged-in user (or applicant for guest)
        doctype_id=None,            # NULL — ID Applications are not a document type
        price=0,
        status="Pending",
        payment_status="unpaid",
        form_data={
            "request_type": ID_APPLICATION_DOCTYPE_NAME,
            # "Request for" — the resident selected via the form
            "request_for_id": applicant_resident_id,
            "request_for_name": f"{applicant.first_name} {applicant.last_name}",
            # Session display helpers
            "session_rfid": display_rfid,
            "requested_date": now.isoformat(),
            # Manual entry overrides (empty dict if DB data was used)
            "use_manual_data": use_manual_data,
            **manual_overrides,
        },
        requested_at=now,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    # Auto-generate PDF from template at submission time (same as regular documents)
    id_doctype = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    if id_doctype and id_doctype.file:
        try:
            # Build context from applicant DB fields + manual overrides
            from sqlalchemy.orm import joinedload as _jl
            applicant_full = (
                db.query(Resident)
                .options(_jl(Resident.addresses))
                .filter(Resident.id == applicant_resident_id)
                .first()
            )
            current_address = next(
                (a for a in (applicant_full.addresses if applicant_full else []) if a.is_current), None
            )
            full_address = (
                f"{current_address.house_no_street}, Purok {current_address.purok_id}, "
                f"{current_address.barangay}, {current_address.municipality}, "
                f"{current_address.province}"
                if current_address else ""
            )

            pdf_context = {
                "last_name":      applicant.last_name,
                "first_name":     applicant.first_name,
                "middle_name":    applicant.middle_name or "",
                "suffix":         applicant.suffix or "",
                "birthdate":      str(applicant.birthdate) if applicant.birthdate else "",
                "address":        full_address,
                "contact_number": applicant.phone_number or "",
                "photo":          bytes(applicant.photo) if applicant.photo else None,
                "brgy_id_number": "",  # not assigned yet at submission time
            }

            # Apply manual overrides if submitted
            for key in ("last_name", "first_name", "middle_name", "birthdate", "address", "contact_number"):
                if manual_overrides.get(key):
                    pdf_context[key] = manual_overrides[key]

            pdf_bytes = _generate_id_pdf(bytes(id_doctype.file), pdf_context)
            relative_path = _save_id_pdf(request.transaction_no, pdf_bytes)
            request.request_file_path = relative_path
            db.commit()
            print(f"✅ ID PDF generated at submission for {request.transaction_no}")
        except Exception as e:
            print(f"❌ ID PDF generation failed at submission for {request.transaction_no}: {str(e)}")

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

    Steps:
      1. Validate the request exists and is in "Approved" status.
      2. Resolve the applicant resident from form_data["request_for_id"].
      3. Build the template context from:
           - Resident DB fields (last_name, first_name, etc.)
           - form_data manual overrides (if use_manual_data=True)
           - residents.photo (bytes, for {{photo}} placeholder)
      4. Generate the next sequential brgy_id_number (00001, 00002, …).
      5. Fill the .docx template stored on the ID Application DocumentType.
      6. Store the filled .docx bytes on DocumentRequest.request_file_path
         (encoded as base64 string so it survives the Text column).
      7. Create a BarangayID row linking resident ↔ request ↔ active RFID.
      8. Mark the DocumentRequest status = "Released".

    Raises:
        404 — request not found
        400 — request is not in "Approved" status
        400 — no ID Application template has been uploaded by admin
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
        .options(joinedload(Resident.rfids), joinedload(Resident.addresses))
        .filter(Resident.id == int(applicant_id))
        .first()
    )
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant resident not found.")

    # ── 3. Build template context ─────────────────────────────────────────────
    # Start from DB fields
    current_address = next(
        (a for a in applicant.addresses if a.is_current), None
    )
    full_address = (
        f"{current_address.house_no_street}, Purok {current_address.purok_id}, "
        f"{current_address.barangay}, {current_address.municipality}, "
        f"{current_address.province}"
        if current_address else ""
    )

    context = {
        "last_name":      applicant.last_name,
        "first_name":     applicant.first_name,
        "middle_name":    applicant.middle_name or "",
        "suffix":         applicant.suffix or "",
        "birthdate":      str(applicant.birthdate) if applicant.birthdate else "",
        "address":        full_address,
        "contact_number": applicant.phone_number or "",
        # Store raw bytes — _generate_id_pdf will bind it as InlineImage
        "photo":          bytes(applicant.photo) if applicant.photo else None,
    }

    # Override with manual_data values if the applicant chose manual entry
    if form_data.get("use_manual_data"):
        manual_keys = [
            "last_name", "first_name", "middle_name",
            "birthdate", "address", "contact_number",
        ]
        for key in manual_keys:
            if form_data.get(key):
                context[key] = form_data[key]

    # ── 4. Generate brgy_id_number ────────────────────────────────────────────
    brgy_id_number = _generate_brgy_id_number(db)
    context["brgy_id_number"] = brgy_id_number

    # ── 5. Generate PDF from template ────────────────────────────────────────
    id_doctype = db.query(DocumentType).filter(
        DocumentType.is_id_application.is_(True)
    ).first()

    if id_doctype and id_doctype.file:
        try:
            pdf_bytes = _generate_id_pdf(bytes(id_doctype.file), context)
            relative_path = _save_id_pdf(req.transaction_no, pdf_bytes)
            req.request_file_path = relative_path
            print(f"✅ ID PDF generated for {req.transaction_no}")
        except Exception as e:
            # PDF failure does not block the release — admin can regenerate manually
            print(f"❌ ID PDF generation failed for {req.transaction_no}: {str(e)}")
    # If no template uploaded, request_file_path stays None — that is fine

    # ── 7. Create BarangayID row ──────────────────────────────────────────────
    # Guard: prevent duplicate active BarangayID for the same resident
    existing_brgy_id = (
        db.query(BarangayID)
        .filter(
            BarangayID.resident_id == applicant.id,
            BarangayID.is_active.is_(True),
        )
        .first()
    )
    if existing_brgy_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This resident already has an active Barangay ID."
        )

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

    # ── 8. Mark the request as Released ──────────────────────────────────────
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
        "has_filled_template": filled_docx_b64 is not None,
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
    Also returns brgy_id_number if a BarangayID row has been created (post-release).
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
        session_rfid = (req.form_data or {}).get("session_rfid", "Guest Mode")
        brgy_id_number = req.barangay_id.brgy_id_number if req.barangay_id else None

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