"""
app/api/kiosk/contact.py

Router for kiosk contact information display.
Returns the barangay's emergency numbers, office hours, and support details.
Falls back to sensible defaults if no contact record has been configured.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.contact import ContactInformationOut
from app.services.contact_service import get_or_create_contact

router = APIRouter(prefix="/contact")


# =================================================================================
# CONTACT INFORMATION
# =================================================================================

@router.get("", response_model=ContactInformationOut)
def kiosk_get_contact(db: Session = Depends(get_db)):
    return get_or_create_contact(db)