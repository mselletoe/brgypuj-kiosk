"""
Equipment Borrowing Service Schemas
---------------------------
Pydantic models defining the data structures for Equipment Inventory and Borrowing Requests.
These schemas handle data validation for Kiosk submissions and serialization for 
Admin Dashboard management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


# =========================================================
# EQUIPMENT INVENTORY (Managed by Admin, Consumed by Kiosk)
# =========================================================

class EquipmentInventoryBase(BaseModel):
    """
    Base attributes for an equipment item in inventory.
    """
    name: str
    total_quantity: int = Field(ge=0)
    available_quantity: int = Field(ge=0)
    rate_per_day: Decimal = Field(ge=0)

    @field_validator('available_quantity')
    @classmethod
    def validate_available_quantity(cls, v, info):
        """Ensure available quantity doesn't exceed total quantity"""
        if 'total_quantity' in info.data and v > info.data['total_quantity']:
            raise ValueError('Available quantity cannot exceed total quantity')
        return v


# ---------- ADMIN INPUT ----------

class EquipmentInventoryCreate(EquipmentInventoryBase):
    """
    Schema for adding new equipment to inventory via Admin Dashboard.
    """
    pass


class EquipmentInventoryUpdate(BaseModel):
    """
    Schema for updating existing inventory. All fields are optional 
    to support partial updates (PATCH requests).
    """
    name: Optional[str] = None
    total_quantity: Optional[int] = Field(None, ge=0)
    available_quantity: Optional[int] = Field(None, ge=0)
    rate_per_day: Optional[Decimal] = Field(None, ge=0)


# ---------- OUTPUT SCHEMAS ----------

class EquipmentInventoryOut(EquipmentInventoryBase):
    """
    Equipment inventory info for both Kiosk and Admin views.
    Includes the ID for referencing in requests.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# EQUIPMENT BORROWING REQUESTS (Submitted by Residents, Processed by Admin)
# =========================================================

class EquipmentRequestItemInput(BaseModel):
    """
    Individual equipment item in a borrowing request.
    """
    item_id: int
    quantity: int = Field(gt=0)


class EquipmentRequestBase(BaseModel):
    """
    Common fields for all equipment borrowing requests.
    """
    contact_person: Optional[str] = None
    contact_number: Optional[str] = None
    purpose: Optional[str] = None
    borrow_date: datetime
    return_date: datetime
    items: List[EquipmentRequestItemInput] = Field(min_length=1)

    @field_validator('return_date')
    @classmethod
    def validate_return_date(cls, v, info):
        """Ensure return date is after borrow date"""
        if 'borrow_date' in info.data and v <= info.data['borrow_date']:
            raise ValueError('Return date must be after borrow date')
        return v


class EquipmentRequestCreate(EquipmentRequestBase):
    """
    Validation schema for incoming Kiosk submissions.
    Includes the resident_id linked to the authenticated RFID session.
    resident_id can be None for guest mode.
    """
    resident_id: int
    use_autofill: bool = False  # Whether to use resident data for autofill


class EquipmentRequestKioskResponse(BaseModel):
    """
    Immediate feedback for the Kiosk user.
    Returns the unique transaction_no for manual tracking.
    """
    transaction_no: str
    total_cost: Decimal


class EquipmentRequestItemOut(BaseModel):
    """
    Output schema for individual equipment items in a request.
    """
    id: int
    item_id: int
    item_name: str
    quantity: int
    rate_per_day: Decimal

    model_config = ConfigDict(from_attributes=True)


class EquipmentRequestKioskOut(BaseModel):
    """
    Schema for Kiosk transaction history or 'Track My Request' views.
    Filters out internal processing details (like admin IDs).
    """
    transaction_no: str
    status: str
    contact_person: Optional[str]
    contact_number: Optional[str]
    purpose: Optional[str]
    borrow_date: datetime
    return_date: datetime
    total_cost: Decimal
    payment_status: str
    requested_at: datetime
    items: List[EquipmentRequestItemOut]

    model_config = ConfigDict(from_attributes=True)


class EquipmentRequestAdminOut(BaseModel):
    """
    High-level request data for Admin Dashboard list views (Tables).
    Includes identifiers for the resident and detailed item information.
    """
    id: int
    transaction_no: str

    resident_id: Optional[int]
    resident_first_name: Optional[str]
    resident_middle_name: Optional[str]
    resident_last_name: Optional[str]
    resident_rfid: Optional[str]
    resident_phone: Optional[str]

    contact_person: Optional[str]
    contact_number: Optional[str]
    purpose: Optional[str]

    status: str
    borrow_date: datetime
    return_date: datetime
    returned_at: Optional[datetime]
    total_cost: Decimal
    payment_status: str
    is_refunded: bool

    notes: Optional[str]
    requested_at: datetime

    items: List[EquipmentRequestItemOut]

    model_config = ConfigDict(from_attributes=True)


class EquipmentRequestAdminDetail(EquipmentRequestAdminOut):
    """
    Comprehensive request data for the Admin Detail/Processing view.
    Includes the resident's full name and additional processing information.
    """
    resident_name: Optional[str]
    borrowing_period_days: int  # Calculated field

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# AUTOFILL DATA
# =========================================================

class EquipmentAutofillData(BaseModel):
    """
    Schema for autofill data returned to the kiosk.
    Contains resident information pre-filled for convenience.
    """
    contact_person: Optional[str]
    contact_number: Optional[str]