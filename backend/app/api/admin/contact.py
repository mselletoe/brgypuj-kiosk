"""
app/api/admin/contact.py
 
Router for barangay contact information management.
Handles retrieval and update of the singleton contact record,
auto-creating it with sensible defaults if it does not yet exist.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.contact import ContactInformation
from app.schemas.contact import ContactInformationOut, ContactInformationUpdate

router = APIRouter(prefix="/contact")


# =================================================================================
# INTERNAL HELPERS
# =================================================================================

def get_or_create_contact(db: Session) -> ContactInformation:
    contact = db.query(ContactInformation).first()
    if not contact:
        contact = ContactInformation(
            id=1,
            emergency_number="911",
            emergency_desc="For life-threatening emergencies",
            phone="",
            email="",
            office_hours="Monday to Friday, 8:00 AM - 5:00 PM",
            address="",
            tech_support="",
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


# =================================================================================
# CONTACT INFORMATION
# =================================================================================

@router.get("", response_model=ContactInformationOut)
def get_contact(db: Session = Depends(get_db)):
    return get_or_create_contact(db)


@router.put("", response_model=ContactInformationOut)
def update_contact(payload: ContactInformationUpdate, db: Session = Depends(get_db)):
    contact = get_or_create_contact(db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact