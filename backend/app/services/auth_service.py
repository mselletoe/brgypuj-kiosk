from sqlalchemy.orm import Session
from app.models.resident import Resident, ResidentRFID

def rfid_login(db: Session, rfid_uid: str):
    result = (
        db.query(Resident, ResidentRFID)
        .join(ResidentRFID, Resident.id == ResidentRFID.resident_id)
        .filter(
            ResidentRFID.rfid_uid == rfid_uid,
            ResidentRFID.is_active == True
        )
        .first()
    )

    if not result:
        return None

    resident, rfid = result

    resident.has_pin = resident.rfid_pin is not None
    
    return resident