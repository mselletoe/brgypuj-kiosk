from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base

class ContactInformation(Base):
    __tablename__ = "contact_information"

    id = Column(Integer, primary_key=True, default=1)
    emergency_number = Column(String(20), nullable=False, server_default="911")
    emergency_desc = Column(String(255), server_default="For life-threatening emergencies")
    phone = Column(String(50), server_default="")
    email = Column(String(255), server_default="")
    office_hours = Column(String(255), server_default="Monday to Friday, 8:00 AM - 5:00 PM")
    address = Column(Text, server_default="")
    tech_support = Column(Text, server_default="")
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())