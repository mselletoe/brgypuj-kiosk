"""
Transaction History API - Admin Endpoints
------------------------------------------
Administrative endpoint for viewing the full unified transaction history
across all residents and transaction types.
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
def get_resident_transaction_history(resident_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Retrieve the unified transaction history for a specific resident.

    Returns all completed or rejected transactions across:
    - Document Requests (Released → Completed, Rejected → Rejected)
    - Equipment Requests (Returned → Completed, Rejected → Rejected)
    - RFID Activities (once the RFID module is enabled)

    Results are ordered by most recent first.
    """
    return get_transaction_history(db, resident_id)