"""
Document Services Schemas
---------------------------
Pydantic models defining the data structures for Document Types and Requests.
These schemas handle data validation for Kiosk submissions and serialization for 
Admin Dashboard management.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


# =========================================================
# DOCUMENT TYPES (Managed by Admin, Consumed by Kiosk)
# =========================================================

class DocumentTypeBase(BaseModel):
    """
    Base attributes for a document template.
    @property fields: List of JSON objects defining dynamic form requirements 
    """
    doctype_name: str
    description: Optional[str] = None
    price: Decimal
    fields: List[Dict[str, Any]] = []

class RequirementItem(BaseModel):
    id: str
    label: str
    type: Literal["document", "system_check"]
    params: Optional[Dict[str, Any]] = None
    
# ---------- ADMIN INPUT ----------

class DocumentTypeCreate(DocumentTypeBase):
    """
    Schema for creating a new document template via Admin Dashboard.
    """
    is_available: bool = True


class DocumentTypeUpdate(BaseModel):
    """
    Schema for updating existing templates. All fields are optional 
    to support partial updates (PATCH requests).
    """
    doctype_name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    fields: Optional[List[Dict[str, Any]]] = None
    is_available: Optional[bool] = None


# ---------- OUTPUT SCHEMAS ----------

class DocumentTypeKioskOut(DocumentTypeBase):
    """
    Public-facing document info shown on the Kiosk selection screen.
    Includes the ID for referencing in requests.
    """
    id: int

    model_config = ConfigDict(from_attributes=True)


class DocumentTypeAdminOut(DocumentTypeKioskOut):
    """
    Internal-facing document info for Admin tables.
    Includes availability status for management toggles.
    """
    is_available: bool
    has_template: bool

    model_config = ConfigDict(from_attributes=True)


class DocumentTypeProcessingOut(BaseModel):
    """
    Heavy schema used ONLY by the backend worker or admin during 
    document generation/autofilling.
    @property file: The raw BYTEA/blob template for the document.
    """
    id: int
    doctype_name: str
    price: Decimal
    fields: List[Dict[str, Any]]
    file: bytes

    model_config = ConfigDict(from_attributes=True)


# =========================================================
# DOCUMENT REQUESTS (Submitted by Residents, Processed by Admin)
# =========================================================

class DocumentRequestBase(BaseModel):
    """
    Common fields for all document requests.
    @property form_data: Key-value pairs containing responses to the dynamic 'fields'.
    """
    doctype_id: int
    form_data: Dict[str, Any]


class DocumentRequestCreate(DocumentRequestBase):
    """
    Validation schema for incoming Kiosk submissions.
    Includes the resident_id linked to the authenticated RFID session.
    """
    resident_id: int


class DocumentRequestKioskResponse(BaseModel):
    """
    Immediate feedback for the Kiosk user.
    Returns the unique transaction_no for manual tracking.
    """
    transaction_no: str


class DocumentRequestKioskOut(BaseModel):
    """
    Schema for Kiosk transaction history or 'Track My Request' views.
    Filters out internal processing details (like admin IDs).
    """
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
    """
    High-level request data for Admin Dashboard list views (Tables).
    Includes identifiers for the resident and the document type.
    """
    id: int
    transaction_no: str

    resident_id: int
    resident_first_name: Optional[str]
    resident_middle_name: Optional[str]
    resident_last_name: Optional[str]
    resident_rfid: Optional[str]
    resident_phone: Optional[str]
    
    doctype_id: int
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
    """
    Comprehensive request data for the Admin Detail/Processing view.
    Includes the resident's full name and path to generated files.
    """
    resident_name: str
    price: Decimal
    request_file_path: Optional[str] = None