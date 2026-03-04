"""
RFID Registration Service Layer
--------------------------------
Business logic for linking a newly scanned (unregistered) RFID card
to an approved ID Application resident.

Workflows:
  1. check_rfid_status    — determines whether a scanned UID is new or already linked
  2. verify_admin_passcode — validates the hardcoded admin passcode gate
  3. get_approved_id_applications — lists approved ID Applications awaiting RFID linking
  4. link_rfid_to_resident — creates a ResidentRFID row and marks the application Completed
"""

from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.resident import Resident, ResidentRFID
from app.models.document import DocumentRequest

# ---------------------------------------------------------------------------
# Admin passcode — stored here for easy rotation.
# In production, move this to an environment variable or a settings table.
# ---------------------------------------------------------------------------
ADMIN_PASSCODE = "7890"

# Matches the sentinel used throughout the codebase
ID_APPLICATION_DOCTYPE_NAME = "ID Application"


# =========================================================
# 1. CHECK RFID STATUS
# =========================================================

def check_rfid_status(db: Session, rfid_uid: str) -> dict:
    """
    Checks whether a scanned RFID UID already exists in the ResidentRFID table.

    Returns:
        { "is_new": True }   — UID is unregistered; proceed to admin passcode → Register
        { "is_new": False }  — UID is already linked; continue with normal auth flow

    The caller (ScanRFID.vue) uses this to decide which route to push.
    This endpoint never raises — it always returns a clean boolean result.
    """
    existing = (
        db.query(ResidentRFID)
        .filter(ResidentRFID.rfid_uid == rfid_uid)
        .first()
    )
    return {"is_new": existing is None}


# =========================================================
# 2. VERIFY ADMIN PASSCODE
# =========================================================

def verify_admin_passcode(passcode: str) -> dict:
    """
    Validates the admin passcode required before accessing the Register screen.

    A simple string comparison is used because this is an offline kiosk context
    and the passcode is an operational gate — not a cryptographic secret.

    Args:
        passcode: The 4-digit code entered on the keypad.

    Returns:
        { "valid": True }  — passcode matches; frontend may proceed to /register
        { "valid": False } — passcode mismatch; frontend should show error

    Raises:
        HTTP 429 — placeholder for future rate-limiting (not yet implemented).
    """
    return {"valid": passcode == ADMIN_PASSCODE}


# =========================================================
# 3. GET APPROVED ID APPLICATIONS  (awaiting RFID linking)
# =========================================================

def get_approved_id_applications(db: Session) -> list[dict]:
    """
    Returns all ID Application DocumentRequests that have been:
      - Approved (status = "Approved")
      - Not yet linked to an RFID card (checked via form_data["rfid_linked"] flag)

    These are the transactions shown in the Register screen left panel so the
    admin can pick the correct one to pair with the freshly scanned card.

    The applicant resident's full details (name, birthdate, address) are
    joined in and returned so the right panel can display them without a
    second API call.
    """
    applications = (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident)
        )
        .filter(
            DocumentRequest.doctype_id.is_(None),          # ID Applications only
            DocumentRequest.status == "Approved",           # Admin-approved
        )
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )

    result = []
    for app in applications:
        # Skip applications that have already been linked to an RFID
        form_data = app.form_data or {}
        if form_data.get("rfid_linked"):
            continue

        # Resolve the applicant resident (the one the ID is FOR)
        applicant_id = form_data.get("request_for_id")
        if not applicant_id:
            continue

        applicant = db.query(Resident).filter(Resident.id == int(applicant_id)).first()
        if not applicant:
            continue

        # Skip residents who already have an active RFID card
        has_active_rfid = any(r.is_active for r in applicant.rfids)
        if has_active_rfid:
            continue

        result.append({
            "transaction_no": app.transaction_no,
            "document_request_id": app.id,
            "resident_id": applicant.id,
            "first_name": applicant.first_name,
            "middle_name": applicant.middle_name,
            "last_name": applicant.last_name,
            "suffix": applicant.suffix,
            "birthdate": str(applicant.birthdate) if applicant.birthdate else None,
            "address": next((f"{a.house_no_street}, Purok {a.purok_id}, {a.barangay}, {a.municipality}, {a.province}" for a in applicant.addresses if a.is_current), None),
            "requested_at": app.requested_at,
        })

    return result


# =========================================================
# 4. LINK RFID TO RESIDENT
# =========================================================

def link_rfid_to_resident(
    db: Session,
    rfid_uid: str,
    resident_id: int,
    document_request_id: int,
) -> dict:
    """
    Completes the RFID registration flow by:
      1. Ensuring the UID is not already in use (race-condition guard).
      2. Creating a new ResidentRFID row (is_active=True).
      3. Flagging form_data["rfid_linked"] = True on the DocumentRequest
         so it disappears from the Register screen's pending list.
      4. Marking the DocumentRequest status as "Completed".

    Args:
        rfid_uid:            The new card's hardware UID from the scanner.
        resident_id:         The applicant resident to link the card to.
        document_request_id: The approved ID Application being fulfilled.

    Returns:
        Confirmation dict with resident name and the new RFID UID.

    Raises:
        409 — UID already registered (another admin registered it first).
        404 — Resident or DocumentRequest not found.
        400 — DocumentRequest is not in Approved status.
    """
    # Guard: prevent duplicate UIDs
    duplicate = db.query(ResidentRFID).filter(ResidentRFID.rfid_uid == rfid_uid).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This RFID card is already registered to another resident."
        )

    # Resolve resident
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found.")

    # Resolve document request
    doc_request = (
        db.query(DocumentRequest)
        .filter(DocumentRequest.id == document_request_id)
        .first()
    )
    if not doc_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ID Application not found."
        )
    if doc_request.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID Application is not in Approved status."
        )

    # Create the RFID record
    new_rfid = ResidentRFID(
        resident_id=resident_id,
        rfid_uid=rfid_uid,
        is_active=True,
        created_at=datetime.now(),
    )
    db.add(new_rfid)

    # Update the DocumentRequest: mark linked and complete
    updated_form_data = dict(doc_request.form_data or {})
    updated_form_data["rfid_linked"] = True
    updated_form_data["rfid_uid"] = rfid_uid
    updated_form_data["linked_at"] = datetime.now().isoformat()
    doc_request.form_data = updated_form_data
    doc_request.status = "Completed"

    db.commit()
    db.refresh(new_rfid)

    return {
        "success": True,
        "rfid_uid": rfid_uid,
        "resident_id": resident_id,
        "resident_first_name": resident.first_name,
        "resident_last_name": resident.last_name,
        "transaction_no": doc_request.transaction_no,
        "linked_at": new_rfid.created_at,
    }