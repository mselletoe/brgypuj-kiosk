from sqlalchemy import (
    Column, Integer, SmallInteger, String, Date,
    ForeignKey, TIMESTAMP, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class BarangayID(Base):
    __tablename__ = "barangay_ids"
    id = Column(Integer, primary_key=True)
    brgy_id_number = Column(String(10), unique=True, nullable=True)
    resident_id = Column(
        Integer,
        ForeignKey("residents.id", ondelete="CASCADE"),
        nullable=False,
    )
    rfid_id = Column(
        Integer,
        ForeignKey("resident_rfid.id", ondelete="SET NULL"),
        nullable=True,
    )
    request_id = Column(
        Integer,
        ForeignKey("document_requests.id", ondelete="SET NULL"),
        nullable=True,
    )
    issued_date   = Column(Date, nullable=True)          # date card was released
    expiration_date = Column(Date, nullable=True)        # mirrors ResidentRFID.expiration_date
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    resident = relationship("Resident", back_populates="barangay_ids")
    rfid     = relationship("ResidentRFID", back_populates="barangay_id")
    request  = relationship("DocumentRequest", back_populates="barangay_id")