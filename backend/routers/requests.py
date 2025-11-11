from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Request, RequestStatus, RequestType
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy import func

router = APIRouter(prefix="/requests", tags=["Requests"])

# ----------------------------
# Pydantic Schemas
# ----------------------------
class RequestCreate(BaseModel):
    resident_id: Optional[int] = None
    request_type_id: int
    form_data: Optional[Dict[str, Any]] = {}

    class Config:
        extra = "allow"

class RequestOut(BaseModel):
    id: int
    resident_id: Optional[int]
    request_type_id: Optional[int] = None
    document_type: str
    price: int
    form_data: Optional[Dict[str, Any]] = {}
    status: str
    created_at: str
    payment_status: Optional[str] = "Unpaid"

# Pydantic model for updating status
class StatusUpdateSchema(BaseModel):
    status_name: str

# ----------------------------
# Helper to get or create status
# ----------------------------
def get_status(db: Session, name: str):
    status = db.query(RequestStatus).filter_by(name=name).first()
    if not status:
        status = RequestStatus(name=name)
        db.add(status)
        db.commit()
        db.refresh(status)
    return status

# ----------------------------
# Create a new request
# ----------------------------
@router.post("/", response_model=RequestOut)
def create_request(req: RequestCreate, db: Session = Depends(get_db)):
    pending_status = get_status(db, "pending") 

    request_type = db.query(RequestType).filter_by(id=req.request_type_id).first()
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")

    new_request = Request(
        resident_id=req.resident_id,
        request_type_id=req.request_type_id,
        status_id=pending_status.id,
        form_data=req.form_data,
        payment_status="Unpaid",
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "id": new_request.id,
        "resident_id": new_request.resident_id,
        "request_type_id": new_request.request_type_id,
        "document_type": request_type.request_type_name,
        "price": request_type.price,
        "form_data": new_request.form_data,
        "status": pending_status.name,
        "created_at": new_request.created_at.isoformat(),
        "payment_status": new_request.payment_status,
    }

# ----------------------------
# Get all requests
# ----------------------------
@router.get("/", response_model=list[RequestOut])
def get_requests(db: Session = Depends(get_db)):
    results = db.query(Request).options(joinedload(Request.request_type)).all()
    output = []
    for r in results:
        output.append({
            "id": r.id,
            "resident_id": r.resident_id,
            "request_type_id": r.request_type_id,
            "document_type": r.request_type.request_type_name if r.request_type else "Unknown",
            "price": r.request_type.price if r.request_type else 0,
            "form_data": r.form_data,
            "status": r.status_obj.name if r.status_obj else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "payment_status": r.payment_status,
        })
    return output

# ----------------------------
# Toggle Payment Status (Paid / Unpaid)
# ----------------------------
@router.put("/{request_id}/payment")
def toggle_payment_status(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.payment_status = "Paid" if req.payment_status != "Paid" else "Unpaid"
    req.updated_at = func.now()

    db.commit()
    db.refresh(req)

    return {"message": "Payment status updated", "payment_status": req.payment_status}

# ----------------------------
# Update Request Status (Generic)
# ----------------------------
@router.put("/{request_id}/status")  
def update_request_status(request_id: int, payload: StatusUpdateSchema, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    status = get_status(db, payload.status_name)
    req.status_id = status.id
    req.updated_at = func.now()

    db.commit()
    db.refresh(req)

    return {"message": f"Request status updated to '{payload.status_name}'", "status": payload.status_name}

# ----------------------------
# Approve Request (Move to processing)
# ----------------------------
@router.put("/{request_id}/approve") 
def approve_request(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    if req.payment_status != "Paid":
        raise HTTPException(status_code=400, detail="Cannot approve unpaid request")

    processing_status = get_status(db, "processing")
    req.status_id = processing_status.id
    req.updated_at = func.now()

    db.commit()
    db.refresh(req)

    return {"message": "Request approved and moved to processing", "status": "processing"}