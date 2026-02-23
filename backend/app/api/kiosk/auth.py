"""
Auth Router for Kiosk Operations
-------------------------------
Handles authentication logic for the Barangay Kiosk including:
1. Anonymous Guest sessions.
2. RFID-based resident identification.
3. PIN setup for first-time / default residents.
4. PIN verification for returning residents.
"""

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
from app.models.resident import Resident

router = APIRouter(prefix="/auth")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sentinel value assigned during the NOT NULL migration.
# Residents with this value have not yet configured a real PIN.
RFID_PIN_DEFAULT = "0000"


@router.post("/guest")
def guest_login():
    """
    Initializes a guest session.

    Returns:
        dict: A simple dictionary defining the session mode as 'guest'.
    """
    return {"mode": "guest"}


@router.post("/rfid", response_model=RFIDLoginResponse)
def rfid_auth(payload: RFIDLoginRequest, db: Session = Depends(get_db)):
    """
    Identifies a resident via their RFID UID.

    Args:
        payload (RFIDLoginRequest): Contains the rfid_uid from the hardware scanner.
        db (Session): SQLAlchemy database session provided by dependency injection.

    Returns:
        RFIDLoginResponse: Validated resident profile data and PIN status.

    Raises:
        HTTPException: 401 Unauthorized if the RFID is not found or is marked inactive.
    """
    resident = rfid_login(db, payload.rfid_uid)

    if not resident:
        raise HTTPException(status_code=401, detail="Invalid or inactive RFID")

    return {
        "mode": "rfid",
        "resident_id": resident.id,
        "first_name": resident.first_name,
        "last_name": resident.last_name,
        "has_pin": resident.has_pin,
    }


@router.post("/set-pin", status_code=status.HTTP_200_OK)
def set_pin(payload: SetPinRequest, db: Session = Depends(get_db)):
    """
    Sets a new PIN for a resident who has the default '0000' sentinel PIN.

    Called by AuthPIN.vue during the first-time PIN setup workflow.

    Args:
        payload (SetPinRequest): resident_id, pin (plain text), rfid_uid.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: Success message.

    Raises:
        HTTPException 404: Resident not found.
        HTTPException 400: Resident already has a real PIN configured —
                           use /verify-pin instead.
    """
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    # Guard: prevent overwriting an already-configured PIN via this endpoint
    if resident.rfid_pin not in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="PIN already configured. Use /verify-pin to authenticate."
        )

    resident.rfid_pin = pwd_context.hash(payload.pin)
    db.commit()

    return {"message": "PIN set successfully"}


@router.post("/verify-pin", response_model=VerifyPinResponse)
def verify_pin(payload: VerifyPinRequest, db: Session = Depends(get_db)):
    """
    Verifies a resident's PIN against the stored bcrypt hash.

    Called by AuthPIN.vue during the standard login workflow.

    Args:
        payload (VerifyPinRequest): resident_id and pin (plain text).
        db (Session): SQLAlchemy database session.

    Returns:
        VerifyPinResponse: { valid: true } on success, { valid: false } on mismatch.

    Raises:
        HTTPException 404: Resident not found.
        HTTPException 400: Resident has not configured a PIN yet —
                           use /set-pin instead.
    """
    resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    # Guard: resident still has the default sentinel — they should set a PIN first
    if resident.rfid_pin in (None, RFID_PIN_DEFAULT):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No PIN configured. Please set a PIN first."
        )

    is_valid = pwd_context.verify(payload.pin, resident.rfid_pin)

    return {"valid": is_valid}