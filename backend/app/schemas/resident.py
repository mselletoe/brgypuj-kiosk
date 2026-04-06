from pydantic import BaseModel, EmailStr, Field, field_validator
from datetime import date
from typing import Optional

class ResidentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=128)
    middle_name: Optional[str] = Field(None, max_length=128)
    last_name: str = Field(..., min_length=1, max_length=128)
    suffix: Optional[str] = Field(None, max_length=8)
    gender: str = Field(..., pattern="^(male|female|other)$")
    birthdate: date
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = Field(None, max_length=15)


class AddressCreate(BaseModel):
    house_no_street: str = Field(..., min_length=1, max_length=255)
    purok_id: int = Field(..., gt=0)
    barangay: str = Field(default="Poblacion I", max_length=64)
    municipality: str = Field(default="Amadeo", max_length=16)
    province: str = Field(default="Cavite", max_length=16)
    region: str = Field(default="Region IV-A", max_length=64)


class ResidentRFIDCreate(BaseModel):
    rfid_uid: str = Field(..., min_length=1, max_length=16)
    is_active: bool = Field(default=True)
    expiration_date: Optional[date] = None


class ResidentCreate(ResidentBase):
    residency_start_date: Optional[date] = None  
    address: AddressCreate
    rfid: Optional[ResidentRFIDCreate] = None
    photo: Optional[bytes] = None
    
    @field_validator('residency_start_date')
    @classmethod
    def validate_residency_date(cls, v):
        from datetime import timezone, timedelta
        if v is None:
            return v
        pht_today = (date.today()) 
        if v > pht_today:
            raise ValueError('Residency start date cannot be in the future')
        return v
    
    @field_validator('birthdate')
    @classmethod
    def validate_birthdate(cls, v):
        if v > date.today():
            raise ValueError('Birthdate cannot be in the future')
        return v


class ResidentUpdate(BaseModel):
    model_config = {"populate_by_name": True}
    
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
    house_no_street: Optional[str] = Field(None, min_length=1, max_length=255)
    purok_id: Optional[int] = Field(None, gt=0)
    barangay: Optional[str] = Field(None, max_length=64)
    municipality: Optional[str] = Field(None, max_length=16)
    province: Optional[str] = Field(None, max_length=16)
    region: Optional[str] = Field(None, max_length=64)


class ResidentRFIDUpdate(BaseModel):
    rfid_uid: Optional[str] = Field(None, min_length=1, max_length=16)
    is_active: Optional[bool] = None
    expiration_date: Optional[date] = None


class PurokResponse(BaseModel):
    id: int
    purok_name: str
    
    model_config = {"from_attributes": True}


class AddressResponse(BaseModel):
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
    id: int
    rfid_uid: str
    is_active: bool
    created_at: str
    expiration_date: Optional[date] = None
    
    model_config = {"from_attributes": True}


class ResidentListItem(BaseModel):
    id: int
    full_name: str
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    rfid_no: Optional[str] = None
    purok_id: Optional[int] = None
    current_address: Optional[str] = None


class ResidentDetailResponse(BaseModel):
    id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    full_name: str
    gender: str
    birthdate: str 
    age: int
    photo: Optional[str] = None    
    
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    residency_start_date: str 
    years_of_residency: int
    residency_months: int = 0  
    residency_label: str = ""  
    
    current_address: Optional[AddressResponse] = None
    
    active_rfid: Optional[ResidentRFIDResponse] = None

    brgy_id_number:          Optional[str] = None
    brgy_id_expiration_date: Optional[str] = None  
    
    registered_at: str
    
    model_config = {"from_attributes": True}


class ResidentDropdownItem(BaseModel):
    id: int
    full_name: str
    
    model_config = {"from_attributes": True}


class ResidentAutofillOut(BaseModel):
    full_name: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    gender: str
    birthdate: str 
    age: int
    
    email: Optional[str] = None
    phone_number: Optional[str] = None
    
    unit_blk_street: Optional[str] = None
    purok_name: Optional[str] = None
    barangay: Optional[str] = None
    municipality: Optional[str] = None
    province: Optional[str] = None
    region: Optional[str] = None
    full_address: Optional[str] = None
    
    years_residency: int
    residency_start_date: str 
    
    rfid_uid: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }