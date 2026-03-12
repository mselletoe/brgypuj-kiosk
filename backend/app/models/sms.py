from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from sqlalchemy.sql import func
from app.db.base import Base


class SMSLog(Base):
    """
    Persists every SMS blast so the frontend can show 'Recent Sends'.
    The actual delivery to the SMS gateway is handled in the service layer;
    this table is purely an audit / history log.
    """
    __tablename__ = "sms_logs"

    id         = Column(Integer, primary_key=True)
    message    = Column(Text, nullable=False)
    mode       = Column(String(64), nullable=False)   # 'groups' | 'puroks' | 'specific'
    recipients = Column(Integer, nullable=False, default=0)
    sent_at    = Column(TIMESTAMP, server_default=func.current_timestamp(), nullable=False)