from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import RequestType
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter( prefix="/request-types", tags=["Request Types"] )

# --- Pydantic Schemas ---
class RequestTypeBase(BaseModel):
    request_type_name: str
    description: Optional[str] = None
    template_id: Optional[int] = None
    status: Optional[str] = "active"
    price: Optional[float] = 0.0

class RequestTypeCreate(RequestTypeBase):
    pass

class RequestTypeUpdate(RequestTypeBase):
    pass

class RequestTypeOut(RequestTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# --- CRUD Endpoints ---

@router.get("/", response_model=List[RequestTypeOut])
def get_all_request_types(db: Session = Depends(get_db)):
    return db.query(RequestType).all()

@router.post("/", response_model=RequestTypeOut)
def create_request_type(req: RequestTypeCreate, db: Session = Depends(get_db)):
    new_type = RequestType(**req.dict())
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    return new_type

@router.put("/{id}", response_model=RequestTypeOut)
def update_request_type(id: int, req: RequestTypeUpdate, db: Session = Depends(get_db)):
    existing = db.query(RequestType).filter(RequestType.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Request type not found")

    for key, value in req.dict(exclude_unset=True).items():
        setattr(existing, key, value)
    existing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/{id}")
def delete_request_type(id: int, db: Session = Depends(get_db)):
    existing = db.query(RequestType).filter(RequestType.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Request type not found")
    db.delete(existing)
    db.commit()
    return {"message": "Request type deleted successfully"}