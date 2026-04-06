"""
app/api/kiosk/contact.py

Router for kiosk contact information display.
Returns the barangay's emergency numbers, office hours, and support details.
Falls back to sensible defaults if no contact record has been configured.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.contact import ContactInformation
from app.schemas.contact import ContactInformationOut

router = APIRouter(prefix="/contact")


@router.get("", response_model=ContactInformationOut)
def get_contact(db: Session = Depends(get_db)):
    contact = db.query(ContactInformation).first()
    if not contact:
        return ContactInformation(
            id=1,
            emergency_number="911",
            emergency_desc="For life-threatening emergencies",
            phone="",
            email="",
            office_hours="Monday to Friday, 8:00 AM - 5:00 PM",
            address="",
            tech_support="If you're experiencing issues with the kiosk, please contact our office or visit during business hours for assistance.",
        )
    return contact