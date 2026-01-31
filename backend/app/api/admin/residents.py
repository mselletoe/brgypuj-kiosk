from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.schemas.resident import ResidentResponse
from app.services.resident_service import get_all_residents
from app.api.deps import get_db

router = APIRouter(prefix="/residents")

@router.get("/", response_model=List[ResidentResponse])
def read_residents(db: Session = Depends(get_db)):
    """
    Get all residents.
    """
    return get_all_residents(db)