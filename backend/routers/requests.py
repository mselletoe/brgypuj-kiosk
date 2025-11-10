from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Request, RequestStatus, RequestType
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
    document_type: str
    form_data: Optional[Dict[str, Any]] = {}
    status: str
    price: int

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

    # Fetch the request type for price & name
    request_type = db.query(RequestType).filter_by(id=req.request_type_id).first()
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")

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
        "document_type": request_type.request_type_name,  # include this
        "price": request_type.price,                      # include this
        "form_data": new_request.form_data,
        "status": pending_status.name
    }

# ----------------------------
# Get all requests
# ----------------------------
@router.get("/", response_model=list[RequestOut])
def get_requests(db: Session = Depends(get_db)):
    requests = db.query(Request).options(joinedload(Request.request_type)).all()
    output = []
    for r in requests:
        output.append({
            "id": r.id,
            "resident_id": r.resident_id,
            "request_type_id": r.request_type_id,
            "document_type": r.request_type.request_type_name if r.request_type else "Unknown",
            "form_data": r.form_data,
            "status": r.status_obj.name if r.status_obj else None,
            "price": r.request_type.price if r.request_type else 0,
        })
    return output