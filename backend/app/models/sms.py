from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class SMSLog(Base):
    __tablename__ = "sms_logs"

    id         = Column(Integer, primary_key=True)
    message    = Column(Text, nullable=False)
    mode       = Column(String(64), nullable=False)   # 'groups' | 'puroks' | 'specific'
    recipients = Column(Integer, nullable=False, default=0)
    sent_at    = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)