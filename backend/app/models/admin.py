from sqlalchemy import Column, SmallInteger, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Admin(Base):
    __tablename__ = "admin"

    id = Column(SmallInteger, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    position = Column(String(100), nullable=True)           # e.g. "Barangay Secretary", "Treasurer" — cosmetic label
    system_role = Column(String(50), nullable=False, server_default="admin")   # "admin" | "superadmin" — controls permissions
    photo = Column(LargeBinary, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    resident = relationship("Resident", back_populates="admin_accounts")
    document_requests_processed = relationship("DocumentRequest", back_populates="processed_by_admin")