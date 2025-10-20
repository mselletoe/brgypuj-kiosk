from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import RfidUID, Resident
from datetime import datetime

router = APIRouter(prefix="/rfid", tags=["RFID"])

@router.post("/register")
def register_rfid(resident_id: int, rfid_uid: str, db: Session = Depends(get_db)):
    # Check if RFID UID is already used
    existing_uid = db.query(RfidUID).filter(RfidUID.rfid_uid == rfid_uid).first()
    if existing_uid:
        raise HTTPException(status_code=400, detail="This RFID card is already registered.")

    # Check if resident exists
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found.")

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

    return {"message": "RFID registered successfully", "rfid_uid": new_rfid.rfid_uid}

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