"""
app/schemas/equipment.py

Pydantic schemas for equipment inventory management and borrowing requests.
Shared across the admin and kiosk equipment routers.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# =================================================================================
# SHARED MODELS
# =================================================================================

class EquipmentRequestItemInput(BaseModel):
    item_id:  int
    quantity: int = Field(gt=0)


class EquipmentRequestItemOut(BaseModel):
    id:           int
    item_id:      int
    item_name:    str
    quantity:     int
    rate_per_day: Decimal

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# INVENTORY — CREATE / UPDATE
# =================================================================================

class EquipmentInventoryBase(BaseModel):
    name:               str
    total_quantity:     int     = Field(ge=0)
    available_quantity: int     = Field(ge=0)
    rate_per_day:       Decimal = Field(ge=0)

    @field_validator('available_quantity')
    @classmethod
    def validate_available_quantity(cls, v, info):
        if 'total_quantity' in info.data and v > info.data['total_quantity']:
            raise ValueError('Available quantity cannot exceed total quantity')
        return v


class EquipmentInventoryCreate(EquipmentInventoryBase):
    """Request schema for creating a new equipment inventory item."""
    pass


class EquipmentInventoryUpdate(BaseModel):
    name:               Optional[str]     = None
    total_quantity:     Optional[int]     = Field(None, ge=0)
    available_quantity: Optional[int]     = Field(None, ge=0)
    rate_per_day:       Optional[Decimal] = Field(None, ge=0)


# =================================================================================
# INVENTORY — RESPONSES
# =================================================================================

class EquipmentInventoryOut(EquipmentInventoryBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# EQUIPMENT REQUESTS — CREATE
# =================================================================================

class EquipmentRequestBase(BaseModel):
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    purpose:        Optional[str] = None
    borrow_date:    datetime
    return_date:    datetime
    items:          List[EquipmentRequestItemInput] = Field(min_length=1)

    @field_validator('return_date')
    @classmethod
    def validate_return_date(cls, v, info):
        if 'borrow_date' in info.data and v < info.data['borrow_date']:
            raise ValueError('Return date must be on or after borrow date')
        return v


class EquipmentRequestCreate(EquipmentRequestBase):
    resident_id:  Optional[int] = None
    use_autofill: bool          = False


# =================================================================================
# EQUIPMENT REQUESTS — RESPONSES
# =================================================================================

class EquipmentRequestKioskResponse(BaseModel):
    transaction_no: str
    total_cost:     Decimal


class EquipmentRequestKioskOut(BaseModel):
    transaction_no: str
    status:         str
    contact_person: Optional[str]
    contact_number: Optional[str]
    purpose:        Optional[str]
    borrow_date:    datetime
    return_date:    datetime
    total_cost:     Decimal
    payment_status: str
    requested_at:   datetime
    items:          List[EquipmentRequestItemOut]

    model_config = ConfigDict(from_attributes=True)


class EquipmentRequestAdminOut(BaseModel):
    id:             int
    transaction_no: str

    resident_id:          Optional[int]
    resident_first_name:  Optional[str]
    resident_middle_name: Optional[str]
    resident_last_name:   Optional[str]
    resident_rfid:        Optional[str]
    resident_phone:       Optional[str]

    contact_person: Optional[str]
    contact_number: Optional[str]
    purpose:        Optional[str]

    status:         str
    borrow_date:    datetime
    return_date:    datetime
    returned_at:    Optional[datetime]
    total_cost:     Decimal
    payment_status: str
    is_refunded:    bool

    notes:        Optional[str]
    requested_at: datetime

    items: List[EquipmentRequestItemOut]

    model_config = ConfigDict(from_attributes=True)


class EquipmentRequestAdminDetail(EquipmentRequestAdminOut):
    resident_name:        Optional[str]
    borrowing_period_days: int 

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# AUTOFILL
# =================================================================================

class EquipmentAutofillData(BaseModel):
    contact_person: Optional[str]
    contact_number: Optional[str]