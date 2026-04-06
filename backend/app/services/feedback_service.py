"""
app/services/feedback_service.py
 
Service layer for resident feedback submissions.
Handles creation, retrieval, and deletion of feedback entries.
Supports both RFID-authenticated and guest submissions.
"""

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.misc import Feedback
from app.models.resident import Resident
from app.schemas.feedback import FeedbackCreate, FeedbackKioskResponse


# =================================================================================
# INTERNAL HELPERS
# =================================================================================

def _validate_resident(db: Session, resident_id: int) -> Resident:
    resident = db.query(Resident).filter(Resident.id == resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    return resident


def _get_feedback(db: Session, feedback_id: int):
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


# =================================================================================
# KIOSK
# =================================================================================

def create_feedback(db: Session, payload: FeedbackCreate) -> FeedbackKioskResponse:
    if payload.resident_id is not None:
        _validate_resident(db, payload.resident_id)

    feedback = Feedback(
        resident_id=payload.resident_id,
        category=payload.category,
        rating=payload.rating,
        additional_comments=payload.additional_comments
    )

    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackKioskResponse()


# =================================================================================
# ADMIN
# =================================================================================

def get_all_feedbacks(db: Session):
    return (
        db.query(Feedback)
        .options(joinedload(Feedback.resident))
        .order_by(Feedback.created_at.desc())
        .all()
    )


def delete_feedback(db: Session, feedback_id: int):
    feedback = _get_feedback(db, feedback_id)
    if not feedback:
        return False
    
    db.delete(feedback)
    db.commit()
    return True


def bulk_delete_feedbacks(db: Session, ids: list[int]):
    count = db.query(Feedback).filter(Feedback.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count