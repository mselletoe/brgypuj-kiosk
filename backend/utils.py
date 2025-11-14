"""
================================================================================
File: utils.py
Description:
    This module provides utility functions for the backend, such as password
    hashing and verification using passlib.
================================================================================
"""

from passlib.context import CryptContext

# Initialize the password hashing context
# We use bcrypt as the hashing algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hashes a plain-text password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain-text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)