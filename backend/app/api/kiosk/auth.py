from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.kiosk.auth import RFIDLoginRequest, RFIDLoginResponse
from app.services.auth_service import rfid_login

router = APIRouter(prefix="/auth")

@router.post("/guest")
def guest_login():
    return {
        "mode": "guest"
    }

@router.post("/rfid", response_model=RFIDLoginResponse)
def rfid_auth(payload: RFIDLoginRequest, db: Session = Depends(get_db)):
    resident = rfid_login(db, payload.rfid_uid)

    if not resident:
        raise HTTPException(status_code=401, detail="Invalid or inactive RFID")

    return {
        "mode": "rfid",
        "resident_id": resident.id,
        "first_name": resident.first_name,
        "last_name": resident.last_name,
        "has_pin": resident.rfid_pin is not None
    }