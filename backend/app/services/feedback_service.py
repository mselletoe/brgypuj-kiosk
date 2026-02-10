"""
Feedback Service Layer
---------------------------
Handles the business logic for feedback management, including kiosk submissions
and administrative monitoring.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.misc import Feedback
from app.models.resident import Resident
from app.schemas.feedback import FeedbackCreate, FeedbackKioskResponse


# -------------------------------------------------
# Internal Helpers
# -------------------------------------------------

def _validate_resident(db: Session, resident_id: int) -> Resident:
    """
    Ensures the resident exists in the database.
    Only called when resident_id is provided.
    """
    resident = db.query(Resident).filter(Resident.id == resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    return resident


def _get_feedback(db: Session, feedback_id: int):
    """
    Internal helper to retrieve a feedback record by ID.
    """
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


# -------------------------------------------------
# Kiosk Service Functions
# -------------------------------------------------

def create_feedback(db: Session, payload: FeedbackCreate) -> FeedbackKioskResponse:
    """
    Processes a new feedback submission from the kiosk.
    Supports both authenticated (resident_id provided) and guest mode (resident_id = None).
    """
    # Validate resident if resident_id is provided
    if payload.resident_id is not None:
        _validate_resident(db, payload.resident_id)

    # Create feedback record
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


# -------------------------------------------------
# Administrative Functions
# -------------------------------------------------

def get_all_feedbacks(db: Session):
    """
    Admin: Retrieves all feedback submissions with resident information.
    """
    from sqlalchemy.orm import joinedload
    
    return (
        db.query(Feedback)
        .options(joinedload(Feedback.resident))
        .order_by(Feedback.created_at.desc())
        .all()
    )


def delete_feedback(db: Session, feedback_id: int):
    """
    Admin: Deletes a specific feedback record.
    """
    feedback = _get_feedback(db, feedback_id)
    if not feedback:
        return False
    
    db.delete(feedback)
    db.commit()
    return True


def bulk_delete_feedbacks(db: Session, ids: list[int]):
    """
    Admin: Bulk delete operation for multiple feedback records.
    Returns the count of successfully deleted records.
    """
    count = db.query(Feedback).filter(Feedback.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return count