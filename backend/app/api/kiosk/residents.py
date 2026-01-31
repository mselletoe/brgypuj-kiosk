from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.services.resident_service import get_resident_autofill_data
from app.schemas.resident import ResidentAutofillOut

router = APIRouter(prefix="/residents")


@router.get(
    "/{resident_id}/autofill",
    response_model=ResidentAutofillOut,
    summary="Get resident data for form autofill"
)
def get_resident_for_autofill(
    resident_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves comprehensive resident data for autofilling document request forms.
    Includes computed fields like age and years of residency.
    """
    resident_data = get_resident_autofill_data(db, resident_id)
    
    if not resident_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    
    return resident_data