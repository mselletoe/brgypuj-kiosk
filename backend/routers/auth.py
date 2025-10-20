from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import get_db
from models import BrgyStaff

router = APIRouter(prefix="/auth", tags=["Auth"])

# bcrypt context for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    staff = db.query(BrgyStaff).filter(BrgyStaff.email == data.email).first()
    if not staff:
        raise HTTPException(status_code=404, detail="User not found")

    # Truncate password to 72 bytes for bcrypt
    password_to_check = data.password[:72]

    try:
        if not pwd_context.verify(password_to_check, staff.password):
            raise HTTPException(status_code=401, detail="Invalid password")
    except Exception as e:
        print(f"[ERROR] Password verification failed: {e}")
        raise HTTPException(status_code=500, detail="Password verification failed")

    if not staff.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    return {
        "message": "Login successful",
        "staff_id": staff.id,
        "role": staff.role,
        "email": staff.email,
        "created_at": staff.created_at
    }
