from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional

class ResidentBase(BaseModel):
    """Base schema with common resident fields"""
    first_name: str = Field(..., min_length=1, max_length=128)
    middle_name: Optional[str] = Field(None, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    suffix: Optional[str] = Field(None, max_length=8)
    gender: str = Field(..., pattern="^(male|female|other)$")
    birthdate: date
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=15)


# ============================================================================
# Request Schemas (Input)
# ============================================================================

class AddressCreate(BaseModel):
    """Schema for creating a new address"""
    house_no_street: str = Field(..., min_length=1, max_length=255)
    purok_id: int = Field(..., gt=0)
    barangay: str = Field(default="Poblacion Uno", max_length=64)
    municipality: str = Field(default="Amadeo", max_length=16)
    province: str = Field(default="Cavite", max_length=16)
    region: str = Field(default="Region IV-A", max_length=64)


class ResidentRFIDCreate(BaseModel):
    """Schema for creating/registering an RFID card"""
    rfid_uid: str = Field(..., min_length=1, max_length=16)
    is_active: bool = Field(default=True)
    expiration_date: Optional[date] = None


class ResidentCreate(ResidentBase):
    """Schema for creating a new resident with address and RFID"""
    residency_start_date: Optional[date] = None  # Defaults to today in service layer
    
    # Nested objects
    address: AddressCreate
    rfid: ResidentRFIDCreate
    photo: Optional[bytes] = None
    
    @field_validator('residency_start_date')
    @classmethod
    def validate_residency_date(cls, v):
        if v and v > date.today():
            raise ValueError('Residency start date cannot be in the future')
        return v
    
    @field_validator('birthdate')
    @classmethod
    def validate_birthdate(cls, v):
        if v > date.today():
            raise ValueError('Birthdate cannot be in the future')
        return v


class ResidentUpdate(BaseModel):
    """Schema for updating resident information (all fields optional)"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=128)
    middle_name: Optional[str] = Field(None, max_length=128)
    last_name: Optional[str] = Field(None, min_length=1, max_length=128)
    suffix: Optional[str] = Field(None, max_length=8)
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    birthdate: Optional[date] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=15)
    residency_start_date: Optional[date] = None
    photo: Optional[bytes] = None
    
    @field_validator('birthdate')
    @classmethod
    def validate_birthdate(cls, v):
        if v and v > date.today():
            raise ValueError('Birthdate cannot be in the future')
        return v


class AddressUpdate(BaseModel):
    """Schema for updating address information"""
    house_no_street: Optional[str] = Field(None, min_length=1, max_length=255)
    purok_id: Optional[int] = Field(None, gt=0)
    barangay: Optional[str] = Field(None, max_length=64)
    municipality: Optional[str] = Field(None, max_length=16)
    province: Optional[str] = Field(None, max_length=16)
    region: Optional[str] = Field(None, max_length=64)


class ResidentRFIDUpdate(BaseModel):
    """Schema for updating RFID information"""
    rfid_uid: Optional[str] = Field(None, min_length=1, max_length=16)
    is_active: Optional[bool] = None
    expiration_date: Optional[date] = None

# ============================================================================
# Response Schemas (Output)
# ============================================================================

class PurokResponse(BaseModel):
    """Schema for Purok information in responses"""
    id: int
    purok_name: str
    
    model_config = {"from_attributes": True}


class AddressResponse(BaseModel):
    """Schema for address information in responses"""
    id: int
    house_no_street: str
    purok_id: int
    purok: Optional[PurokResponse] = None
    barangay: str
    municipality: str
    province: str
    region: str
    is_current: bool
    
    model_config = {"from_attributes": True}


class ResidentRFIDResponse(BaseModel):
    """Schema for RFID information in responses"""
    id: int
    rfid_uid: str
    is_active: bool
    created_at: str
    expiration_date: Optional[date] = None
    
    model_config = {"from_attributes": True}


class ResidentListItem(BaseModel):
    """
    Lightweight schema for resident list (table view).
    Only includes fields needed for the residents table.
    """
    id: int
    full_name: str
    phone_number: Optional[str] = None
    rfid_no: Optional[str] = None
    current_address: Optional[str] = None
    
    model_config = {"from_attributes": True}


class ResidentDetailResponse(BaseModel):
    """
    Complete resident information for detailed view.
    Includes all personal info, address, and RFID details.
    """
    # Basic Info
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    full_name: str
    gender: str
    birthdate: str  # Formatted date
    age: int
    photo: Optional[bytes] = None
    
    # Contact Info
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    # Residency Info
    residency_start_date: str  # Formatted date
    years_of_residency: int
    
    # Address Info (current address only)
    current_address: Optional[AddressResponse] = None
    
    # RFID Info (active RFID only)
    active_rfid: Optional[ResidentRFIDResponse] = None
    
    # Timestamps
    registered_at: str
    
    model_config = {"from_attributes": True}


class ResidentDropdownItem(BaseModel):
    """
    Minimal schema for dropdown selections (e.g., Create Account page).
    Only includes ID and full name.
    """
    id: int
    full_name: str
    
    model_config = {"from_attributes": True}


# ============================================================================
# Autofill Schema (for forms)
# ============================================================================

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