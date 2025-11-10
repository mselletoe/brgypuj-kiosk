from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Request, RequestStatus
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter(prefix="/requests", tags=["Requests"])

# ----------------------------
# Pydantic Schemas
# ----------------------------
class RequestCreate(BaseModel):
    resident_id: Optional[int] = None  # null for guest
    request_type_id: int
    form_data: Optional[Dict[str, Any]] = {}  # dynamic fields

    class Config:
        extra = "allow"

class RequestOut(BaseModel):
    id: int
    resident_id: Optional[int]
    request_type_id: int
    form_data: Optional[Dict[str, Any]] = {}
    status: str

# ----------------------------
# Helper to get default pending status
# ----------------------------
def get_pending_status(db: Session):
    status = db.query(RequestStatus).filter_by(name="pending").first()
    if not status:
        # create pending if not exists
        status = RequestStatus(name="pending")
        db.add(status)
        db.commit()
        db.refresh(status)
    return status

# ----------------------------
# Create a new request
# ----------------------------
@router.post("/", response_model=RequestOut)
def create_request(req: RequestCreate, db: Session = Depends(get_db)):
    pending_status = get_pending_status(db)

    new_request = Request(
        resident_id=req.resident_id,
        request_type_id=req.request_type_id,
        status_id=pending_status.id,
        form_data=req.form_data
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "id": new_request.id,
        "resident_id": new_request.resident_id,
        "request_type_id": new_request.request_type_id,
        "form_data": new_request.form_data,
        "status": pending_status.name
    }

# ----------------------------
# Get all requests
# ----------------------------
@router.get("/", response_model=list[RequestOut])
def get_requests(db: Session = Depends(get_db)):
    results = db.query(Request).all()
    output = []
    for r in results:
        output.append({
            "id": r.id,
            "resident_id": r.resident_id,
            "request_type_id": r.request_type_id,
            "form_data": r.form_data,
            "status": r.status_obj.name if r.status_obj else None
        })
    return output