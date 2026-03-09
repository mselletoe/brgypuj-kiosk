"""
System Config Service
---------------------
Handles the singleton pattern for system_config.
The table always has exactly one row (id=1).
If it doesn't exist yet, get_config() creates it with defaults.
"""

from sqlalchemy.orm import Session
from app.models.systemconfig import SystemConfig
from app.schemas.systemconfig import SystemConfigUpdate


def get_config(db: Session) -> SystemConfig:
    """
    Returns the single system config row.
    Creates it with defaults if it doesn't exist yet (first-run safety).
    """
    config = db.query(SystemConfig).filter(SystemConfig.id == 1).first()
    if not config:
        config = SystemConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def update_config(db: Session, data: SystemConfigUpdate) -> SystemConfig:
    """
    Applies a partial update (PATCH). Only fields explicitly set in `data`
    are written — unset fields are left unchanged.
    """
    config = get_config(db)

    # Only update fields that were explicitly provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    db.commit()
    db.refresh(config)
    return config


def set_logo_path(db: Session, path: str) -> SystemConfig:
    """Convenience helper called after a logo file upload succeeds."""
    config = get_config(db)
    config.brgy_logo_path = path
    db.commit()
    db.refresh(config)
    return config


def set_last_backup(db: Session) -> SystemConfig:
    """Called after a successful backup to stamp last_backup_at."""
    from datetime import datetime, timezone
    config = get_config(db)
    config.last_backup_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(config)
    return config