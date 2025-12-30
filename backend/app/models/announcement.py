from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, Date, LargeBinary
from sqlalchemy.sql import func
from app.db.base import Base

class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(Date, nullable=False)
    event_time = Column(String(32))
    location = Column(String(255), nullable=False)
    image = Column(LargeBinary)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())