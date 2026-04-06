from datetime import date, datetime, time
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


class BlotterRecordBase(BaseModel):
    complainant_name: str
    complainant_age: Optional[int] = None
    complainant_address: Optional[str] = None
    respondent_name: Optional[str] = None
    respondent_age: Optional[int] = None
    respondent_address: Optional[str] = None
    incident_date: Optional[date] = None
    incident_time: Optional[time] = None
    incident_place: Optional[str] = None
    incident_type: Optional[str] = None
    narrative: Optional[str] = None
    recorded_by: Optional[str] = None
    contact_no: Optional[str] = None


class BlotterRecordCreate(BlotterRecordBase):
    complainant_id: Optional[int] = None
    respondent_id: Optional[int] = None


class BlotterRecordUpdate(BaseModel):
    complainant_id: Optional[int] = None
    complainant_name: Optional[str] = None
    complainant_age: Optional[int] = None
    complainant_address: Optional[str] = None
    respondent_id: Optional[int] = None
    respondent_name: Optional[str] = None
    respondent_age: Optional[int] = None
    respondent_address: Optional[str] = None
    incident_date: Optional[date] = None
    incident_time: Optional[time] = None
    incident_place: Optional[str] = None
    incident_type: Optional[str] = None
    narrative: Optional[str] = None
    recorded_by: Optional[str] = None
    contact_no: Optional[str] = None


class BlotterRecordOut(BlotterRecordBase):
    id: int
    blotter_no: str

    complainant_id: Optional[int] = None
    complainant_resident_name: Optional[str] = None

    respondent_id: Optional[int] = None
    respondent_resident_name: Optional[str] = None

    role: Optional[str] = None

    status: str = "active"
    resolved_at: Optional[datetime] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlotterRecordDetail(BlotterRecordOut):
    complainant_resident_first_name: Optional[str] = None
    complainant_resident_middle_name: Optional[str] = None
    complainant_resident_last_name: Optional[str] = None
    complainant_resident_phone: Optional[str] = None

    respondent_resident_first_name: Optional[str] = None
    respondent_resident_middle_name: Optional[str] = None
    respondent_resident_last_name: Optional[str] = None
    respondent_resident_phone: Optional[str] = None