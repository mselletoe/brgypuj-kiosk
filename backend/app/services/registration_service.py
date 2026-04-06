from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.resident import Resident, ResidentRFID
from app.models.document import DocumentRequest
from app.models.barangayid import BarangayID
from app.services.systemconfig_service import get_config

ADMIN_PASSCODE = "7890"

ID_APPLICATION_DOCTYPE_NAME = "ID Application"


def check_rfid_status(db: Session, rfid_uid: str) -> dict:
    existing = (
        db.query(ResidentRFID)
        .filter(ResidentRFID.rfid_uid == rfid_uid)
        .first()
    )
    return {"is_new": existing is None}


def verify_admin_passcode(passcode: str) -> dict:
    return {"valid": passcode == ADMIN_PASSCODE}


def get_approved_id_applications(db: Session) -> list[dict]:
    applications = (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident)
        )
        .filter(
            DocumentRequest.doctype_id.is_(None), 
            DocumentRequest.status == "Approved", 
        )
        .order_by(DocumentRequest.requested_at.desc())
        .all()
    )

    result = []
    for app in applications:
        form_data = app.form_data or {}
        if form_data.get("rfid_linked"):
            continue

        applicant_id = form_data.get("request_for_id")
        if not applicant_id:
            continue

        applicant = db.query(Resident).filter(Resident.id == int(applicant_id)).first()
        if not applicant:
            continue

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


def link_rfid_to_resident(
    db: Session,
    rfid_uid: str,
    resident_id: int,
    document_request_id: int,
) -> dict:
    duplicate = db.query(ResidentRFID).filter(ResidentRFID.rfid_uid == rfid_uid).first()
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This RFID card is already registered to another resident."
        )

    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found.")

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

    config = get_config(db)
    expiration_date = date.today() + timedelta(days=config.rfid_expiry_days)

    new_rfid = ResidentRFID(
        resident_id=resident_id,
        rfid_uid=rfid_uid,
        is_active=True,
        expiration_date=expiration_date,
        created_at=datetime.now(),
    )
    db.add(new_rfid)
    db.flush() 

    barangay_id_row = (
        db.query(BarangayID)
        .filter(
            BarangayID.request_id == document_request_id,
            BarangayID.is_active.is_(False),
        )
        .first()
    )
    if barangay_id_row:
        barangay_id_row.rfid_id         = new_rfid.id
        barangay_id_row.expiration_date = expiration_date
        barangay_id_row.is_active       = True

    updated_form_data = dict(doc_request.form_data or {})
    updated_form_data["rfid_linked"] = True
    updated_form_data["rfid_uid"] = rfid_uid
    updated_form_data["linked_at"] = datetime.now().isoformat()
    doc_request.form_data = updated_form_data

    db.commit()
    db.refresh(new_rfid)

    brgy_id_number = barangay_id_row.brgy_id_number if barangay_id_row else None

    return {
        "success": True,
        "rfid_uid": rfid_uid,
        "resident_id": resident_id,
        "resident_first_name": resident.first_name,
        "resident_last_name": resident.last_name,
        "transaction_no": doc_request.transaction_no,
        "brgy_id_number": brgy_id_number,
        "expiration_date": str(expiration_date),
        "linked_at": new_rfid.created_at,
    }