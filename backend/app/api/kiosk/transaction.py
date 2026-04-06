"""
app/api/kiosk/transaction.py

Router for kiosk transaction history.
Allows residents to view their past document and equipment request history.
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
    return get_transaction_history(db, resident_id)