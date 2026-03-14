"""
Transaction History Schemas
---------------------------
Single shared Pydantic schema used by both Kiosk and Admin interfaces.
Both interfaces expose the same fields, so no split is needed.

If Admin ever requires extra fields (e.g. resident_id, resident name),
extend via: class TransactionHistoryAdminOut(TransactionHistoryOut): ...
"""

from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


class TransactionHistoryOut(BaseModel):
    id: int
    transaction_type: Literal["document", "equipment", "rfid"] 
    transaction_name: str 
    transaction_no: str
    rfid_uid: Optional[str] = None
    status: str             # "Completed" | "Rejected"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)