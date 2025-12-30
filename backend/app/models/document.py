from sqlalchemy import Column, SmallInteger, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(SmallInteger, primary_key=True)
    doctype_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(String, default="0.00")  # can be DECIMAL
    file = Column(String)  # BYTEA if needed
    fields = Column(String, default="[]")
    is_available = Column(Boolean, default=True)

    document_requests = relationship("DocumentRequest", back_populates="doctype")


class DocumentRequest(Base):
    __tablename__ = "document_requests"

    id = Column(Integer, primary_key=True)
    transaction_no = Column(String(20), unique=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    doctype_id = Column(Integer, ForeignKey("document_types.id"))
    processed_by = Column(SmallInteger, ForeignKey("admin.id", ondelete="SET NULL"))
    status = Column(String(32), default="Pending")
    payment_status = Column(String(20), default="unpaid")
    form_data = Column(String)  # JSONB in DB
    request_file_path = Column(Text)
    requested_at = Column(TIMESTAMP, server_default=func.now())

    resident = relationship("Resident", back_populates="document_requests")
    doctype = relationship("DocumentType", back_populates="document_requests")
    processed_by_admin = relationship("Admin", back_populates="document_requests_processed")