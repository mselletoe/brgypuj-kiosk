from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True)
    transaction_name = Column(String(50), nullable=False)   # Document Request, Equipment Request, etc.
    transaction_no = Column(String(20), nullable=False)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=True)  # Guest if NULL
    rfid_uid = Column(String(50), nullable=True)
    status = Column(String(20), CheckConstraint("status IN ('Completed', 'Rejected')"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    resident = relationship("Resident")