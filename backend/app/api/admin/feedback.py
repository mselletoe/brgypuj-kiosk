"""
app/api/admin/feedback.py
 
Router for resident feedback management.
Handles listing all submitted feedback entries and
individual or bulk deletion by admin.
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


# =================================================================================
# INTERNAL HELPERS
# =================================================================================

def _format_feedback_for_admin(feedback):
    rfid_display = "Guest Mode"
    
    if feedback.resident:
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


# =================================================================================
# FEEDBACK RECORDS
# =================================================================================

@router.get(
    "",
    response_model=list[FeedbackAdminOut],
)
def list_feedbacks(db: Session = Depends(get_db)):
    feedbacks = get_all_feedbacks(db)
    return [_format_feedback_for_admin(fb) for fb in feedbacks]


# =================================================================================
# DELETION
# =================================================================================

@router.delete("/{feedback_id}")
def delete_feedback_record(feedback_id: int, db: Session = Depends(get_db)):
    success = delete_feedback(db, feedback_id)
    if not success:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return {"detail": "Feedback deleted"}


@router.post("/bulk-delete")
def bulk_delete_feedback_records(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    deleted_count = bulk_delete_feedbacks(db, ids)
    return {"detail": f"{deleted_count} feedbacks deleted"}