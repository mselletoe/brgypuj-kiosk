from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from app.schemas.sms import (
    SMSRequest,
    RecipientCountResponse,
    SMSSendResponse,
    SMSHistoryItem,
)
from app.services.sms_service import (
    get_recipient_count,
    send_sms_announcement,
    get_sms_history,
)
from app.api.deps import get_db

router = APIRouter(prefix="/sms")


# ============================================================================
# Preview (dry-run)
# ============================================================================

@router.post("/preview", response_model=RecipientCountResponse)
def preview_recipients(payload: SMSRequest, db: Session = Depends(get_db)):
    """
    Resolve recipients for the given payload and return the count WITHOUT
    actually sending any messages.

    Use this to power the live "X recipients selected" badge in the UI.
    """
    return get_recipient_count(db, payload)


# ============================================================================
# Send
# ============================================================================

@router.post("/send", response_model=SMSSendResponse, status_code=201)
def send_announcement(payload: SMSRequest, db: Session = Depends(get_db)):
    """
    Send an SMS blast to the resolved recipient list and log the operation.

    recipient_mode options
    ──────────────────────
    - **groups**   → pass `groups` list with one or more of:
        `female`, `male`, `adult`, `youth`, `senior`, `with_rfid`
    - **puroks**   → pass `purok_ids` list with purok IDs from the database
    - **specific** → pass `phone_numbers` list with raw phone numbers

    Example (groups):
    ```json
    {
      "message": "Barangay assembly bukas ng 5PM sa covered court.",
      "recipient_mode": "groups",
      "groups": ["senior", "with_rfid"]
    }
    ```

    Example (puroks):
    ```json
    {
      "message": "Water interruption scheduled tomorrow, 8AM–5PM.",
      "recipient_mode": "puroks",
      "purok_ids": [1, 3]
    }
    ```
    """
    return send_sms_announcement(db, payload)


# ============================================================================
# History
# ============================================================================

@router.get("/history", response_model=List[SMSHistoryItem])
def list_sms_history(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Return recent SMS blasts in descending order for the history panel.
    """
    return get_sms_history(db, limit=limit)