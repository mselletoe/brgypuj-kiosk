"""
Blotter Records Schemas
---------------------------
Pydantic models defining the data structures for Blotter Records.
These schemas handle data validation and serialization for the
Admin Dashboard blotter management feature.
"""

from datetime import date, datetime, time
from typing import Optional
from pydantic import BaseModel, ConfigDict


# =========================================================
# BLOTTER RECORDS (Admin Dashboard only)
# =========================================================

class BlotterRecordBase(BaseModel):
    """
    Common fields shared across blotter record operations.
    """
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


# ---------- ADMIN INPUT ----------

class BlotterRecordCreate(BlotterRecordBase):
    """
    Schema for creating a new blotter record via Admin Dashboard.
    Optionally links to a registered resident as complainant.
    """
    complainant_id: Optional[int] = None


class BlotterRecordUpdate(BaseModel):
    """
    Schema for updating existing blotter records. All fields are optional
    to support partial updates.
    """
    complainant_id: Optional[int] = None
    complainant_name: Optional[str] = None
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


# ---------- OUTPUT SCHEMAS ----------

class BlotterRecordOut(BlotterRecordBase):
    """
    Standard blotter record data for Admin Dashboard list views.
    Includes the auto-generated blotter number and linked resident info.
    """
    id: int
    blotter_no: str
    complainant_id: Optional[int] = None

    # Resolved resident name if linked
    complainant_resident_name: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BlotterRecordDetail(BlotterRecordOut):
    """
    Comprehensive blotter record data for the Admin Detail view.
    Extends the list schema with the full linked resident details.
    """
    complainant_resident_first_name: Optional[str] = None
    complainant_resident_middle_name: Optional[str] = None
    complainant_resident_last_name: Optional[str] = None
    complainant_resident_phone: Optional[str] = None