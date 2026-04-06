"""
app/services/systemconfig_service.py
 
Service layer for system configuration management.
Handles reading, updating, and persisting the single SystemConfig row (id=1).
Also manages the barangay logo and last backup timestamp.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timezone
from app.models.systemconfig import SystemConfig
from app.schemas.systemconfig import SystemConfigUpdate


def get_config(db: Session) -> SystemConfig:
    config = db.query(SystemConfig).filter(SystemConfig.id == 1).first()
    if not config:
        config = SystemConfig(id=1)
        db.add(config)
        db.commit()
        db.refresh(config)
    return config


def update_config(db: Session, data: SystemConfigUpdate) -> SystemConfig:
    config = get_config(db)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    db.commit()
    db.refresh(config)
    return config


def get_logo_bytes(db: Session) -> tuple[bytes, str]:
    config = get_config(db)
    if not config.brgy_logo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No logo uploaded."
        )

    raw = config.brgy_logo
    if raw[:4] == b'\x89PNG':
        content_type = "image/png"
    elif raw[:2] in (b'\xff\xd8',):
        content_type = "image/jpeg"
    elif raw[:4] == b'RIFF' and raw[8:12] == b'WEBP':
        content_type = "image/webp"
    elif raw[:5] in (b'<?xml', b'<svg '):
        content_type = "image/svg+xml"
    else:
        content_type = "image/png"
    return raw, content_type


def set_last_backup(db: Session) -> SystemConfig:
    config = get_config(db)
    config.last_backup_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(config)
    return config