from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db

router = APIRouter()

@router.get("/health")
def admin_health(db: Session = Depends(get_db)):
    return {"status": "admin ok"}
