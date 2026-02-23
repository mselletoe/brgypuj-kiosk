from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.schemas.faqs import FAQCreate, FAQUpdate, FAQAdminOut
from app.services.faqs_service import (
    create_faq,
    update_faq,
    delete_faq,
    bulk_delete_faqs,
    get_all_faqs,
    get_kiosk_faqs
)
from app.api.deps import get_db

router = APIRouter(prefix="/faqs")

@router.post("", response_model=FAQAdminOut, status_code=status.HTTP_201_CREATED)
def admin_create_faq(payload: FAQCreate, db: Session = Depends(get_db)):
    return create_faq(db, payload)

@router.put("/{faq_id}", response_model=FAQAdminOut)
def admin_update_faq(faq_id: int, payload: FAQUpdate, db: Session = Depends(get_db)):
    faq = update_faq(db, faq_id, payload)
    if not faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return faq

@router.delete("/{faq_id}", status_code=status.HTTP_204_NO_CONTENT)
def admin_delete_faq(faq_id: int, db: Session = Depends(get_db)):
    if not delete_faq(db, faq_id):
        raise HTTPException(status_code=404, detail="FAQ not found")
    return

@router.post("/bulk-delete")
def admin_bulk_delete(ids: list[int], db: Session = Depends(get_db)):
    count = bulk_delete_faqs(db, ids)
    return {"deleted_count": count}

@router.get("/admin", response_model=list[FAQAdminOut])
def admin_list_faqs(db: Session = Depends(get_db)):
    return get_all_faqs(db)