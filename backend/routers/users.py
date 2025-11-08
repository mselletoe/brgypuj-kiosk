"""
================================================================================
File: users.py
Description:
    This module defines API routes for managing user PIN authentication and 
    retrieving resident (user) information. It provides endpoints for creating, 
    verifying, and checking the existence of a user's PIN, as well as fetching 
    basic user details.

    The PIN system allows residents to set and verify a short numeric identifier
    for secure access to self-service or kiosk operations. 

    Note: PINs are currently stored in plaintext for simplicity — this should be 
    replaced with proper hashing for production use.
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models import Resident

# FastAPI router
router = APIRouter()

# Password context (reserved for future use — PINs not yet hashed)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==============================================================================
# Endpoint: Check if user has a PIN
# ==============================================================================
@router.get("/users/{user_id}/pin")
def get_user_pin(user_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="User not found")
    has_pin = resident.account_pin is not None
    return {"has_pin": has_pin}

# ==============================================================================
# Endpoint: Set user PIN
# ==============================================================================
@router.post("/users/{user_id}/pin")
def set_user_pin(user_id: int, data: dict, db: Session = Depends(get_db)):
    pin = data.get("pin")
    if not pin:
        raise HTTPException(status_code=400, detail="PIN required")

    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="User not found")

    if resident.account_pin:
        raise HTTPException(status_code=400, detail="PIN already set")

    # Directly store the PIN (not hashed)
    resident.account_pin = pin
    db.commit()
    return {"message": "PIN set successfully"}

# ==============================================================================
# Endpoint: Verify user PIN
# ==============================================================================
@router.post("/users/{user_id}/pin/verify")
def verify_user_pin(user_id: int, data: dict, db: Session = Depends(get_db)):
    pin = data.get("pin")
    if not pin:
        raise HTTPException(status_code=400, detail="PIN required")

    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident or not resident.account_pin:
        raise HTTPException(status_code=404, detail="PIN not found")

    valid = (pin == resident.account_pin)
    return {"valid": valid}

# ==============================================================================
# Endpoint: Get user info
# ==============================================================================
@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": resident.id,
        "first_name": resident.first_name,
        "last_name": resident.last_name,
        "account_pin": bool(resident.account_pin),
        # =======================================================================
        # Additional fields can be added here if needed
        # =======================================================================
    }