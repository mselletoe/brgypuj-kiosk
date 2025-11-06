"""
================================================================================
File: admin_auth.py
Description:
    This module handles authentication for Barangay staff (admin users).
    It provides a login endpoint that verifies user credentials, ensures the
    account is active, and returns a signed JWT access token for authorized
    access to the system.

    The module includes:
      • Secure password hashing and verification using Passlib
      • JWT token generation with expiration
      • Request and response models for structured API handling

    This ensures a secure authentication process and controlled access
    across the system's administrative routes.
================================================================================
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models import BrgyStaff
import os

# ==========================
# JWT settings
# ==========================
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev_fallback_key_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# ==========================
# Password hashing
# ==========================
pwd_context = CryptContext(
    schemes=["bcrypt", "sha256_crypt", "pbkdf2_sha256"], 
    deprecated="auto"
)

# ==========================
# FastAPI router
# ==========================
router = APIRouter(prefix="/auth", tags=["Authentication"])

# ==========================
# Request / Response models
# ==========================
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==========================
# Token creation
# ==========================
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ==========================
# Login route
# ==========================
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Locate staff record by email
    user = db.query(BrgyStaff).filter(BrgyStaff.email == request.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Retrieve and verify hashed password
    hashed_pw = user.password.strip()

    try:
        if not pwd_context.verify(request.password, hashed_pw):
            raise HTTPException(status_code=401, detail="Invalid email or password")
    except ValueError:
        raise HTTPException(status_code=500, detail="Error verifying password. Check hash format.")

    # Ensure account is active
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account inactive")

    # Payload for JWT token
    token_data = {
        "sub": user.email, 
        "role": user.role, 
        "id": user.id,
        "first_name": user.resident.first_name if user.resident else "Unknown",
        "last_name": user.resident.last_name if user.resident else "User"
    }

    # Return encoded token
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token}