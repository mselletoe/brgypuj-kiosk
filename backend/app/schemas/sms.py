from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class RecipientMode(str, Enum):
    groups   = "groups"
    puroks   = "puroks"
    specific = "specific"


class ResidentGroup(str, Enum):
    female    = "female"
    male      = "male"
    adult     = "adult"     
    youth     = "youth"   
    senior    = "senior" 
    with_rfid = "with_rfid" 


class SMSRequest(BaseModel):
    message: str = Field(
        ..., min_length=1, max_length=500,
        description="The SMS body (max 500 characters / ~3 SMS pages)"
    )
    recipient_mode: RecipientMode

    groups: Optional[List[ResidentGroup]] = Field(
        None, description="Required when recipient_mode == 'groups'"
    )

    purok_ids: Optional[List[int]] = Field(
        None, description="Required when recipient_mode == 'puroks'"
    )

    phone_numbers: Optional[List[str]] = Field(
        None, description="Required when recipient_mode == 'specific'"
    )

    model_config = {"use_enum_values": True}


class RecipientCountResponse(BaseModel):
    recipient_mode: str
    group_labels: Optional[List[str]] = None 
    purok_names:  Optional[List[str]] = None 
    count: int


class SMSSendResponse(BaseModel):
    success:         bool
    recipients:      int 
    message_preview: str 
    failed:          int  = 0
    queued_at:       str  = ""


class SMSHistoryItem(BaseModel):
    id:         int
    message:    str
    mode:       str
    recipients: int
    sent_at:    str

    model_config = {"from_attributes": True}