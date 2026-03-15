"""
app/schemas/document.py

Pydantic schemas for document type configuration and document request management.
Shared across the admin and kiosk document routers.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# =================================================================================
# SHARED
# =================================================================================

class DocumentTypeBase(BaseModel):
    doctype_name: str
    description: Optional[str] = None
    price: Decimal
    fields: List[Dict[str, Any]] = []

class RequirementItem(BaseModel):
    id: str
    label: str
    type: Literal["document", "system_check"]
    params: Optional[Dict[str, Any]] = None
    

# =================================================================================
# DOCUMENT TYPES — CREATE / UPDATE
# =================================================================================
class DocumentTypeCreate(DocumentTypeBase):
    is_available: bool = True
    is_id_application: bool = False


class DocumentTypeUpdate(BaseModel):
    doctype_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    fields: Optional[List[Dict[str, Any]]] = None
    is_available: Optional[bool] = None
    is_id_application: Optional[bool] = None
    requirements: Optional[List[Dict[str, Any]]] = None


# =================================================================================
# DOCUMENT TYPES — RESPONSES
# =================================================================================
class DocumentTypeKioskOut(DocumentTypeBase):
    id: int
    requirements: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)


class DocumentTypeAdminOut(DocumentTypeKioskOut):
    is_available: bool
    is_id_application: bool = False
    has_template: bool

    model_config = ConfigDict(from_attributes=True)


class DocumentTypeProcessingOut(BaseModel):
    id: int
    doctype_name: str
    price: Decimal
    fields: List[Dict[str, Any]]
    file: bytes

    model_config = ConfigDict(from_attributes=True)


# =================================================================================
# ELIGIBILITY
# =================================================================================
class RequirementCheckResult(BaseModel):
    id: str
    label: str
    type: str 
    passed: Optional[bool] = None 
    message: Optional[str] = None 


class EligibilityCheckResult(BaseModel):
    eligible: bool
    resident_id: int
    doctype_id: int
    checks: List[RequirementCheckResult]


# =================================================================================
# DOCUMENT REQUESTS — CREATE
# =================================================================================

class DocumentRequestBase(BaseModel):
    doctype_id: int
    form_data: Dict[str, Any]


class DocumentRequestCreate(DocumentRequestBase):
    resident_id: int


# =================================================================================
# DOCUMENT REQUESTS — RESPONSES
# =================================================================================
class DocumentRequestKioskResponse(BaseModel):
    transaction_no: str


class DocumentRequestKioskOut(BaseModel):
    transaction_no: str
    status: str
    price: Decimal
    payment_status: str
    requested_at: datetime
    doctype_name: str
    price: Decimal
    form_data: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class DocumentRequestAdminOut(BaseModel):
    id: int
    transaction_no: str

    resident_id: Optional[int]
    resident_first_name: Optional[str]
    resident_middle_name: Optional[str]
    resident_last_name: Optional[str]
    resident_rfid: Optional[str]
    resident_phone: Optional[str]
    
    doctype_id: Optional[int]
    doctype_name: str

    status: str
    price: Decimal
    payment_status: str

    form_data: Dict[str, Any]
    notes: Optional[str] = None

    processed_by: Optional[int]
    requested_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentRequestAdminDetail(DocumentRequestAdminOut):
    resident_name: str
    price: Decimal
    request_file_path: Optional[str] = None