"""
app/api/kiosk/auth.py

Router for kiosk-facing authentication. Supports guest sessions,
RFID card scanning, and PIN management (set and verify).
Includes lockout enforcement for repeated failed PIN attempts.
"""

from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.api.deps import get_db
from app.schemas.kiosk.auth import (
    RFIDLoginRequest,
    RFIDLoginResponse,
    SetPinRequest,
    VerifyPinRequest,
    VerifyPinResponse,
)
from app.services.auth_service import rfid_login
from app.services.systemconfig_service import get_config
from app.models.resident import Resident, Address, Purok

router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
RFID_PIN_DEFAULT = "0000"


def _as_utc(dt):
    """Return a timezone-aware UTC datetime, even if the DB returns a naive value."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _active_lockout_payload(resident: Resident, db: Session, now: datetime):
    """
    Return a 423 detail payload if lockout is still active.
    If lockout already expired, clear both locked_until and failed attempts
    so the next PIN try starts with a fresh attempt allowance.
    """
    locked_until = _as_utc(resident.locked_until)
    if not locked_until:
        return None

    if locked_until > now:
        remaining = max(1, int((locked_until - now).total_seconds()))
        return {
            "reason": "too_many_attempts",
            "locked_until": locked_until.isoformat(),
            "lockout_seconds_remaining": remaining,
        }

    # Lockout has expired. Clear stale lockout state before verifying again.
    resident.locked_until = None
    resident.failed_pin_attempts = 0
    db.commit()
    return None


@router.post("/guest")
def guest_login():
    """Starts an unauthenticated guest session on the kiosk."""
    return {"mode": "guest"}


@router.post("/rfid", response_model=RFIDLoginResponse)
def rfid_auth(payload: RFIDLoginRequest, db: Session = Depends(get_db)):
    resident = rfid_login(db, payload.rfid_uid)

    if not resident:
        raise HTTPException(status_code=401, detail="Invalid or inactive RFID")

    now = datetime.now(timezone.utc)
    lockout_detail = _active_lockout_payload(resident, db, now)
    if lockout_detail:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=lockout_detail)

    current_address = (
        db.query(Address)
        .filter(
            Address.resident_id == resident.id,
            Address.is_current == True,
        )
        .join(Purok)
        .first()
    )

    formatted_address = None
    if current_address:
        formatted_address = (
            f"{current_address.house_no_street}, "
            f"{current_address.purok.purok_name}, "
            f"{current_address.barangay}, "
            f"{current_address.municipality}, "
            f"{current_address.province}"
        )

    return {
        "mode": "rfid",
        "resident_id": resident.id,
        "first_name": resident.first_name,
        "middle_name": resident.middle_name,
        "last_name": resident.last_name,
        "has_pin": resident.has_pin,
        "address": formatted_address,
    }


@router.post("/set-pin", status_code=status.HTTP_200_OK)
def set_pin(payload: SetPinRequest, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    if resident.rfid_pin not in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN already configured. Use /verify-pin to authenticate.",
        )

    resident.rfid_pin = pwd_context.hash(payload.pin)
    resident.failed_pin_attempts = 0
    resident.locked_until = None
    db.commit()

    return {"message": "PIN set successfully"}


@router.post("/verify-pin", response_model=VerifyPinResponse)
def verify_pin(payload: VerifyPinRequest, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured. Please set a PIN first.",
        )

    now = datetime.now(timezone.utc)
    lockout_detail = _active_lockout_payload(resident, db, now)
    if lockout_detail:
        raise HTTPException(status_code=status.HTTP_423_LOCKED, detail=lockout_detail)

    is_valid = pwd_context.verify(payload.pin, resident.rfid_pin)

    if is_valid:
        resident.failed_pin_attempts = 0
        resident.locked_until = None
        db.commit()
        return {"valid": True}

    config = get_config(db)
    max_failed_attempts = max(1, int(config.max_failed_attempts or 1))
    lockout_minutes = max(1, int(config.lockout_minutes or 1))

    resident.failed_pin_attempts = (resident.failed_pin_attempts or 0) + 1

    if resident.failed_pin_attempts >= max_failed_attempts:
        resident.locked_until = now + timedelta(minutes=lockout_minutes)
        db.commit()

        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "reason": "too_many_attempts",
                "locked_until": resident.locked_until.isoformat(),
                "lockout_seconds_remaining": lockout_minutes * 60,
            },
        )

    db.commit()

    attempts_left = max_failed_attempts - resident.failed_pin_attempts
    return {"valid": False, "attempts_left": attempts_left}
