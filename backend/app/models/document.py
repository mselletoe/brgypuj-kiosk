from sqlalchemy import Column, SmallInteger, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, Numeric, LargeBinary, FetchedValue, CheckConstraint, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class DocumentType(Base):
    __tablename__ = "document_types"

    id = Column(SmallInteger, primary_key=True)
    doctype_name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), server_default="0.00")
    file = Column(LargeBinary)
    fields = Column(JSON, server_default="'[]'")
    is_available = Column(Boolean, nullable=False, server_default="true")
    requirements = Column(JSON, server_default="'[]'")

    document_requests = relationship("DocumentRequest", back_populates="doctype")

    @property
    def has_template(self) -> bool:
        """Check if document has an uploaded template file"""
        return self.file is not None and len(self.file) > 0 if self.file else False

class DocumentRequest(Base):
    __tablename__ = "document_requests"

    id = Column(Integer, primary_key=True)
    transaction_no = Column(String(20), unique=True, nullable=False, server_default=FetchedValue())
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    doctype_id = Column(SmallInteger, ForeignKey("document_types.id"), nullable=True)
    price = Column(Numeric(10, 2), nullable=False, server_default="0.00")
    processed_by = Column(SmallInteger, ForeignKey("admin.id", ondelete="SET NULL"))
    status = Column(
        String(32), 
        CheckConstraint("status IN ('Pending', 'Approved', 'Ready', 'Released', 'Rejected')"),
        nullable=False, 
        server_default="Pending"
    )
    payment_status = Column(
        String(20), 
        CheckConstraint("payment_status IN ('unpaid', 'paid')"),
        nullable=False, 
        server_default="unpaid"
    )
    form_data = Column(JSONB)
    request_file_path = Column(Text)
    requested_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    notes = Column(Text, nullable=True)

    resident = relationship("Resident", back_populates="document_requests")
    doctype = relationship("DocumentType", back_populates="document_requests")
    processed_by_admin = relationship("Admin", back_populates="document_requests_processed")