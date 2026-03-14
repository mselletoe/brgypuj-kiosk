from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.faqs import FAQKioskOut
from app.services.faqs_service import (
    get_kiosk_faqs
)
from app.api.deps import get_db

router = APIRouter(prefix="/faqs")

@router.get("/kiosk", response_model=list[FAQKioskOut])
def kiosk_list_faqs(db: Session = Depends(get_db)):
    return get_kiosk_faqs(db)