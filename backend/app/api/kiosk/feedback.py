"""
Kiosk Feedback Services API
---------------------------
Handles resident-facing and guest operations for submitting feedback
via the kiosk interface.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackKioskResponse
)
from app.services.feedback_service import create_feedback

router = APIRouter(prefix="/feedbacks")


# =========================================================
# FEEDBACK SUBMISSION
# =========================================================

@router.post(
    "",
    response_model=FeedbackKioskResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Processes a feedback submission from the kiosk.
    Supports both authenticated users (with resident_id) and guest mode (resident_id = None).
    """
    return create_feedback(db, payload)