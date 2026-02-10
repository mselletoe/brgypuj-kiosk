from datetime import date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.resident import Resident, Address, ResidentRFID, Purok
from app.schemas.resident import (
    ResidentCreate, 
    ResidentUpdate, 
    AddressUpdate, 
    ResidentRFIDUpdate
)
from typing import List, Optional, Dict


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_age(birthdate: date) -> int:
    """Calculate age from birthdate"""
    today = date.today()
    age = today.year - birthdate.year
    
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    
    return age


def calculate_years_of_residency(residency_start_date: date) -> int:
    """Calculate years of residency from start date"""
    today = date.today()
    years = today.year - residency_start_date.year
    
    # Adjust if anniversary hasn't occurred this year
    if (today.month, today.day) < (residency_start_date.month, residency_start_date.day):
        years -= 1
    
    return max(0, years)  # Don't return negative years


def build_full_name(first_name: str, middle_name: Optional[str], 
                   last_name: str, suffix: Optional[str]) -> str:
    """Build full name from components"""
    name_parts = [first_name]
    if middle_name:
        name_parts.append(middle_name)
    name_parts.append(last_name)
    if suffix:
        name_parts.append(suffix)
    return " ".join(name_parts)


def build_full_address(address: Address) -> str:
    """Build full address string from Address object"""
    address_parts = [
        address.house_no_street,
        address.purok.purok_name if address.purok else None,
        address.barangay,
        address.municipality,
        address.province,
    ]
    return ", ".join(filter(None, address_parts))


# ============================================================================
# CRUD Operations - READ
# ============================================================================

def get_all_residents_list(db: Session) -> List[Dict]:
    """
    Fetch all residents formatted for table list view.
    Returns: List of dicts with id, full_name, phone_number, rfid_no, current_address
    """
    residents = (
        db.query(Resident)
        .options(
            joinedload(Resident.addresses).joinedload(Address.purok),
            joinedload(Resident.rfids)
        )
        .order_by(Resident.last_name, Resident.first_name)
        .all()
    )
    
    result = []
    for resident in residents:
        # Get current address
        current_address = next(
            (addr for addr in resident.addresses if addr.is_current),
            None
        )
        
        # Get active RFID
        active_rfid = next(
            (rfid for rfid in resident.rfids if rfid.is_active),
            None
        )
        
        result.append({
            "id": resident.id,
            "full_name": build_full_name(
                resident.first_name, 
                resident.middle_name, 
                resident.last_name, 
                resident.suffix
            ),
            "phone_number": resident.phone_number,
            "rfid_no": active_rfid.rfid_uid if active_rfid else None,
            "current_address": build_full_address(current_address) if current_address else None
        })
    
    return result


def get_residents_dropdown(db: Session) -> List[Dict]:
    """
    Fetch all residents for dropdown selection (ID and full name only).
    Used in Create Account and other dropdowns.
    Returns: List of dicts with id and full_name
    """
    residents = (
        db.query(Resident)
        .order_by(Resident.last_name, Resident.first_name)
        .all()
    )
    
    return [
        {
            "id": resident.id,
            "full_name": build_full_name(
                resident.first_name,
                resident.middle_name,
                resident.last_name,
                resident.suffix
            )
        }
        for resident in residents
    ]


def get_resident_by_id(db: Session, resident_id: int) -> Optional[Resident]:
    """
    Fetch a single resident by ID with all relationships loaded.
    """
    return (
        db.query(Resident)
        .options(
            joinedload(Resident.addresses).joinedload(Address.purok),
            joinedload(Resident.rfids)
        )
        .filter(Resident.id == resident_id)
        .first()
    )


def get_resident_detail(db: Session, resident_id: int) -> Optional[Dict]:
    """
    Fetch comprehensive resident details for view/edit.
    Returns: Dict with all resident information including computed fields
    """
    resident = get_resident_by_id(db, resident_id)
    
    if not resident:
        return None
    
    # Get current address
    current_address = next(
        (addr for addr in resident.addresses if addr.is_current),
        None
    )
    
    # Get active RFID
    active_rfid = next(
        (rfid for rfid in resident.rfids if rfid.is_active),
        None
    )
    
    # Calculate computed fields
    age = calculate_age(resident.birthdate)
    years_residency = calculate_years_of_residency(resident.residency_start_date)
    
    return {
        # Basic Info
        "id": resident.id,
        "first_name": resident.first_name,
        "middle_name": resident.middle_name,
        "last_name": resident.last_name,
        "suffix": resident.suffix,
        "full_name": build_full_name(
            resident.first_name,
            resident.middle_name,
            resident.last_name,
            resident.suffix
        ),
        "gender": resident.gender,
        "birthdate": resident.birthdate.strftime("%m/%d/%Y"),
        "age": age,
        
        # Contact Info
        "email": resident.email,
        "phone_number": resident.phone_number,
        
        # Residency Info
        "residency_start_date": resident.residency_start_date.strftime("%m/%d/%Y"),
        "years_of_residency": years_residency,
        
        # Address Info
        "current_address": {
            "id": current_address.id,
            "house_no_street": current_address.house_no_street,
            "purok_id": current_address.purok_id,
            "purok": {
                "id": current_address.purok.id,
                "purok_name": current_address.purok.purok_name
            } if current_address.purok else None,
            "barangay": current_address.barangay,
            "municipality": current_address.municipality,
            "province": current_address.province,
            "region": current_address.region,
            "is_current": current_address.is_current
        } if current_address else None,
        
        # RFID Info
        "active_rfid": {
            "id": active_rfid.id,
            "rfid_uid": active_rfid.rfid_uid,
            "is_active": active_rfid.is_active,
            "created_at": active_rfid.created_at.isoformat()
        } if active_rfid else None,
        
        # Timestamps
        "registered_at": resident.registered_at.isoformat()
    }


def get_resident_autofill_data(db: Session, resident_id: int) -> Optional[dict]:
    """
    Fetches comprehensive resident data for form autofill including:
    - Personal information
    - Current address details
    - Active RFID card
    - Computed fields (age, years of residency)
    """
    # Fetch resident with related data
    resident = (
        db.query(Resident)
        .options(
            joinedload(Resident.addresses).joinedload(Address.purok),
            joinedload(Resident.rfids)
        )
        .filter(Resident.id == resident_id)
        .first()
    )
    
    if not resident:
        return None
    
    # Get current address
    current_address = next(
        (addr for addr in resident.addresses if addr.is_current),
        None
    )
    
    # Get active RFID
    active_rfid = next(
        (rfid for rfid in resident.rfids if rfid.is_active),
        None
    )
    
    # Build full name
    name_parts = [resident.first_name]
    if resident.middle_name:
        name_parts.append(resident.middle_name)
    name_parts.append(resident.last_name)
    if resident.suffix:
        name_parts.append(resident.suffix)
    full_name = " ".join(name_parts)
    
    # Build full address
    full_address = None
    if current_address:
        address_parts = [
            current_address.house_no_street,
            current_address.purok.purok_name if current_address.purok else None,
            current_address.barangay,
            current_address.municipality,
            current_address.province,
        ]
        full_address = ", ".join(filter(None, address_parts))
    
    # Calculate computed fields
    age = calculate_age(resident.birthdate)
    years_residency = calculate_years_of_residency(resident.residency_start_date)
    
    # Format birthdate for display
    formatted_birthdate = resident.birthdate.strftime("%m/%d/%Y")
    
    return {
        # Personal Information
        "full_name": full_name,
        "first_name": resident.first_name,
        "middle_name": resident.middle_name,
        "last_name": resident.last_name,
        "suffix": resident.suffix,
        "gender": resident.gender,
        "birthdate": formatted_birthdate,
        "age": age,
        
        # Contact Information
        "email": resident.email,
        "phone_number": resident.phone_number,
        
        # Address Information
        "unit_blk_street": current_address.house_no_street if current_address else None,
        "purok_name": current_address.purok.purok_name if current_address and current_address.purok else None,
        "barangay": current_address.barangay if current_address else None,
        "municipality": current_address.municipality if current_address else None,
        "province": current_address.province if current_address else None,
        "region": current_address.region if current_address else None,
        "full_address": full_address,
        
        # Residency Information
        "years_residency": years_residency,
        "residency_start_date": resident.residency_start_date.strftime("%m/%d/%Y"),
        
        # RFID Information
        "rfid_uid": active_rfid.rfid_uid if active_rfid else None,
    }


# ============================================================================
# CRUD Operations - CREATE
# ============================================================================

def create_resident(db: Session, resident_data: ResidentCreate) -> Resident:
    """
    Create a new resident with address and RFID.
    Validates that RFID UID is unique and purok exists.
    """
    # Set residency_start_date to today if not provided
    residency_start_date = resident_data.residency_start_date or date.today()
    
    # Validate purok exists
    purok = db.query(Purok).filter(Purok.id == resident_data.address.purok_id).first()
    if not purok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purok with ID {resident_data.address.purok_id} not found"
        )
    
    # Check if RFID UID already exists
    existing_rfid = (
        db.query(ResidentRFID)
        .filter(ResidentRFID.rfid_uid == resident_data.rfid.rfid_uid)
        .first()
    )
    if existing_rfid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"RFID UID '{resident_data.rfid.rfid_uid}' is already registered"
        )
    
    # Check if email already exists (if provided)
    if resident_data.email:
        existing_email = (
            db.query(Resident)
            .filter(Resident.email == resident_data.email)
            .first()
        )
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{resident_data.email}' is already registered"
            )
    
    try:
        # Create resident
        new_resident = Resident(
            first_name=resident_data.first_name,
            middle_name=resident_data.middle_name,
            last_name=resident_data.last_name,
            suffix=resident_data.suffix,
            gender=resident_data.gender,
            birthdate=resident_data.birthdate,
            residency_start_date=residency_start_date,
            email=resident_data.email,
            phone_number=resident_data.phone_number
        )
        
        db.add(new_resident)
        db.flush()  # Get the resident ID
        
        # Create address
        new_address = Address(
            resident_id=new_resident.id,
            house_no_street=resident_data.address.house_no_street,
            purok_id=resident_data.address.purok_id,
            barangay=resident_data.address.barangay,
            municipality=resident_data.address.municipality,
            province=resident_data.address.province,
            region=resident_data.address.region,
            is_current=True
        )
        db.add(new_address)
        
        # Create RFID
        new_rfid = ResidentRFID(
            resident_id=new_resident.id,
            rfid_uid=resident_data.rfid.rfid_uid,
            is_active=resident_data.rfid.is_active
        )
        db.add(new_rfid)
        
        db.commit()
        db.refresh(new_resident)
        
        return new_resident
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Please check your input data."
        )


# ============================================================================
# CRUD Operations - UPDATE
# ============================================================================

def update_resident(db: Session, resident_id: int, 
                   resident_data: ResidentUpdate) -> Resident:
    """
    Update resident basic information.
    """
    resident = get_resident_by_id(db, resident_id)
    
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    # Check email uniqueness if being updated
    if resident_data.email and resident_data.email != resident.email:
        existing = db.query(Resident).filter(
            Resident.email == resident_data.email,
            Resident.id != resident_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{resident_data.email}' is already in use"
            )
    
    # Update only provided fields
    update_data = resident_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resident, field, value)
    
    db.commit()
    db.refresh(resident)
    
    return resident


def update_resident_address(db: Session, resident_id: int, 
                           address_data: AddressUpdate) -> Address:
    """
    Update resident's current address.
    """
    resident = get_resident_by_id(db, resident_id)
    
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    # Get current address
    current_address = next(
        (addr for addr in resident.addresses if addr.is_current),
        None
    )
    
    if not current_address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No current address found for this resident"
        )
    
    # Validate purok if being updated
    if address_data.purok_id:
        purok = db.query(Purok).filter(Purok.id == address_data.purok_id).first()
        if not purok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Purok with ID {address_data.purok_id} not found"
            )
    
    # Update only provided fields
    update_data = address_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_address, field, value)
    
    db.commit()
    db.refresh(current_address)
    
    return current_address


def update_resident_rfid(db: Session, resident_id: int, 
                        rfid_data: ResidentRFIDUpdate) -> ResidentRFID:
    """
    Update resident's active RFID.
    """
    resident = get_resident_by_id(db, resident_id)
    
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    # Get active RFID
    active_rfid = next(
        (rfid for rfid in resident.rfids if rfid.is_active),
        None
    )
    
    if not active_rfid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active RFID found for this resident"
        )
    
    # Check UID uniqueness if being updated
    if rfid_data.rfid_uid and rfid_data.rfid_uid != active_rfid.rfid_uid:
        existing = db.query(ResidentRFID).filter(
            ResidentRFID.rfid_uid == rfid_data.rfid_uid,
            ResidentRFID.id != active_rfid.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"RFID UID '{rfid_data.rfid_uid}' is already registered"
            )
    
    # Update only provided fields
    update_data = rfid_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(active_rfid, field, value)
    
    db.commit()
    db.refresh(active_rfid)
    
    return active_rfid


# ============================================================================
# CRUD Operations - DELETE
# ============================================================================

def delete_resident(db: Session, resident_id: int) -> bool:
    """
    Delete a resident and all associated data (cascade).
    Returns True if deleted, raises HTTPException if not found.
    """
    resident = get_resident_by_id(db, resident_id)
    
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    try:
        db.delete(resident)
        db.commit()
        return True
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete resident. They may have related records that prevent deletion."
        )


# ============================================================================
# Utility Functions
# ============================================================================

def get_all_puroks(db: Session) -> List[Purok]:
    """
    Get all puroks for dropdown selections.
    """
    return db.query(Purok).order_by(Purok.purok_name).all()