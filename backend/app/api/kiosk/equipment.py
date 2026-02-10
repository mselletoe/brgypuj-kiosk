"""
Equipment Borrowing API - Kiosk Endpoints
---------------------------
Public-facing endpoints for residents to browse equipment inventory
and submit borrowing requests through the kiosk interface.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.equipment import (
    EquipmentInventoryOut,
    EquipmentRequestCreate,
    EquipmentRequestKioskResponse,
    EquipmentRequestKioskOut,
    EquipmentAutofillData,
)
from app.services import equipment_service

router = APIRouter(prefix="/equipment")


@router.get("/inventory", response_model=List[EquipmentInventoryOut])
def get_available_equipment(db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve all available equipment items for display on the kiosk.
    
    Returns equipment details including:
    - Item name
    - Total quantity owned
    - Available quantity
    - Rate per day
    """
    return equipment_service.get_available_equipment(db)


@router.get("/autofill/{resident_id}", response_model=EquipmentAutofillData)
def get_autofill_data(resident_id: int, db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve resident data for autofilling the borrowing form.
    
    Returns:
    - Borrower name
    - Contact person
    - Contact number
    """
    return equipment_service.get_equipment_autofill_data(db, resident_id)


@router.post("/requests", response_model=EquipmentRequestKioskResponse, status_code=status.HTTP_201_CREATED)
def create_equipment_request(
    payload: EquipmentRequestCreate,
    db: Session = Depends(get_db)
):
    """
    **Kiosk:** Submit a new equipment borrowing request.
    
    Request body should include:
    - resident_id: ID of the logged-in resident (optional for guest mode)
    - contact_person: Person to contact (optional)
    - contact_number: Contact phone number (optional)
    - purpose: Purpose of borrowing (optional)
    - borrow_date: When the equipment will be borrowed
    - return_date: When the equipment will be returned
    - items: List of equipment items with quantities
    - use_autofill: Whether to use resident data for autofill
    
    Returns:
    - transaction_no: Unique identifier for tracking the request
    - total_cost: Total cost of the borrowing
    """
    return equipment_service.create_equipment_request(db, payload)


@router.get("/requests/history/{resident_id}", response_model=List[EquipmentRequestKioskOut])
def get_request_history(resident_id: int, db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve equipment borrowing history for a specific resident.
    
    Returns a list of all equipment requests made by the resident,
    ordered by most recent first.
    """
    return equipment_service.get_kiosk_request_history(db, resident_id)