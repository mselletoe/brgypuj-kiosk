from sqlalchemy.orm import Session, joinedload
from datetime import datetime, date
from fastapi import HTTPException, status
from app.models.blotter import BlotterRecord
from app.models.resident import Resident, Address
from app.schemas.blotter import BlotterRecordCreate, BlotterRecordUpdate


def _get_record(db: Session, blotter_id: int) -> BlotterRecord | None:
    return (
        db.query(BlotterRecord)
        .options(
            joinedload(BlotterRecord.complainant),
            joinedload(BlotterRecord.respondent),
        )
        .filter(BlotterRecord.id == blotter_id)
        .first()
    )


def _generate_blotter_no(db: Session) -> str:
    year = datetime.now().year
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


def _get_full_name(resident) -> str:
    """Returns the full name of a resident."""
    return " ".join(filter(None, [
        resident.first_name,
        resident.middle_name,
        resident.last_name,
    ]))


def _calculate_age(birthdate) -> int | None:
    if not birthdate:
        return None
    today = date.today()
    return today.year - birthdate.year - (
        (today.month, today.day) < (birthdate.month, birthdate.day)
    )


def _get_resident_address(db: Session, resident_id: int) -> str | None:
    address = (
        db.query(Address)
        .filter(Address.resident_id == resident_id)
        .first()
    )
    if not address:
        return None
    parts = filter(None, [
        getattr(address, 'street', None),
        getattr(address, 'barangay', None),
        getattr(address, 'city', None),
    ])
    return ", ".join(parts) or None


# -------------------------------------------------
# Service Functions
# -------------------------------------------------

def get_all_blotter_records(db: Session) -> list[BlotterRecord]:
    return (
        db.query(BlotterRecord)
        .options(
            joinedload(BlotterRecord.complainant),
            joinedload(BlotterRecord.respondent),
        )
        .order_by(BlotterRecord.created_at.desc())
        .all()
    )


def get_blotter_record_by_id(db: Session, blotter_id: int) -> BlotterRecord | None:
    return _get_record(db, blotter_id)


def get_blotter_records_by_resident(db: Session, resident_id: int) -> list[BlotterRecord]:
    return (
        db.query(BlotterRecord)
        .options(
            joinedload(BlotterRecord.complainant),
            joinedload(BlotterRecord.respondent),
        )
        .filter(
            (BlotterRecord.complainant_id == resident_id) |
            (BlotterRecord.respondent_id == resident_id)
        )
        .order_by(BlotterRecord.created_at.desc())
        .all()
    )


def has_blotter_record_as_respondent(db: Session, resident_id: int) -> bool:
    return (
        db.query(BlotterRecord)
        .filter(
            BlotterRecord.respondent_id == resident_id,
            BlotterRecord.status == "active",
        )
        .first()
    ) is not None


def resolve_blotter_record(db: Session, blotter_id: int) -> BlotterRecord | None:
    from datetime import datetime

    record = _get_record(db, blotter_id)
    if not record:
        return None

    if record.status == "resolved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blotter record is already resolved",
        )

    record.status = "resolved"
    record.resolved_at = datetime.utcnow()

    db.commit()
    db.refresh(record)

    return record


def reopen_blotter_record(db: Session, blotter_id: int) -> BlotterRecord | None:
    record = _get_record(db, blotter_id)
    if not record:
        return None

    if record.status == "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Blotter record is already active",
        )

    record.status = "active"
    record.resolved_at = None

    db.commit()
    db.refresh(record)

    return record


def create_blotter_record(db: Session, payload: BlotterRecordCreate) -> BlotterRecord:
    data = payload.model_dump()

    if payload.complainant_id:
        resident = _validate_resident(db, payload.complainant_id)
        data['complainant_name'] = _get_full_name(resident)
        data['complainant_age'] = _calculate_age(resident.birthdate)
        data['complainant_address'] = _get_resident_address(db, resident.id)

    if payload.respondent_id:
        resident = _validate_resident(db, payload.respondent_id)
        data['respondent_name'] = _get_full_name(resident)
        data['respondent_age'] = _calculate_age(resident.birthdate)
        data['respondent_address'] = _get_resident_address(db, resident.id)

    blotter_no = _generate_blotter_no(db)

    record = BlotterRecord(blotter_no=blotter_no, **data)
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def update_blotter_record( db: Session, blotter_id: int, payload: BlotterRecordUpdate ) -> BlotterRecord | None:
    record = _get_record(db, blotter_id)
    if not record:
        return None

    data = payload.model_dump(exclude_unset=True)

    if data.get('complainant_id'):
        resident = _validate_resident(db, data['complainant_id'])
        data['complainant_name'] = _get_full_name(resident)
        data['complainant_age'] = _calculate_age(resident.birthdate)
        data['complainant_address'] = _get_resident_address(db, resident.id)

    if data.get('respondent_id'):
        resident = _validate_resident(db, data['respondent_id'])
        data['respondent_name'] = _get_full_name(resident)
        data['respondent_age'] = _calculate_age(resident.birthdate)
        data['respondent_address'] = _get_resident_address(db, resident.id)

    for field, value in data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record


def delete_blotter_record(db: Session, blotter_id: int) -> bool:
    record = db.query(BlotterRecord).filter(BlotterRecord.id == blotter_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def bulk_delete_blotter_records(db: Session, ids: list[int]) -> int:
    count = (
        db.query(BlotterRecord)
        .filter(BlotterRecord.id.in_(ids))
        .delete(synchronize_session=False)
    )
    db.commit()
    return count