from sqlalchemy.orm import Session
from app.models.resident import Resident
from typing import List

def get_all_residents(db: Session) -> List[Resident]:
    """
    Fetch all residents from the database.
    """
    return db.query(Resident).order_by(Resident.last_name, Resident.first_name).all()

def get_resident_by_id(db: Session, resident_id: int) -> Resident:
    """
    Fetch a single resident by ID.
    """
    return db.query(Resident).filter(Resident.id == resident_id).first()
