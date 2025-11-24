"""
================================================================================
File: auth_utils.py
Description:
    Centralized authentication utilities for tracking login method and user
    identity across all API services. Provides JWT token generation/validation
    and dependency injection helpers for protected routes.

    Features:
      • JWT token creation with user metadata (login method, resident info)
      • Token validation and decoding
      • FastAPI dependencies for route protection
      • Support for RFID and Guest login modes
================================================================================
"""

from fastapi import Depends, HTTPException, Header
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os

# Load from .env
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# ==============================================================================
# Token Creation
# ==============================================================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT token with user information and login method.
    
    Args:
        data: Dictionary containing user info (resident_id, login_method, etc.)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ==============================================================================
# Token Validation
# ==============================================================================
def decode_access_token(token: str):
    """
    Decode and validate JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

# ==============================================================================
# FastAPI Dependency: Get Current User
# ==============================================================================
def get_current_user(authorization: Optional[str] = Header(None)):
    """
    FastAPI dependency to extract and validate current user from token.
    
    Usage:
        @router.get("/protected")
        def protected_route(user = Depends(get_current_user)):
            # user contains: resident_id, login_method, name, etc.
            pass
    
    Returns:
        Dictionary with user information:
        {
            "resident_id": int or None (None for guests),
            "login_method": "rfid" or "guest",
            "name": str,
            "is_guest": bool,
            "rfid_uid": str or None
        }
    """
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header missing"
        )
    
    try:
        # Extract token from "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication scheme"
            )
        
        payload = decode_access_token(token)
        return payload
        
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

# ==============================================================================
# FastAPI Dependency: Require RFID Login
# ==============================================================================
def require_rfid_user(user = Depends(get_current_user)):
    """
    FastAPI dependency that ensures user logged in via RFID.
    Use this for routes that should only be accessible to registered residents.
    
    Usage:
        @router.post("/request-document")
        def create_request(user = Depends(require_rfid_user)):
            resident_id = user["resident_id"]
            # Process request...
    """
    if user.get("login_method") != "rfid":
        raise HTTPException(
            status_code=403,
            detail="This action requires RFID login"
        )
    
    if not user.get("resident_id"):
        raise HTTPException(
            status_code=403,
            detail="No resident ID found"
        )
    
    return user

# ==============================================================================
# FastAPI Dependency: Allow Guest or RFID
# ==============================================================================
def get_optional_user(authorization: Optional[str] = Header(None)):
    """
    Optional authentication - returns user info if token present, None otherwise.
    Use this for routes that work differently for authenticated vs guest users.
    
    Usage:
        @router.get("/announcements")
        def get_announcements(user = Depends(get_optional_user)):
            if user:
                # Personalized content
            else:
                # Public content
    """
    if not authorization:
        return None
    
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None