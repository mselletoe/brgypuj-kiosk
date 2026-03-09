from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.contact import ContactInformation
from app.schemas.contact import ContactInformationOut, ContactInformationUpdate

router = APIRouter(prefix="/contact")


def get_or_create_contact(db: Session) -> ContactInformation:
    """Always returns the single contact record, creating it if it doesn't exist."""
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