"""
================================================================================
File: admin_auth.py
...
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

from database import get_db
import models
import schemas 
import utils # <-- Import hashing utils

# ==========================
# JWT settings
# ==========================
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev_fallback_key_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================
# FastAPI router
# ==========================
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================
# Token creation
# ==========================
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ==========================
# Login route (UPDATED)
# ==========================
@router.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # Locate staff record by email
    user = db.query(models.BrgyStaff).filter(models.BrgyStaff.email.ilike(request.email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify HASHED password
    if not utils.verify_password(request.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Ensure account is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account inactive")

    # Payload for JWT token
    first_name = "Staff"
    last_name = "User"
    if user.resident:
        first_name = user.resident.first_name
        last_name = user.resident.last_name
    # No fallback to staff_name, as resident is now required

    token_data = {
        "sub": user.email, 
        "role": user.role, 
        "id": user.id,
        "first_name": first_name,
        "last_name": last_name
    }

    # Return encoded token
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token}

# ==========================
# Register route (UPDATED)
# ==========================
@router.post("/register", response_model=schemas.StaffDisplay, status_code=status.HTTP_201_CREATED)
def register_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    """
    Register a new barangay staff member.
    """
    
    # 1. Check if resident is already a staff member
    existing_staff_resident = db.query(models.BrgyStaff).filter(
        models.BrgyStaff.resident_id == staff.resident_id
    ).first()
    if existing_staff_resident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This resident is already registered as a staff member."
        )

    # 2. Check if email is already in use (case-insensitive)
    existing_staff_email = db.query(models.BrgyStaff).filter(
        models.BrgyStaff.email.ilike(staff.email)
    ).first()
    
    if existing_staff_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already in use."
        )

    # 3. Hash the password
    hashed_password = utils.hash_password(staff.password)

    # 4. Create the new staff member object
    new_staff = models.BrgyStaff(
        resident_id=staff.resident_id, # <-- Using resident_id
        email=staff.email,
        password=hashed_password, # <-- Using hashed password
        role=staff.role, # <-- Using role from frontend
        is_active=True 
    )

    # 5. Add to database
    try:
        db.add(new_staff)
        db.commit()
        db.refresh(new_staff)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred. Could not create account."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

    return new_staff