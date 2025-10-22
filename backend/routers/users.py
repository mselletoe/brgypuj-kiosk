# backend/routers/users.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models import Resident

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Check if user has PIN
@router.get("/users/{user_id}/pin")
def get_user_pin(user_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == user_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="User not found")
    has_pin = resident.account_pin is not None
    return {"has_pin": has_pin}

# Set PIN
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

    # Save PIN directly (no hashing)
    resident.account_pin = pin
    db.commit()
    return {"message": "PIN set successfully"}

# Verify PIN
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

# Get user info
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
        # any other fields you need
    }