from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
import enum

from app.db.base import Base


class LogSource(str, enum.Enum):
    ADMIN = "admin"
    KIOSK = "kiosk"
    SYSTEM = "system"


class LogLevel(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(str, enum.Enum):
    AUTH = "auth"                       # Login, logout, failed attempts
    TRANSACTION = "transaction"         # Document requests, approvals, rejections
    RESIDENT = "resident"               # Resident CRUD operations
    ADMIN_ACTION = "admin_action"       # Admin-specific actions (settings, reports)
    EQUIPMENT = "equipment"             # Equipment borrow/return
    ANNOUNCEMENT = "announcement"       # Announcements created/updated/deleted
    BLOTTER = "blotter"                 # Blotter report actions
    SYSTEM = "system"                   # App startup, DB issues, connectivity
    SECURITY = "security"               # Unauthorized access, token issues


class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Who triggered it
    actor_id = Column(Integer, nullable=True)           # Admin ID (null for kiosk/system events)
    actor_name = Column(String(100), nullable=True)     # "Admin Juan" or "Kiosk" or "System"
    actor_role = Column(String(50), nullable=True)      # "admin", "kiosk", "system"

    # What happened
    action = Column(String(150), nullable=False)        # e.g. "Approved document request #42"
    category = Column(SAEnum(LogCategory), nullable=False, default=LogCategory.SYSTEM)
    level = Column(SAEnum(LogLevel), nullable=False, default=LogLevel.INFO)
    source = Column(SAEnum(LogSource), nullable=False, default=LogSource.SYSTEM)

    # Context / details
    target_type = Column(String(100), nullable=True)    # e.g. "DocumentRequest", "Resident"
    target_id = Column(Integer, nullable=True)          # ID of the affected record
    details = Column(Text, nullable=True)               # JSON string or plain text extra info

    # Request metadata
    ip_address = Column(String(45), nullable=True)      # IPv4 or IPv6
    endpoint = Column(String(200), nullable=True)       # e.g. "/admin/documents/42/approve"
    http_method = Column(String(10), nullable=True)     # GET, POST, PUT, DELETE, PATCH

    # Outcome
    status_code = Column(Integer, nullable=True)        # HTTP status if applicable

    # Timestamp (auto-set on insert)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<SystemLog [{self.level.upper()}] {self.source} | {self.action} @ {self.created_at}>"