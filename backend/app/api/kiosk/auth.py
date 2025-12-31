"""
Auth Router for Kiosk Operations
-------------------------------
Handles authentication logic for the Barangay Kiosk including:
1. Anonymous Guest sessions.
2. RFID-based resident identification.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.kiosk.auth import RFIDLoginRequest, RFIDLoginResponse
from app.services.auth_service import rfid_login

router = APIRouter(prefix="/auth")

@router.post("/guest")
def guest_login():
    """
    Initializes a guest session.
    
    Returns:
        dict: A simple dictionary defining the session mode as 'guest'.
    """
    return {
        "mode": "guest"
    }

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

    # 1. Invoke service layer to fetch resident and validate RFID status
    resident = rfid_login(db, payload.rfid_uid)

    if not resident:
        raise HTTPException(status_code=401, detail="Invalid or inactive RFID")

    # 2. Construct response based on the RFIDLoginResponse schema.
    # The 'has_pin' field determines the frontend routing logic (PIN screen vs Home).
    return {
        "mode": "rfid",
        "resident_id": resident.id,
        "first_name": resident.first_name,
        "last_name": resident.last_name,
        "has_pin": resident.rfid_pin is not None
    }