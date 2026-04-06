"""
app/services/faqs_service.py
 
Service layer for FAQ management.
Handles creation, update, deletion, and retrieval of FAQ entries
for both the admin panel and kiosk display.
"""

from sqlalchemy.orm import Session
from app.models.faqs import FAQ
from app.schemas.faqs import FAQCreate, FAQUpdate

def create_faq(db: Session, payload: FAQCreate):
    faq = FAQ(question=payload.question, answer=payload.answer)
    db.add(faq)
    db.commit()
    db.refresh(faq)
    return faq


def update_faq(db: Session, faq_id: int, payload: FAQUpdate):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        return None
    faq.question = payload.question
    faq.answer = payload.answer
    db.commit()
    db.refresh(faq)
    return faq


def delete_faq(db: Session, faq_id: int):
    faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not faq:
        return False
    db.delete(faq)
    db.commit()
    return True


def bulk_delete_faqs(db: Session, ids: list[int]):
    count = db.query(FAQ).filter(FAQ.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count


def get_all_faqs(db: Session):
    return db.query(FAQ).order_by(FAQ.created_at.desc()).all()


def get_kiosk_faqs(db: Session):
    return db.query(FAQ).all()