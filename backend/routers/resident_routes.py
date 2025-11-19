"""
================================================================================
File: resident_routes.py
...
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
import models
import schemas

# =============================================
# Initialize Router
# =============================================
router = APIRouter(prefix="/residents", tags=["Residents"])

# ==============================================================================
# ROUTE: Filter Residents (Your Existing Route)
# ==============================================================================
@router.get("/filter")
def get_filtered_residents(
    last_letter: str = Query(..., min_length=1, max_length=1),
    first_letter: str = Query(..., min_length=1, max_length=1),
    db: Session = Depends(get_db)
):
    """
    Retrieve residents whose first and last names start with specific letters.
    ...
    """
    
    # Query database for matching residents
    residents = (
        db.query(models.Resident)
        .filter(models.Resident.last_name.ilike(f"{last_letter}%"))
        .filter(models.Resident.first_name.ilike(f"{first_letter}%"))
        .all()
    )

    # Format Output
    result = []
    for resident in residents:
        # Check whether this resident already has an assigned RFID
        has_rfid = (
            db.query(models.RfidUID)
            .filter(models.RfidUID.resident_id == resident.id)
            .first()
            is not None
        )

        # Combine and clean up resident data for output
        result.append({
            "id": resident.id,
            "name": f"{resident.first_name} {resident.middle_name or ''} {resident.last_name}".strip(),
            "birthdate": resident.birthdate,
            "address": resident.address.unit_blk_street if resident.address else None,
            "has_rfid": has_rfid
        })

    return result

# ==============================================================================
# ROUTE: Get Available Residents for Staff Creation (NEW Route - Added Back)
# ==============================================================================
@router.get("/available-staff", response_model=List[schemas.ResidentSimple])
def get_available_residents_for_staff(db: Session = Depends(get_db)):
    """
    Get a list of residents who are not already registered as BrgyStaff.
    This is used for populating the 'Create Account' dropdown.
    """
    
    # Find all resident IDs that are already in the brgy_staff table
    staff_resident_ids_query = db.query(models.BrgyStaff.resident_id).filter(models.BrgyStaff.resident_id != None)
    
    # Find all residents whose IDs are NOT IN the list of staff resident IDs
    available_residents = db.query(models.Resident).filter(
        ~models.Resident.id.in_(staff_resident_ids_query)
    ).all()
    
    return available_residents