from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey, Boolean, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="SET NULL"))
    category = Column(
        String(50), 
        CheckConstraint("category IN ('Service Quality', 'Interface Design', 'System Speed', 'Accessibility', 'General Experience')"),
        nullable=False
    )
    rating = Column(
        Integer, 
        CheckConstraint("rating >= 1 AND rating <= 5"),
        nullable=False
    )
    additional_comments = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

    resident = relationship("Resident", back_populates="feedbacks")


class RFIDReport(Base):
    __tablename__ = "rfid_reports"

    id = Column(Integer, primary_key=True)
    resident_id = Column(Integer, ForeignKey("residents.id", ondelete="CASCADE"))
    status = Column(String(32), default="Pending")
    created_at = Column(TIMESTAMP, server_default=func.now())

    resident = relationship("Resident", back_populates="rfid_reports")