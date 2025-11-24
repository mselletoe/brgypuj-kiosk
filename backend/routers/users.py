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
from auth_utils import create_access_token

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
    rfid_uid = data.get("rfid_uid")

    if not pin:
        raise HTTPException(status_code=400, detail="PIN required")

    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="User not found")

    if resident.account_pin:
        raise HTTPException(status_code=400, detail="PIN already set")

    # Store the PIN (consider hashing in production)
    resident.account_pin = pin
    db.commit()

    # Generate JWT token for immediate login after PIN setup
    token_data = {
        "resident_id": resident.id,
        "login_method": "rfid",
        "name": f"{resident.first_name} {resident.last_name}",
        "is_guest": False,
        "rfid_uid": rfid_uid
    }
    access_token = create_access_token(token_data)
    
    return {
        "message": "PIN set successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

# ==============================================================================
# Endpoint: Verify user PIN
# ==============================================================================
@router.post("/users/{user_id}/pin/verify")
def verify_user_pin(user_id: int, data: dict, db: Session = Depends(get_db)):
    pin = data.get("pin")
    rfid_uid = data.get("rfid_uid")

    if not pin:
        raise HTTPException(status_code=400, detail="PIN required")

    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident or not resident.account_pin:
        raise HTTPException(status_code=404, detail="PIN not found")

    valid = (pin == resident.account_pin)

    if not valid:
        return {"valid": False}
    
    # Generate JWT token on successful verification
    token_data = {
        "resident_id": resident.id,
        "login_method": "rfid",
        "name": f"{resident.first_name} {resident.last_name}",
        "is_guest": False,
        "rfid_uid": rfid_uid,
        "email": resident.email
    }
    access_token = create_access_token(token_data)
    
    return {
        "valid": True,
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

# ==============================================================================
# Endpoint: Guest Login (NEW)
# ==============================================================================
@router.post("/users/guest/login")
def guest_login():
    """
    Generate a JWT token for guest users.
    Guest users have limited access and no resident_id.
    """
    token_data = {
        "resident_id": None,
        "login_method": "guest",
        "name": "Guest User",
        "is_guest": True,
        "rfid_uid": None
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

# ==============================================================================
# Endpoint: Admin Login (NEW)
# ==============================================================================
@router.post("/users/admin/login")
def admin_login(data: dict):
    """
    Generate a JWT token for admin login via PIN.
    """
    pin = data.get("pin")
    rfid_uid = data.get("rfid_uid")
    ADMIN_PIN = "7890"  # Should be in env variables
    
    if pin != ADMIN_PIN:
        raise HTTPException(status_code=401, detail="Invalid admin PIN")
    
    token_data = {
        "resident_id": None,
        "login_method": "admin",
        "name": "Admin",
        "is_guest": False,
        "is_admin": True,
        "rfid_uid": rfid_uid
    }
    access_token = create_access_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": token_data
    }

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
        "middle_name": resident.middle_name,
        "email": resident.email,
        "phone_number": resident.phone_number,
        "account_pin": bool(resident.account_pin),
    }