"""
app/api/admin/contact.py

Router for barangay contact information management.
Handles retrieval and update of the singleton contact record.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.contact import ContactInformationOut, ContactInformationUpdate
from app.services.contact_service import get_or_create_contact, update_contact

router = APIRouter(prefix="/contact")


# =================================================================================
# CONTACT INFORMATION
# =================================================================================

@router.get("", response_model=ContactInformationOut)
def admin_get_contact(db: Session = Depends(get_db)):
    return get_or_create_contact(db)


@router.put("", response_model=ContactInformationOut)
def admin_update_contact(payload: ContactInformationUpdate, db: Session = Depends(get_db)):
    return update_contact(db, payload)