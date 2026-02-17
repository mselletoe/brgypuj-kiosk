from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, ForeignKey, FetchedValue
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Time
from app.db.base import Base


class BlotterRecord(Base):
    __tablename__ = "blotter_records"

    id = Column(Integer, primary_key=True)
    blotter_no = Column(String(20), unique=True, nullable=False)
    complainant_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"), nullable=True)
    complainant_name = Column(String(255), nullable=False)
    complainant_age = Column(Integer, nullable=True)
    complainant_address = Column(String(255), nullable=True)
    respondent_name = Column(String(255), nullable=False)
    respondent_age = Column(Integer, nullable=True)
    respondent_address = Column(String(255), nullable=True)
    incident_date = Column(Date, nullable=False)
    incident_time = Column(Time, nullable=True)
    incident_place = Column(String(255), nullable=True)
    incident_type = Column(String(128), nullable=True)
    narrative = Column(Text, nullable=True)
    recorded_by = Column(String(255), nullable=True)
    contact_no = Column(String(16), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

    complainant = relationship("Resident", back_populates="blotter_records")