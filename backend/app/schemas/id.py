from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class ResidentSearchResult(BaseModel):
    resident_id: int
    first_name:  str
    middle_name: Optional[str] = None
    last_name:   str
    suffix:      Optional[str] = None
    has_rfid:    bool             
    has_pending: bool = False     


class BirthdateVerifyRequest(BaseModel):
    resident_id: int
    birthdate:   date


class BirthdateVerifyResponse(BaseModel):
    verified: bool


class IDApplicationRequest(BaseModel):
    resident_id:           Optional[int] = None    
    applicant_resident_id: int                  
    rfid_uid:              Optional[str] = None  
    photo:                 Optional[str] = None  
    use_manual_data:       bool = False  
    field_values:          dict = {} 


class IDApplicationResponse(BaseModel):
    transaction_no:       str
    resident_first_name:  str
    resident_last_name:   str
    requested_at:         datetime


class ChangePinRequest(BaseModel):
    resident_id:  int
    current_pin:  str
    new_pin:      str


class ChangePinResponse(BaseModel):
    success: bool
    message: str


class ReportLostCardVerifyRequest(BaseModel):
    resident_id: int


class ReportLostCardVerifyResponse(BaseModel):
    resident_id: int
    first_name:  str
    last_name:   str
    rfid_uid:    Optional[str]
    has_rfid:    bool


class ReportLostCardRequest(BaseModel):
    resident_id: int
    pin:         str
    rfid_uid:    Optional[str] = None   


class ReportLostCardResponse(BaseModel):
    report_id:            int
    resident_first_name:  str
    resident_last_name:   str
    rfid_uid:             Optional[str]
    reported_at:          datetime


class IDApplicationAdminOut(BaseModel):
    id:                   int
    transaction_no:       str
    resident_id:          Optional[int]
    resident_first_name:  Optional[str]
    resident_last_name:   Optional[str]
    resident_rfid:        str             
    brgy_id_number:       Optional[str]
    requested_at:         datetime
    status:               str
    payment_status:       str


class RFIDReportAdminOut(BaseModel):
    id:                   int
    resident_id:          Optional[int]
    resident_first_name:  Optional[str]
    resident_last_name:   Optional[str]
    rfid_uid:             Optional[str] = None
    status:               str
    reported_at:          datetime           


class LinkRFIDResponse(BaseModel):
    success:             bool
    rfid_uid:            str
    resident_id:         int
    resident_first_name: str
    resident_last_name:  str
    transaction_no:      str
    brgy_id_number:      str
    expiration_date:     str    
    linked_at:           datetime


class VerifyPinRequest(BaseModel):
    resident_id: int
    pin:         str


class VerifyPinResponse(BaseModel):
    verified: bool