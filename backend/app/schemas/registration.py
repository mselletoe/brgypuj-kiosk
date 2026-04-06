from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class RFIDStatusResponse(BaseModel):
    is_new: bool


class AdminPasscodeRequest(BaseModel):
    passcode: str


class AdminPasscodeResponse(BaseModel):
    valid: bool


class ApprovedIDApplication(BaseModel):
    transaction_no: str
    document_request_id: int
    resident_id: int
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    birthdate: Optional[str] = None  
    address: Optional[str] = None
    requested_at: datetime


class LinkRFIDRequest(BaseModel):
    rfid_uid: str 
    resident_id: int  
    document_request_id: int 


class LinkRFIDResponse(BaseModel):
    success: bool
    rfid_uid: str
    resident_id: int
    resident_first_name: str
    resident_last_name: str
    transaction_no: str
    linked_at: datetime