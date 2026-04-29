"""
app/services/contact_service.py

Service layer for contact information management.
Handles retrieval and update of the singleton contact record,
auto-creating it with sensible defaults if it does not yet exist.
"""

from sqlalchemy.orm import Session
from app.models.contact import ContactInformation
from app.schemas.contact import ContactInformationUpdate

_DEFAULTS = dict(
    id=1,
    emergency_number="911",
    emergency_desc="For life-threatening emergencies",
    phone="",
    email="",
    office_hours="Monday to Friday, 8:00 AM - 5:00 PM",
    address="",
    tech_support=(
        "If you're experiencing issues with the kiosk, please contact our "
        "office or visit during business hours for assistance."
    ),
)


def get_or_create_contact(db: Session) -> ContactInformation:
    contact = db.query(ContactInformation).first()
    if not contact:
        contact = ContactInformation(**_DEFAULTS)
        db.add(contact)
        db.commit()
        db.refresh(contact)
    return contact


def update_contact(db: Session, payload: ContactInformationUpdate) -> ContactInformation:
    contact = get_or_create_contact(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact