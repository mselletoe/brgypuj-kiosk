from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from sqlalchemy.sql import func

from app.db.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"
    id = Column(Integer, primary_key=True, default=1)
    brgy_name = Column(String(150), nullable=True, default="Barangay")
    brgy_subname = Column(String(200), nullable=True)
    brgy_logo = Column(LargeBinary, nullable=True)
    rfid_expiry_days    = Column(Integer, nullable=False, default=365)
    rfid_reminder_days  = Column(Integer, nullable=False, default=30) 
    auto_logout_duration = Column(Integer, nullable=False, default=1800)
    max_failed_attempts = Column(Integer, nullable=False, default=5)
    lockout_minutes     = Column(Integer, nullable=False, default=15)
    default_view = Column(String(50), nullable=False, default="dashboard")
    maintenance_mode = Column(Boolean, nullable=False, default=False)
    maintenance_message = Column(String(500), nullable=True)
    backup_schedule = Column(String(20), nullable=False, default="manual")
    backup_time = Column(String(5), nullable=True, default="02:00")
    last_backup_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @property
    def has_logo(self) -> bool:
        return self.brgy_logo is not None

    def __repr__(self):
        return f"<SystemConfig brgy='{self.brgy_name}' maintenance={self.maintenance_mode}>"