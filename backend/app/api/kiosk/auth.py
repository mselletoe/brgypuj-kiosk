"""
Auth Router for Kiosk Operations
-------------------------------
Handles authentication logic for the Barangay Kiosk including:
1. Anonymous Guest sessions.
2. RFID-based resident identification.
3. PIN setup for first-time / default residents.
4. PIN verification for returning residents — with failed-attempt lockout.

ADDED:
- verify_pin now enforces lockout using resident.failed_pin_attempts
  and resident.locked_until, driven by SystemConfig settings.
- 423 Locked is returned when the resident is currently locked out,
  with `locked_until` (ISO string) and `lockout_seconds_remaining` in the body.
"""

from datetime import datetime, timezone

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

# Sentinel value assigned during the NOT NULL migration.
RFID_PIN_DEFAULT = "0000"


# ── /guest ────────────────────────────────────────────────────────────────────

@router.post("/guest")
def guest_login():
    """Initializes a guest session."""
    return {"mode": "guest"}


# ── /rfid ─────────────────────────────────────────────────────────────────────

@router.post("/rfid", response_model=RFIDLoginResponse)
def rfid_auth(payload: RFIDLoginRequest, db: Session = Depends(get_db)):
    """
    Identifies a resident via their RFID UID.

    Raises:
        HTTPException 401: RFID not found or inactive.
        HTTPException 423: Resident is currently locked out due to too many
                           failed PIN attempts. Body includes locked_until and
                           lockout_seconds_remaining so the frontend can show
                           a countdown without making extra requests.
    """
    resident = rfid_login(db, payload.rfid_uid)

    if not resident:
        raise HTTPException(status_code=401, detail="Invalid or inactive RFID")

    # ── Lockout check ─────────────────────────────────────────────────────────
    # Surface lockout here (at scan time) so the user gets immediate feedback
    # rather than reaching the PIN screen only to be rejected.
    if resident.locked_until and resident.locked_until > datetime.now(timezone.utc):
        remaining = int((resident.locked_until - datetime.now(timezone.utc)).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "reason": "too_many_attempts",
                "locked_until": resident.locked_until.isoformat(),
                "lockout_seconds_remaining": remaining,
            },
        )

    # ── Build formatted address ───────────────────────────────────────────────
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


# ── /set-pin ──────────────────────────────────────────────────────────────────

@router.post("/set-pin", status_code=status.HTTP_200_OK)
def set_pin(payload: SetPinRequest, db: Session = Depends(get_db)):
    """
    Sets a new PIN for a resident who has the default '0000' sentinel PIN.
    Also clears any stale lockout state from a previous card.
    """
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    if resident.rfid_pin not in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN already configured. Use /verify-pin to authenticate.",
        )

    resident.rfid_pin = pwd_context.hash(payload.pin)
    # Clear any stale lockout data
    resident.failed_pin_attempts = 0
    resident.locked_until = None
    db.commit()

    return {"message": "PIN set successfully"}


# ── /verify-pin ───────────────────────────────────────────────────────────────

@router.post("/verify-pin", response_model=VerifyPinResponse)
def verify_pin(payload: VerifyPinRequest, db: Session = Depends(get_db)):
    """
    Verifies a resident's PIN against the stored bcrypt hash.

    Lockout behaviour (driven by SystemConfig):
    - On wrong PIN: increment failed_pin_attempts.
    - When failed_pin_attempts >= max_failed_attempts: set locked_until to
      now + lockout_minutes, return 423 Locked.
    - On correct PIN: reset failed_pin_attempts and locked_until, return valid=true.

    Returns:
        VerifyPinResponse: { valid: true/false }
        OR 423 if currently locked out.

    Raises:
        HTTPException 404: Resident not found.
        HTTPException 400: No PIN configured yet.
        HTTPException 423: Locked out — body contains locked_until and
                           lockout_seconds_remaining.
    """
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured. Please set a PIN first.",
        )

    # ── Already locked? ───────────────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    if resident.locked_until and resident.locked_until > now:
        remaining = int((resident.locked_until - now).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "reason": "too_many_attempts",
                "locked_until": resident.locked_until.isoformat(),
                "lockout_seconds_remaining": remaining,
            },
        )

    # ── Verify PIN ────────────────────────────────────────────────────────────
    is_valid = pwd_context.verify(payload.pin, resident.rfid_pin)

    if is_valid:
        # Reset lockout counters on success
        resident.failed_pin_attempts = 0
        resident.locked_until = None
        db.commit()
        return {"valid": True}

    # ── Wrong PIN — increment counter ─────────────────────────────────────────
    config = get_config(db)
    resident.failed_pin_attempts = (resident.failed_pin_attempts or 0) + 1

    if resident.failed_pin_attempts >= config.max_failed_attempts:
        from datetime import timedelta
        resident.locked_until = now + timedelta(minutes=config.lockout_minutes)
        db.commit()

        remaining = int(config.lockout_minutes * 60)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "reason": "too_many_attempts",
                "locked_until": resident.locked_until.isoformat(),
                "lockout_seconds_remaining": remaining,
            },
        )

    db.commit()

    attempts_left = config.max_failed_attempts - resident.failed_pin_attempts
    return {"valid": False, "attempts_left": attempts_left}