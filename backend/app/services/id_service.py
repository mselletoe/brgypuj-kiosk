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
"""

import random
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from passlib.context import CryptContext
import base64
from app.models.resident import Resident, ResidentRFID
from app.models.document import DocumentRequest
from app.models.misc import RFIDReport

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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


# =========================================================
# 1. RESIDENT SEARCH  (shared by Apply-for-ID & Report-Lost-Card)
# =========================================================

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
    # Uses the same filter as apply_for_id's duplicate guard (proven to work).
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
            # Legacy / display helpers
            "session_rfid": display_rfid,
            "requested_date": now.isoformat(),
        },
        requested_at=now,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return {
        "transaction_no": request.transaction_no,
        "resident_first_name": applicant.first_name,
        "resident_last_name": applicant.last_name,
        "requested_at": request.requested_at,
    }


# =========================================================
# 4. CHANGE PIN  (authenticated residents only)
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

    # Guard: resident must have a real PIN already
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
# 5. REPORT LOST CARD
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

    Works for guest sessions too — PIN is still required for identity confirmation
    regardless of whether the request originates from a guest or RFID session.

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

    # PIN verification
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

    # Deactivate the RFID card
    deactivated_uid = active_rfid.rfid_uid
    active_rfid.is_active = False

    # Create the RFIDReport record
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
# 6. ADMIN — LIST REPORTS & ID APPLICATIONS
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
        # Find the most recent RFID UID linked to this resident (even if inactive now)
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
    """
    requests = (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident).joinedload(Resident.rfids)
        )
        .filter(DocumentRequest.doctype_id.is_(None))
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )

    result = []
    for req in requests:
        session_rfid = (req.form_data or {}).get("session_rfid", "Guest Mode")

        result.append({
            "id": req.id,
            "transaction_no": req.transaction_no,
            "resident_id": req.resident_id,
            "resident_first_name": req.resident.first_name if req.resident else None,
            "resident_last_name": req.resident.last_name if req.resident else None,
            "resident_rfid": session_rfid,
            "requested_at": req.requested_at,
            "status": req.status,
            "payment_status": req.payment_status,
        })

    return result

def undo_rfid_report(db: Session, report_id: int) -> dict:
    """
    Admin: Undoes a lost-card report by reactivating the resident's RFID card.
    Sets the most recently deactivated RFID card back to is_active = True
    and marks the RFIDReport record as Resolved.

    Raises:
        404 — report not found
        400 — no deactivated RFID card found to restore
    """
    from fastapi import HTTPException, status as http_status

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

    # Find the most recently deactivated card to reactivate
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

    # Reactivate the card
    card_to_restore = inactive_rfids[0]
    card_to_restore.is_active = True

    # Mark the report resolved
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