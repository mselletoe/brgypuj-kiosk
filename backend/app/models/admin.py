from sqlalchemy import Column, SmallInteger, Integer, String, Text, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Admin(Base):
    __tablename__ = "admin"

    id = Column(SmallInteger, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    password = Column(Text, nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    resident = relationship("Resident", back_populates="admin_account")
    document_requests_processed = relationship("DocumentRequest", back_populates="processed_by_admin")