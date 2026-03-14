"""
Kiosk Feedback Services API
---------------------------
Handles resident-facing and guest operations for submitting feedback
via the kiosk interface.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.feedback import (
    FeedbackCreate,
    FeedbackKioskResponse
)
from app.services.feedback_service import create_feedback

router = APIRouter(prefix="/feedbacks")


# =========================================================
# FEEDBACK SUBMISSION
# =========================================================

@router.post("", response_model=FeedbackKioskResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    result = create_feedback(db, payload)
    await ws_manager.broadcast_to_admin(
        "new_feedback",
        {
            "type": "Feedback",
            "resident_name": f"Resident #{payload.resident_id}" if getattr(payload, 'resident_id', None) else "A guest",
            "rating": getattr(payload, 'rating', None),
        },
        db=db 
    )
    return result