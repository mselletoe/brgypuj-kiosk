from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    AddressUpdate,
    ResidentRFIDUpdate,
    ResidentListItem,
    ResidentDetailResponse,
    ResidentDropdownItem,
    ResidentAutofillOut,
    PurokResponse
)
from app.services.resident_service import (
    get_all_residents_list,
    get_residents_dropdown,
    get_resident_detail,
    get_resident_autofill_data,
    create_resident,
    update_resident,
    update_resident_address,
    update_resident_rfid,
    delete_resident,
    get_all_puroks
)
from app.api.deps import get_db

router = APIRouter(prefix="/residents")

# ============================================================================
# READ Endpoints
# ============================================================================

@router.get("/", response_model=List[ResidentListItem])
def list_residents(db: Session = Depends(get_db)):
    """
    Get all residents for table display.
    
    Returns list with: id, full_name, phone_number, rfid_no, current_address
    """
    return get_all_residents_list(db)


@router.get("/dropdown", response_model=List[ResidentDropdownItem])
def list_residents_dropdown(db: Session = Depends(get_db)):
    """
    Get all residents for dropdown selection (ID and full name only).
    
    Used in Create Account and other dropdown selections.
    """
    return get_residents_dropdown(db)


@router.get("/{resident_id}", response_model=ResidentDetailResponse)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for a specific resident.
    
    Includes all personal info, address, RFID, and computed fields (age, years of residency).
    """
    resident = get_resident_detail(db, resident_id)
    
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    return resident


@router.get("/{resident_id}/autofill", response_model=ResidentAutofillOut)
def get_resident_autofill(resident_id: int, db: Session = Depends(get_db)):
    """
    Get resident data formatted for form autofill.
    
    Returns comprehensive data including formatted dates and computed fields.
    """
    autofill_data = get_resident_autofill_data(db, resident_id)
    
    if not autofill_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    return autofill_data


# ============================================================================
# CREATE Endpoints
# ============================================================================

@router.post("/", response_model=ResidentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_new_resident(resident_data: ResidentCreate, db: Session = Depends(get_db)):
    """
    Register a new resident with address and RFID.
    
    Required fields:
    - Personal: first_name, last_name, gender, birthdate
    - Address: house_no_street, purok_id
    - RFID: rfid_uid
    
    Optional fields:
    - middle_name, suffix, email, phone_number, residency_start_date
    - is_active for RFID (defaults to true)
    
    Note: residency_start_date defaults to today if not provided
    """
    new_resident = create_resident(db, resident_data)
    
    # Return detailed response
    return get_resident_detail(db, new_resident.id)


# ============================================================================
# UPDATE Endpoints
# ============================================================================

@router.patch("/{resident_id}", response_model=ResidentDetailResponse)
def update_resident_info(
    resident_id: int,
    resident_data: ResidentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update resident's basic information.
    
    All fields are optional. Only provided fields will be updated.
    """
    updated_resident = update_resident(db, resident_id, resident_data)
    
    # Return detailed response
    return get_resident_detail(db, updated_resident.id)


@router.patch("/{resident_id}/address", response_model=ResidentDetailResponse)
def update_resident_address_info(
    resident_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db)
):
    """
    Update resident's current address.
    
    All fields are optional. Only provided fields will be updated.
    """
    update_resident_address(db, resident_id, address_data)
    
    # Return detailed response
    return get_resident_detail(db, resident_id)


@router.patch("/{resident_id}/rfid", response_model=ResidentDetailResponse)
def update_resident_rfid_info(
    resident_id: int,
    rfid_data: ResidentRFIDUpdate,
    db: Session = Depends(get_db)
):
    """
    Update resident's active RFID information.
    
    All fields are optional. Only provided fields will be updated.
    """
    update_resident_rfid(db, resident_id, rfid_data)
    
    # Return detailed response
    return get_resident_detail(db, resident_id)


# ============================================================================
# DELETE Endpoints
# ============================================================================

@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resident_record(resident_id: int, db: Session = Depends(get_db)):
    """
    Delete a resident and all associated data.
    
    This will cascade delete:
    - All addresses
    - All RFID records
    - All feedbacks
    - All RFID reports
    - All document requests
    - All equipment requests
    
    Note: Will fail if resident has admin account (must be deleted separately)
    """
    delete_resident(db, resident_id)
    return None


# ============================================================================
# Utility Endpoints
# ============================================================================

@router.get("/utils/puroks", response_model=List[PurokResponse])
def list_puroks(db: Session = Depends(get_db)):
    """
    Get all puroks for dropdown selections.
    """
    return get_all_puroks(db)