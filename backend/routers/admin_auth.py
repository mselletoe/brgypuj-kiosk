"""
================================================================================
File: admin_auth.py
Description:
    This module handles authentication for Barangay staff (admin users).
    It provides secure endpoints for:
    
    1. Staff Login (/login): 
       - Verifies email and HASHED password.
       - Checks if the account is active.
       - Returns a JWT (JSON Web Token) containing the user's role and name.
       
    2. Staff Registration (/register):
       - Validates that the Staff ID links to a real Resident.
       - Ensures the email is unique (case-insensitive).
       - Hashes the password before saving to the database (using bcrypt).
       - Automatically pulls the name from the Resident record.    
================================================================================
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
# ==========================
# Register route (FIXED)
# ==========================
@router.post("/register", response_model=schemas.StaffDisplay, status_code=status.HTTP_201_CREATED)
def register_staff(staff: schemas.StaffCreate, db: Session = Depends(get_db)):
    """
    Register a new barangay staff member safely.
    """

    # 1. Ensure the resident exists
    resident = db.query(models.Resident).get(staff.resident_id)
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Selected resident does not exist."
        )

    # 2. Check if this resident is already a staff member
    existing_staff_resident = db.query(models.BrgyStaff).filter(
        models.BrgyStaff.resident_id == staff.resident_id
    ).first()
    if existing_staff_resident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This resident is already registered as a staff member."
        )

    # 3. Check if email is already in use (case-insensitive)
    existing_staff_email = db.query(models.BrgyStaff).filter(
        models.BrgyStaff.email.ilike(staff.email)
    ).first()
    if existing_staff_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email address is already in use."
        )

    # 4. Hash the password
    hashed_password = utils.hash_password(staff.password)

    # 5. Create the staff_name from resident's name (optional)
    staff_name = f"{resident.first_name} {resident.last_name}"

    # 6. Create new staff object
    new_staff = models.BrgyStaff(
        resident_id=int(staff.resident_id),  # ensure integer
        staff_name=staff_name,
        email=staff.email,
        password=hashed_password,
        role=staff.role,
        is_active=True
    )

    # 7. Add to database
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)

    return new_staff