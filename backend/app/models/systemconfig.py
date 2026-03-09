"""
System Config Model
-------------------
Single-row table that stores all system-wide settings.
Only one row should ever exist (id=1). Use the service
helpers to get/update it — never instantiate directly.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.db.base import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, default=1)

    # ── General (Barangay Info) ────────────────────────────────────────────────
    brgy_name = Column(String(150), nullable=True, default="Barangay")
    brgy_subname = Column(String(200), nullable=True)
    brgy_logo_path = Column(String(500), nullable=True)

    # ── Security ──────────────────────────────────────────────────────────────
    rfid_expiry_days = Column(Integer, nullable=False, default=365)
    auto_logout_minutes = Column(Integer, nullable=False, default=30)
    max_failed_attempts = Column(Integer, nullable=False, default=5)
    lockout_minutes = Column(Integer, nullable=False, default=15)

    # ── Preferences ───────────────────────────────────────────────────────────
    default_view = Column(String(50), nullable=False, default="dashboard")
    maintenance_mode = Column(Boolean, nullable=False, default=False)

    # ── Backup ────────────────────────────────────────────────────────────────
    backup_schedule = Column(String(20), nullable=False, default="manual")
    backup_time = Column(String(5), nullable=True,  default="02:00")
    last_backup_at = Column(DateTime(timezone=True), nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────────────
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<SystemConfig brgy='{self.brgy_name}' maintenance={self.maintenance_mode}>"