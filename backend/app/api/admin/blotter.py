"""
Blotter Records API
---------------------------
Provides management endpoints for barangay blotter records
within the administrative dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.blotter import (
    BlotterRecordCreate,
    BlotterRecordDetail,
    BlotterRecordOut,
    BlotterRecordUpdate,
)
from app.services.blotter_service import (
    get_all_blotter_records,
    get_blotter_record_by_id,
    create_blotter_record,
    update_blotter_record,
    delete_blotter_record,
    bulk_delete_blotter_records,
)

router = APIRouter(prefix="/blotter")


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def _resolve_party(resident) -> dict:
    """Extracts resolved fields from a linked resident ORM object."""
    if not resident:
        return {
            "first_name": None,
            "middle_name": None,
            "last_name": None,
            "full_name": None,
            "phone": None,
        }
    full_name = " ".join(filter(None, [
        resident.first_name,
        resident.middle_name,
        resident.last_name,
    ]))
    return {
        "first_name": resident.first_name,
        "middle_name": resident.middle_name,
        "last_name": resident.last_name,
        "full_name": full_name,
        "phone": resident.phone_number,
    }


def _format_record(record) -> dict:
    """
    Formats a BlotterRecord ORM object into a dict suitable for response schemas.
    Resolves linked resident details for both complainant and respondent.
    """
    complainant = _resolve_party(record.complainant)
    respondent = _resolve_party(record.respondent)

    return {
        "id": record.id,
        "blotter_no": record.blotter_no,

        "complainant_id": record.complainant_id,
        "complainant_name": record.complainant_name,
        "complainant_age": record.complainant_age,
        "complainant_address": record.complainant_address,
        "complainant_resident_name": complainant["full_name"],
        "complainant_resident_first_name": complainant["first_name"],
        "complainant_resident_middle_name": complainant["middle_name"],
        "complainant_resident_last_name": complainant["last_name"],
        "complainant_resident_phone": complainant["phone"],

        "respondent_id": record.respondent_id,
        "respondent_name": record.respondent_name,
        "respondent_age": record.respondent_age,
        "respondent_address": record.respondent_address,
        "respondent_resident_name": respondent["full_name"],
        "respondent_resident_first_name": respondent["first_name"],
        "respondent_resident_middle_name": respondent["middle_name"],
        "respondent_resident_last_name": respondent["last_name"],
        "respondent_resident_phone": respondent["phone"],

        "incident_date": record.incident_date,
        "incident_time": record.incident_time,
        "incident_place": record.incident_place,
        "incident_type": record.incident_type,
        "narrative": record.narrative,
        "recorded_by": record.recorded_by,
        "contact_no": record.contact_no,
        "created_at": record.created_at,
    }


# =========================================================
# BLOTTER RECORDS
# =========================================================

@router.get("", response_model=list[BlotterRecordOut])
def list_blotter_records(db: Session = Depends(get_db)):
    """
    Retrieves all blotter records ordered by most recently filed.
    """
    records = get_all_blotter_records(db)
    return [_format_record(r) for r in records]


@router.post("", response_model=BlotterRecordOut, status_code=status.HTTP_201_CREATED)
def create_record(payload: BlotterRecordCreate, db: Session = Depends(get_db)):
    """
    Files a new blotter record. Automatically generates a unique blotter number.
    Optionally links complainant and/or respondent to registered residents.
    """
    record = create_blotter_record(db, payload)
    return _format_record(record)


@router.get("/{blotter_id}", response_model=BlotterRecordDetail)
def get_record(blotter_id: int, db: Session = Depends(get_db)):
    """
    Fetches the full details of a specific blotter record.
    """
    record = get_blotter_record_by_id(db, blotter_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blotter record not found")
    return _format_record(record)


@router.put("/{blotter_id}", response_model=BlotterRecordOut)
def update_record(blotter_id: int, payload: BlotterRecordUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing blotter record. All fields are optional.
    """
    record = update_blotter_record(db, blotter_id, payload)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blotter record not found")
    return _format_record(record)


@router.delete("/{blotter_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(blotter_id: int, db: Session = Depends(get_db)):
    """
    Permanently removes a blotter record from the system.
    """
    deleted = delete_blotter_record(db, blotter_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blotter record not found")


@router.post("/bulk-delete")
def bulk_delete_records(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    """
    Deletes multiple blotter records in a single operation.
    """
    deleted_count = bulk_delete_blotter_records(db, ids)
    return {"detail": f"{deleted_count} blotter records deleted"}