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


@router.post("", response_model=FeedbackKioskResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    payload: FeedbackCreate,
    db: Session = Depends(get_db)
):
    result = create_feedback(db, payload)

    resident_name = None
    if payload.resident_id:
        from app.models.resident import Resident
        resident = db.query(Resident).filter(Resident.id == payload.resident_id).first()
        if resident:
            resident_name = " ".join(filter(None, [resident.first_name, resident.last_name]))

    await ws_manager.broadcast_to_admin(
        "new_feedback",
        {
            "type": "Feedback",
            "resident_name": resident_name,
            "rating": getattr(payload, 'rating', None),
        },
        db=db
    )
    return result