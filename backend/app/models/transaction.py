from sqlalchemy import Column, Integer, String, TIMESTAMP, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class TransactionHistory(Base):
    __tablename__ = "transaction_history"

    id = Column(Integer, primary_key=True)
    transaction_type = Column(                                          # ← ADD THIS
        String(20),
        CheckConstraint("transaction_type IN ('document', 'equipment', 'rfid')"),
        nullable=False,
        default="document"
    )
    transaction_name = Column(String(100), nullable=False)         
    transaction_no = Column(String(20), nullable=False)
    resident_id = Column(Integer, ForeignKey("residents.id"), nullable=True)
    rfid_uid = Column(String(50), nullable=True)
    status = Column(String(20), CheckConstraint("status IN ('Completed', 'Rejected')"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    resident = relationship("Resident")