from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class RecipientMode(str, Enum):
    groups   = "groups"
    puroks   = "puroks"
    specific = "specific"


class ResidentGroup(str, Enum):
    female    = "female"
    male      = "male"
    adult     = "adult"       # 18 years old and above
    youth     = "youth"       # 15–30 years old
    senior    = "senior"      # 60 years old and above
    with_rfid = "with_rfid"   # residents with an active RFID card


# ============================================================================
# Request Schemas
# ============================================================================

class SMSRequest(BaseModel):
    """
    Payload for sending an SMS announcement.

    Choose ONE of the three recipient targeting modes:
      - groups   → list of ResidentGroup enum values
      - puroks   → list of purok IDs (integers)
      - specific → list of raw phone-number strings
    """
    message: str = Field(
        ..., min_length=1, max_length=500,
        description="The SMS body (max 500 characters / ~3 SMS pages)"
    )
    recipient_mode: RecipientMode

    # --- groups mode ---
    groups: Optional[List[ResidentGroup]] = Field(
        None, description="Required when recipient_mode == 'groups'"
    )

    # --- puroks mode ---
    purok_ids: Optional[List[int]] = Field(
        None, description="Required when recipient_mode == 'puroks'"
    )

    # --- specific mode ---
    phone_numbers: Optional[List[str]] = Field(
        None, description="Required when recipient_mode == 'specific'"
    )

    model_config = {"use_enum_values": True}


# ============================================================================
# Response Schemas
# ============================================================================

class RecipientCountResponse(BaseModel):
    """
    Estimated recipient count before sending — returned by the preview endpoint.
    """
    recipient_mode: str
    group_labels: Optional[List[str]] = None   # human-readable group names
    purok_names:  Optional[List[str]] = None   # purok names for selected ids
    count: int


class SMSSendResponse(BaseModel):
    """Response returned after queuing an SMS blast."""
    success:         bool
    recipients:      int    # number of phone numbers targeted
    message_preview: str    # first 80 chars of the message
    failed:          int  = 0
    queued_at:       str  = ""


class SMSHistoryItem(BaseModel):
    """A single entry in the SMS send-history log."""
    id:         int
    message:    str
    mode:       str
    recipients: int
    sent_at:    str

    model_config = {"from_attributes": True}