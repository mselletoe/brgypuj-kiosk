"""
================================================================================
File: request_types.py
Description:
    This module defines API routes for managing "Request Types" — structured
    templates for various document or service requests within the system.

    It provides CRUD (Create, Read, Update, Delete) functionality for
    request types, each containing:
      • A name and description
      • Status (e.g., active/inactive)
      • Optional dynamic fields used in forms
      • Price and availability information

    The Pydantic schemas defined here ensure data validation for both
    incoming requests and outgoing responses.
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import RequestType
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import datetime

# =============================================
# Initialize Router
# =============================================
router = APIRouter( prefix="/request-types", tags=["Request Types"] )


# ==============================================================================
# PYDANTIC SCHEMAS
# ==============================================================================

# Base schema: shared attributes for creation and update operations
class RequestTypeBase(BaseModel):
    request_type_name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    price: Optional[float] = 0.0
    fields: Optional[List[Any]] = []
    available: Optional[bool] = True

# Schema used when creating a new Request Type
class RequestTypeCreate(RequestTypeBase):
    pass

# Schema used when updating an existing Request Type
class RequestTypeUpdate(RequestTypeBase):
    pass

# Schema for data returned to the client
class RequestTypeOut(RequestTypeBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ==============================================================================
# CRUD ENDPOINTS
# ==============================================================================

# Retrieve all Request Types from the database
@router.get("/", response_model=List[RequestTypeOut])
def get_all_request_types(db: Session = Depends(get_db)):
    """
    ----------------------------------------------------------------------------
    Returns:
        List[RequestTypeOut]: All existing request types with full details.
    ----------------------------------------------------------------------------
    """
    return db.query(RequestType).all()

# Create a new Request Type
@router.post("/", response_model=RequestTypeOut)
def create_request_type(req: RequestTypeCreate, db: Session = Depends(get_db)):
    """
    ----------------------------------------------------------------------------
    Steps:
      1. Convert validated request body (Pydantic model) to dictionary.
      2. Insert it into the database using ORM.
      3. Commit and return the newly created record.

    Returns:
        RequestTypeOut: The created request type, including timestamps and ID.
    ----------------------------------------------------------------------------
    """
    new_type = RequestType(**req.dict())
    db.add(new_type)
    db.commit()
    db.refresh(new_type)
    return new_type

# Update an existing Request Type by ID
@router.put("/{id}", response_model=RequestTypeOut)
def update_request_type(id: int, req: RequestTypeUpdate, db: Session = Depends(get_db)):
    """
    ----------------------------------------------------------------------------
    Parameters:
        id (int): ID of the request type to update.
        req (RequestTypeUpdate): Updated data fields.

    Raises:
        HTTPException: If no Request Type is found for the given ID.

    Returns:
        RequestTypeOut: The updated Request Type with refreshed data.
    ----------------------------------------------------------------------------
    """
    existing = db.query(RequestType).filter(RequestType.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Request type not found")

    # Update only fields that were provided (exclude_unset avoids overwriting with None)
    for key, value in req.dict(exclude_unset=True).items():
        setattr(existing, key, value)

    # Update timestamp to reflect modification
    existing.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(existing)
    return existing

# Delete a Request Type by ID
@router.delete("/{id}")
def delete_request_type(id: int, db: Session = Depends(get_db)):
    """
    ----------------------------------------------------------------------------
    Parameters:
        id (int): The ID of the request type to remove.

    Raises:
        HTTPException: If the request type does not exist.

    Returns:
        dict: A confirmation message after successful deletion.
    ----------------------------------------------------------------------------
    """
    existing = db.query(RequestType).filter(RequestType.id == id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Request type not found")
    db.delete(existing)
    db.commit()
    return {"message": "Request type deleted successfully"}