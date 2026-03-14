"""
System Log Service
------------------
Core logging logic. Call `log_action()` anywhere in your routes
to record an event. It never raises exceptions — logging failures
are silently caught so they never break your main request flow.

Actor Resolution:
- Admin actions  → actor_name = admin.resident.first_name + last_name
- Kiosk actions  → actor_name = resident.first_name + last_name (if authenticated)
                   actor_name = "Kiosk" (if anonymous/no resident context)
- System events  → actor_name = "System"
"""

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


# ── Actor name helpers ─────────────────────────────────────────────────────────

def get_admin_actor_name(admin: "Admin") -> str:
    """
    Build display name from admin's linked resident record.
    Admin has no name fields — name lives on admin.resident.
    """
    try:
        r = admin.resident
        parts = [r.first_name, r.last_name]
        return " ".join(p for p in parts if p)
    except Exception:
        return f"Admin #{admin.id}"


def get_resident_actor_name(resident: "Resident") -> str:
    """Build display name from a Resident model instance."""
    try:
        parts = [resident.first_name, resident.last_name]
        return " ".join(p for p in parts if p)
    except Exception:
        return f"Resident #{resident.id}"


# ── Core log_action() ──────────────────────────────────────────────────────────

def log_action(
    db: Session,
    *,
    action: str,
    source: LogSource,
    category: LogCategory,
    level: LogLevel = LogLevel.INFO,

    # Pass the full Admin or Resident object for automatic name resolution,
    # OR pass actor_id / actor_name manually if you prefer.
    admin: Optional["Admin"] = None,
    resident: Optional["Resident"] = None,

    actor_id: Optional[int] = None,
    actor_name: Optional[str] = None,
    actor_role: Optional[str] = None,

    # What was affected
    target_type: Optional[str] = None,
    target_id: Optional[int] = None,
    details: Optional[dict | str] = None,

    # Pass the FastAPI Request object for automatic IP/endpoint/method capture
    request: Optional[Request] = None,
    ip_address: Optional[str] = None,
    endpoint: Optional[str] = None,
    http_method: Optional[str] = None,
    status_code: Optional[int] = None,
) -> Optional[SystemLog]:
    """
    Write a single log entry to the database.

    Preferred usage — pass the model object, let the service resolve the name:

        # Admin action
        log_action(
            db=db,
            action="Approved Barangay Clearance request #42",
            source=LogSource.ADMIN,
            category=LogCategory.TRANSACTION,
            admin=current_admin,        # resolves name via admin.resident
            target_type="DocumentRequest",
            target_id=42,
            request=request,
        )

        # Kiosk action with authenticated resident (via RFID)
        log_action(
            db=db,
            action="Resident submitted Barangay Clearance request",
            source=LogSource.KIOSK,
            category=LogCategory.TRANSACTION,
            resident=current_resident,  # resolves name from resident fields
            target_type="DocumentRequest",
            target_id=new_request.id,
            request=request,
        )

        # Kiosk action with no resident context (anonymous)
        log_action(
            db=db,
            action="Kiosk session started",
            source=LogSource.KIOSK,
            category=LogCategory.SYSTEM,
            request=request,
        )
    """
    try:
        # ── Resolve actor from model objects ──────────────────────────────────
        if admin is not None:
            actor_id = actor_id or admin.id
            actor_name = actor_name or get_admin_actor_name(admin)
            actor_role = actor_role or admin.system_role  # "admin" | "superadmin"

        elif resident is not None:
            actor_id = actor_id or resident.id
            actor_name = actor_name or get_resident_actor_name(resident)
            actor_role = actor_role or "resident"

        else:
            # Anonymous kiosk or system event
            if source == LogSource.KIOSK and actor_name is None:
                actor_name = "Kiosk"
                actor_role = actor_role or "kiosk"
            elif source == LogSource.SYSTEM and actor_name is None:
                actor_name = "System"
                actor_role = actor_role or "system"

        # ── Auto-extract request metadata ─────────────────────────────────────
        if request is not None:
            ip_address = ip_address or _get_client_ip(request)
            endpoint = endpoint or str(request.url.path)
            http_method = http_method or request.method

        # ── Serialize details ─────────────────────────────────────────────────
        details_str: Optional[str] = None
        if isinstance(details, dict):
            details_str = json.dumps(details, ensure_ascii=False)
        elif isinstance(details, str):
            details_str = details

        # ── Write to DB ───────────────────────────────────────────────────────
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
    """Extract real client IP, respecting X-Forwarded-For proxy headers."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


# ── Convenience wrappers ───────────────────────────────────────────────────────

def log_info(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.INFO, **kwargs)

def log_warning(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.WARNING, **kwargs)

def log_error(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.ERROR, **kwargs)

def log_critical(db, action, source, category, **kwargs):
    return log_action(db, action=action, source=source, category=category, level=LogLevel.CRITICAL, **kwargs)