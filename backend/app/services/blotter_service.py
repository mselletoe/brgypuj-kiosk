"""
Blotter Service Layer
---------------------------
Handles the business logic for blotter record management within
the Admin Dashboard. Includes creation, retrieval, update, and 
deletion of blotter records.
"""
import random
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.blotter import BlotterRecord
from app.models.resident import Resident
from app.schemas.blotter import BlotterRecordCreate, BlotterRecordUpdate


# -------------------------------------------------
# Internal Helpers
# -------------------------------------------------

def _get_record(db: Session, blotter_id: int) -> BlotterRecord | None:
    return (
        db.query(BlotterRecord)
        .options(joinedload(BlotterRecord.complainant))
        .filter(BlotterRecord.id == blotter_id)
        .first()
    )


def _generate_blotter_no(db: Session) -> str:
    """
    Generates a unique blotter number in the format YYYY-XXXXX.
    Example: 2025-00001, 2025-00042
    """
    from datetime import datetime

    year = datetime.now().year

    # Get the count of blotter records filed this year to determine next sequence
    year_prefix = f"{year}-"
    count = (
        db.query(BlotterRecord)
        .filter(BlotterRecord.blotter_no.like(f"{year_prefix}%"))
        .count()
    )

    while True:
        sequence = count + 1
        blotter_no = f"{year}-{sequence:05d}"
        exists = db.query(BlotterRecord).filter_by(blotter_no=blotter_no).first()
        if not exists:
            return blotter_no
        count += 1


def _validate_resident(db: Session, resident_id: int) -> Resident:
    """
    Ensures the linked resident exists in the database.
    """
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found",
        )
    return resident


# -------------------------------------------------
# Service Functions
# -------------------------------------------------

def get_all_blotter_records(db: Session) -> list[BlotterRecord]:
    """
    Admin: Retrieves all blotter records ordered by most recent first.
    """
    return (
        db.query(BlotterRecord)
        .options(joinedload(BlotterRecord.complainant))
        .order_by(BlotterRecord.created_at.desc())
        .all()
    )


def get_blotter_record_by_id(db: Session, blotter_id: int) -> BlotterRecord | None:
    """
    Admin: Fetches a single blotter record with full complainant details.
    """
    return _get_record(db, blotter_id)


def create_blotter_record(db: Session, payload: BlotterRecordCreate) -> BlotterRecord:
    """
    Admin: Creates a new blotter record with an auto-generated blotter number.
    Optionally links to a registered resident as the complainant.
    """
    if payload.complainant_id:
        _validate_resident(db, payload.complainant_id)

    blotter_no = _generate_blotter_no(db)

    record = BlotterRecord(
        blotter_no=blotter_no,
        **payload.model_dump(),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def update_blotter_record(
    db: Session, blotter_id: int, payload: BlotterRecordUpdate
) -> BlotterRecord | None:
    """
    Admin: Updates fields of an existing blotter record.
    """
    record = _get_record(db, blotter_id)
    if not record:
        return None

    if payload.complainant_id is not None:
        _validate_resident(db, payload.complainant_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record


def delete_blotter_record(db: Session, blotter_id: int) -> bool:
    """
    Admin: Permanently deletes a blotter record.
    """
    record = db.query(BlotterRecord).filter(BlotterRecord.id == blotter_id).first()
    if not record:
        return False

    db.delete(record)
    db.commit()

    return True


def bulk_delete_blotter_records(db: Session, ids: list[int]) -> int:
    """
    Admin: Deletes multiple blotter records in a single operation.
    Returns the count of deleted records.
    """
    count = (
        db.query(BlotterRecord)
        .filter(BlotterRecord.id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.commit()

    return count