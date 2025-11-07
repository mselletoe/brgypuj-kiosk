"""
================================================================================
File: resident_routes.py
Description:
    This module defines backend API routes for fetching filtered resident data.

    It provides an endpoint that allows filtering residents by the first and
    last letters of their names. The route is primarily used for search or
    dropdown features where users need to quickly locate residents whose
    names match a pattern.

    Each result also indicates whether the resident already has an assigned
    RFID tag, which helps prevent duplicate assignments in RFID management.
================================================================================
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Resident, RfidUID 

# =============================================
# Initialize Router
# =============================================
router = APIRouter(prefix="/residents", tags=["Residents"])

# ==============================================================================
# ROUTE: Filter Residents by First and Last Name Letters
# ==============================================================================
@router.get("/filter")
def get_filtered_residents(
    last_letter: str = Query(..., min_length=1, max_length=1),
    first_letter: str = Query(..., min_length=1, max_length=1),
    db: Session = Depends(get_db)
):
    """
    Retrieve residents whose first and last names start with specific letters.

    Parameters:
        last_letter (str): First letter of the resident's last name.
        first_letter (str): First letter of the resident's first name.
        db (Session): Active SQLAlchemy session dependency.

    Returns:
        List[dict]: Each dictionary contains:
            - id: Resident ID
            - name: Full name (combined first, middle, last)
            - birthdate: Resident’s date of birth
            - address: Unit/Block/Street info (if available)
            - has_rfid: Boolean indicating if the resident has an RFID tag
    """
    
    # --------------------------------------------
    # Query database for matching residents
    # --------------------------------------------
    residents = (
        db.query(Resident)
        .filter(Resident.last_name.ilike(f"{last_letter}%"))
        .filter(Resident.first_name.ilike(f"{first_letter}%"))
        .all()
    )

    # -------------------------------------------------------------------------
    # Format Output: Build response data for dropdowns / search results
    # -------------------------------------------------------------------------
    result = []
    for resident in residents:
        # Check whether this resident already has an assigned RFID
        has_rfid = (
            db.query(RfidUID)
            .filter(RfidUID.resident_id == resident.id)
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