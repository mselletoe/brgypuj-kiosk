# backend/app/models/audit.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"

    id = Column(Integer, primary_key=True)
    admin_id = Column(Integer, nullable=True) # Optional: link to your admin users table
    action = Column(String(100), nullable=False) # e.g., "Approved Request", "Added Resident"
    details = Column(String(255)) # e.g., "DOC-002 - Barangay Clearance"
    entity_type = Column(String(50)) # e.g., "doc", "equip", "resident", "blotter", "system"
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())