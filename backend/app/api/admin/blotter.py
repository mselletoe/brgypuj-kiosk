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

def _format_record(record) -> dict:
    """
    Formats a BlotterRecord ORM object into a dict suitable for response schemas.
    Resolves the linked resident's name if a complainant_id is present.
    """
    resident_first = None
    resident_middle = None
    resident_last = None
    resident_phone = None
    resident_full_name = None

    if record.complainant:
        resident_first = record.complainant.first_name
        resident_middle = record.complainant.middle_name
        resident_last = record.complainant.last_name
        resident_phone = record.complainant.phone_number
        resident_full_name = " ".join(
            filter(None, [resident_first, resident_middle, resident_last])
        )

    return {
        "id": record.id,
        "blotter_no": record.blotter_no,
        "complainant_id": record.complainant_id,
        "complainant_name": record.complainant_name,
        "complainant_age": record.complainant_age,
        "complainant_address": record.complainant_address,
        "respondent_name": record.respondent_name,
        "respondent_age": record.respondent_age,
        "respondent_address": record.respondent_address,
        "incident_date": record.incident_date,
        "incident_time": record.incident_time,
        "incident_place": record.incident_place,
        "incident_type": record.incident_type,
        "narrative": record.narrative,
        "recorded_by": record.recorded_by,
        "contact_no": record.contact_no,
        "created_at": record.created_at,
        # Resolved resident fields
        "complainant_resident_name": resident_full_name,
        "complainant_resident_first_name": resident_first,
        "complainant_resident_middle_name": resident_middle,
        "complainant_resident_last_name": resident_last,
        "complainant_resident_phone": resident_phone,
    }


# =========================================================
# BLOTTER RECORDS
# =========================================================

@router.get(
    "",
    response_model=list[BlotterRecordOut],
)
def list_blotter_records(db: Session = Depends(get_db)):
    """
    Retrieves all blotter records ordered by most recently filed.
    """
    records = get_all_blotter_records(db)
    return [_format_record(r) for r in records]


@router.post(
    "",
    response_model=BlotterRecordOut,
    status_code=status.HTTP_201_CREATED,
)
def create_record(payload: BlotterRecordCreate, db: Session = Depends(get_db)):
    """
    Files a new blotter record. Automatically generates a unique blotter number.
    Optionally links the complainant to a registered resident via complainant_id.
    """
    record = create_blotter_record(db, payload)
    return _format_record(record)


@router.get(
    "/{blotter_id}",
    response_model=BlotterRecordDetail,
)
def get_record(blotter_id: int, db: Session = Depends(get_db)):
    """
    Fetches the full details of a specific blotter record, including
    linked resident information if available.
    """
    record = get_blotter_record_by_id(db, blotter_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blotter record not found",
        )
    return _format_record(record)


@router.put(
    "/{blotter_id}",
    response_model=BlotterRecordOut,
)
def update_record(
    blotter_id: int,
    payload: BlotterRecordUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates an existing blotter record. All fields are optional,
    allowing partial updates to specific details.
    """
    record = update_blotter_record(db, blotter_id, payload)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blotter record not found",
        )
    return _format_record(record)


@router.delete(
    "/{blotter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_record(blotter_id: int, db: Session = Depends(get_db)):
    """
    Permanently removes a blotter record from the system.
    """
    deleted = delete_blotter_record(db, blotter_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blotter record not found",
        )


@router.post("/bulk-delete")
def bulk_delete_records(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    """
    Deletes multiple blotter records in a single operation.
    Returns the count of successfully deleted records.
    """
    deleted_count = bulk_delete_blotter_records(db, ids)
    return {"detail": f"{deleted_count} blotter records deleted"}