from datetime import date
from sqlalchemy.orm import Session, joinedload
from app.models.resident import Resident, Address, ResidentRFID
from typing import List, Optional

def get_all_residents(db: Session) -> List[Resident]:
    """
    Fetch all residents from the database.
    """
    return db.query(Resident).order_by(Resident.last_name, Resident.first_name).all()

def get_resident_by_id(db: Session, resident_id: int) -> Resident:
    """
    Fetch a single resident by ID.
    """
    return db.query(Resident).filter(Resident.id == resident_id).first()

def calculate_age(birthdate: date) -> int:
    """
    Calculate age from birthdate
    """
    today = date.today()
    age = today.year - birthdate.year
    
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    
    return age

def calculate_years_of_residency(residency_start_date: date) -> int:
    """
    Calculate years of residency from start date
    """
    today = date.today()
    years = today.year - residency_start_date.year
    
    # Adjust if anniversary hasn't occurred this year
    if (today.month, today.day) < (residency_start_date.month, residency_start_date.day):
        years -= 1
    
    return max(0, years)  # Don't return negative years

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