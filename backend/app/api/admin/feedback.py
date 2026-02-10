"""
Feedback Administration API
---------------------------
Provides management endpoints for viewing and managing feedback submissions
within the administrative dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.feedback import FeedbackAdminOut
from app.services.feedback_service import (
    get_all_feedbacks,
    delete_feedback,
    bulk_delete_feedbacks
)

router = APIRouter(prefix="/feedbacks")


# =========================================================
# FEEDBACK MANAGEMENT
# =========================================================

def _format_feedback_for_admin(feedback):
    """Helper to format feedback with resident data"""
    # Get the active RFID UID if resident exists
    rfid_display = "Guest"
    
    if feedback.resident:
        # Get the active RFID from the relationship
        active_rfid = next(
            (rfid.rfid_uid for rfid in feedback.resident.rfids if rfid.is_active),
            None
        )
        rfid_display = active_rfid if active_rfid else "No RFID"

    return {
        "id": feedback.id,
        "category": feedback.category,
        "rating": feedback.rating,
        "additional_comments": feedback.additional_comments,
        "resident_id": feedback.resident_id,
        "resident_first_name": feedback.resident.first_name if feedback.resident else None,
        "resident_middle_name": feedback.resident.middle_name if feedback.resident else None,
        "resident_last_name": feedback.resident.last_name if feedback.resident else None,
        "resident_rfid": rfid_display,
        "created_at": feedback.created_at,
    }


@router.get(
    "",
    response_model=list[FeedbackAdminOut],
)
def list_feedbacks(db: Session = Depends(get_db)):
    """
    Lists all feedback submissions for administrative review.
    Includes both resident and guest feedback.
    """
    feedbacks = get_all_feedbacks(db)
    return [_format_feedback_for_admin(fb) for fb in feedbacks]


@router.delete("/{feedback_id}")
def delete_feedback_record(feedback_id: int, db: Session = Depends(get_db)):
    """
    Deletes a specific feedback record.
    """
    success = delete_feedback(db, feedback_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"detail": "Feedback deleted"}


@router.post("/bulk-delete")
def bulk_delete_feedback_records(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    """
    Bulk delete operation for multiple feedback records.
    Returns count of successfully deleted records.
    """
    deleted_count = bulk_delete_feedbacks(db, ids)
    return {"detail": f"{deleted_count} feedbacks deleted"}