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

# bcrypt context for hashing and verifying resident PINs
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sentinel value indicating a resident has not yet set a custom PIN
RFID_PIN_DEFAULT = "0000"


# =================================================================================
# GUEST AUTHENTICATION
# =================================================================================

@router.post("/guest")
def guest_login():
    """Starts an unauthenticated guest session on the kiosk."""
    return {"mode": "guest"}


# =================================================================================
# RFID AUTHENTICATION
# =================================================================================

@router.post("/rfid", response_model=RFIDLoginResponse)
def rfid_auth(payload: RFIDLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates a resident by their RFID card UID.

    Validates the RFID tag, checks for an active lockout, then returns
    the resident's profile and their current formatted address.
    Raises 401 for invalid or inactive cards, and 423 if the account is locked.
    """
    resident = rfid_login(db, payload.rfid_uid)

    if not resident:
        raise HTTPException(status_code=401, detail="Invalid or inactive RFID")

    # Reject login if the resident is within an active lockout window
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

    # Fetch the resident's current address with its associated purok
    current_address = (
        db.query(Address)
        .filter(
            Address.resident_id == resident.id,
            Address.is_current == True,
        )
        .join(Purok)
        .first()
    )

    # Format address into a single readable string if available
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


# =================================================================================
# FIRST TIME SET PIN
# =================================================================================

@router.post("/set-pin", status_code=status.HTTP_200_OK)
def set_pin(payload: SetPinRequest, db: Session = Depends(get_db)):
    """
    Sets a PIN for a resident who has not yet configured one.
    Rejects the request if a custom PIN is already in place — use /verify-pin instead.
    Resets any prior failed attempt counters and lockout on success.
    """
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    # Only allow set-pin if the resident is still on the default PIN
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


# =================================================================================
# VERIFY PIN
# =================================================================================

@router.post("/verify-pin", response_model=VerifyPinResponse)
def verify_pin(payload: VerifyPinRequest, db: Session = Depends(get_db)):
    """
    Verifies a resident's PIN after an RFID scan.

    Tracks failed attempts and enforces a lockout once the configured
    maximum is reached. Returns remaining attempts on failure, or resets the counter on success.
    Raises 423 if the resident is currently locked out.
    """
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")

    # Cannot verify a PIN that hasn't been set yet
    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured. Please set a PIN first.",
        )

    # Reject immediately if still within a lockout window
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

    is_valid = pwd_context.verify(payload.pin, resident.rfid_pin)

    if is_valid:
        # Reset failure tracking on a successful verification
        resident.failed_pin_attempts = 0
        resident.locked_until = None
        db.commit()
        return {"valid": True}

    config = get_config(db)
    resident.failed_pin_attempts = (resident.failed_pin_attempts or 0) + 1

    if resident.failed_pin_attempts >= config.max_failed_attempts:
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