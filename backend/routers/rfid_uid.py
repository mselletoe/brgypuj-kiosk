from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models import RfidUID, Resident
from datetime import datetime

router = APIRouter(prefix="/rfid", tags=["RFID"])

# Pydantic model for request validation
class RFIDRegisterRequest(BaseModel):
    resident_id: int
    rfid_uid: str

@router.post("/register")
def register_rfid(request: RFIDRegisterRequest, db: Session = Depends(get_db)):
    resident_id = request.resident_id
    rfid_uid = request.rfid_uid

    # Check if RFID UID is already used
    existing_uid = db.query(RfidUID).filter(RfidUID.rfid_uid == rfid_uid).first()
    if existing_uid:
        raise HTTPException(status_code=400, detail="This RFID card is already registered.")

    # Check if resident exists
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found.")

    # Check if resident already has an RFID linked
    existing_rfid = db.query(RfidUID).filter(RfidUID.resident_id == resident_id).first()
    if existing_rfid:
        raise HTTPException(status_code=400, detail="This resident already has an RFID linked.")

    # Create new record
    new_rfid = RfidUID(
        resident_id=resident_id,
        rfid_uid=rfid_uid,
        status="active",
        created_at=datetime.now(),
        is_active=True
    )
    db.add(new_rfid)
    db.commit()
    db.refresh(new_rfid)

    return {
        "message": f"RFID {rfid_uid} linked to {resident.first_name} {resident.last_name}",
        "rfid_uid": new_rfid.rfid_uid,
        "resident_id": resident.id
    }

@router.get("/check/{rfid_uid}")
def check_rfid(rfid_uid: str, db: Session = Depends(get_db)):
    existing_uid = db.query(RfidUID).filter(RfidUID.rfid_uid == rfid_uid).first()

    if existing_uid:
        resident = db.query(Resident).filter(Resident.id == existing_uid.resident_id).first()
        return {
            "exists": True,
            "resident_id": resident.id if resident else None,
            "resident_name": f"{resident.first_name} {resident.middle_name or ''} {resident.last_name}".strip()
        }

    return {"exists": False}