from pydantic import BaseModel
from datetime import date
from typing import Optional

class ResidentBase(BaseModel):
    first_name: str
    last_name: str
    middle_name: Optional[str]
    suffix: Optional[str]
    gender: str
    birthdate: date
    email: Optional[str]
    phone_number: Optional[str]

class ResidentCreate(ResidentBase):
    pass

class ResidentResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    middle_name: Optional[str]
    suffix: Optional[str]
    gender: str
    birthdate: date
    email: Optional[str]
    phone_number: Optional[str]

    model_config = {
        "from_attributes": True
    }

class ResidentAutofillOut(BaseModel):
    """
    Comprehensive resident data for form autofill.
    All fields are optional to handle incomplete resident profiles.
    """
    # Personal Information
    full_name: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    gender: str
    birthdate: str  # Formatted as MM/DD/YYYY
    age: int
    
    # Contact Information
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Address Information
    unit_blk_street: Optional[str] = None
    purok_name: Optional[str] = None
    barangay: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    full_address: Optional[str] = None
    
    # Residency Information
    years_residency: int
    residency_start_date: str  # Formatted as MM/DD/YYYY
    
    # RFID Information
    rfid_uid: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }