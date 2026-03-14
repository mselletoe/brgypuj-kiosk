"""
Transaction History API - Kiosk Endpoints
------------------------------------------
Resident-facing endpoint to view their unified transaction history
across Document Requests, Equipment Requests, and RFID Activities.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.transaction import TransactionHistoryOut
from app.services.transaction_service import get_transaction_history

router = APIRouter(prefix="/transactions")


@router.get(
    "/history/{resident_id}",
    response_model=list[TransactionHistoryOut]
)
def get_my_transaction_history(resident_id: int, db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve the unified transaction history for a resident.

    Returns all completed or rejected transactions across:
    - Document Requests
    - Equipment Requests
    - RFID Activities (once enabled)

    Results are ordered by most recent first.
    """
    return get_transaction_history(db, resident_id)