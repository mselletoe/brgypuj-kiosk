from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, ConfigDict


class TransactionHistoryOut(BaseModel):
    id: int
    transaction_type: Literal["document", "equipment", "rfid"] 
    transaction_name: str 
    transaction_no: str
    rfid_uid: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)