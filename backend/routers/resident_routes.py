from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Resident, RfidUID 

router = APIRouter(prefix="/residents", tags=["Residents"])

@router.get("/filter")
def get_filtered_residents(
    last_letter: str = Query(..., min_length=1, max_length=1),
    first_letter: str = Query(..., min_length=1, max_length=1),
    db: Session = Depends(get_db)
):
    # Query residents whose first and last names start with selected letters
    residents = (
        db.query(Resident)
        .filter(Resident.last_name.ilike(f"{last_letter}%"))
        .filter(Resident.first_name.ilike(f"{first_letter}%"))
        .all()
    )

    # Prepare list for dropdown (formatted full names)
    result = []
    for resident in residents:
        # Check if this resident already has RFID
        has_rfid = (
            db.query(RfidUID)
            .filter(RfidUID.resident_id == resident.id)
            .first()
            is not None
        )

        result.append({
            "id": resident.id,
            "name": f"{resident.first_name} {resident.middle_name or ''} {resident.last_name}".strip(),
            "birthdate": resident.birthdate,
            "address": resident.address.unit_blk_street if resident.address else None,
            "has_rfid": has_rfid
        })

    return result