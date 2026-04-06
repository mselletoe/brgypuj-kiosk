import json
import logging
from typing import Optional, TYPE_CHECKING

from fastapi import Request
from sqlalchemy.orm import Session

from app.models.systemlogs import SystemLog, LogSource, LogLevel, LogCategory

if TYPE_CHECKING:
    from app.models.admin import Admin
    from app.models.resident import Resident

_logger = logging.getLogger("system_logs")



def get_admin_actor_name(admin: "Admin") -> str:
    try:
        r = admin.resident
        parts = [r.first_name, r.last_name]
        return " ".join(p for p in parts if p)
    except Exception:
        return f"Admin #{admin.id}"


def get_resident_actor_name(resident: "Resident") -> str:
    try:
        parts = [resident.first_name, resident.last_name]
        return " ".join(p for p in parts if p)
    except Exception:
        return f"Resident #{resident.id}"


def log_action(
    db: Session,
    *,
    action: str,
    source: LogSource,
    category: LogCategory,
    level: LogLevel = LogLevel.INFO,

    admin: Optional["Admin"] = None,
    resident: Optional["Resident"] = None,

    actor_id: Optional[int] = None,
    actor_name: Optional[str] = None,
    actor_role: Optional[str] = None,

    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[dict | str] = None,

    request: Optional[Request] = None,
    ip_address: Optional[str] = None,
    endpoint: Optional[str] = None,
    http_method: Optional[str] = None,
    status_code: Optional[int] = None,
) -> Optional[SystemLog]:
    try:
        if admin is not None:
            actor_id = actor_id or admin.id
            actor_name = actor_name or get_admin_actor_name(admin)
            actor_role = actor_role or admin.system_role

        elif resident is not None:
            actor_id = actor_id or resident.id
            actor_name = actor_name or get_resident_actor_name(resident)
            actor_role = actor_role or "resident"

        else:
            if source == LogSource.KIOSK and actor_name is None:
                actor_name = "Kiosk"
                actor_role = actor_role or "kiosk"
            elif source == LogSource.SYSTEM and actor_name is None:
                actor_name = "System"
                actor_role = actor_role or "system"

        if request is not None:
            ip_address = ip_address or _get_client_ip(request)
            endpoint = endpoint or str(request.url.path)
            http_method = http_method or request.method

        details_str: Optional[str] = None
        if isinstance(details, dict):
            details_str = json.dumps(details, ensure_ascii=False)
        elif isinstance(details, str):
            details_str = details

        log_entry = SystemLog(
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            action=action,
            category=category,
            level=level,
            source=source,
            target_type=target_type,
            target_id=target_id,
            details=details_str,
            ip_address=ip_address,
            endpoint=endpoint,
            http_method=http_method,
            status_code=status_code,
        )

        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    except Exception as exc:
        _logger.error(f"[SystemLog] Failed to write log: {exc}", exc_info=True)
        try:
            db.rollback()
        except Exception:
            pass
        return None


def _get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def log_info(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.INFO, **kwargs)

def log_warning(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.WARNING, **kwargs)

def log_error(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.ERROR, **kwargs)

def log_critical(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.CRITICAL, **kwargs)