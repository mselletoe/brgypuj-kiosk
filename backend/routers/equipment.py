"""
================================================================================
File: equipment.py
Description:
    This router manages the complete Equipment Borrowing System.
    It handles inventory management, request processing, and the borrowing lifecycle.

    Key Features:
    1. Inventory Management:
       - View all equipment items and their stock levels.
       - Update item details (total quantity, available stock, rental rates).

    2. Request Management (Admin Side):
       - View all requests with optional status filtering.
       - Create single-item requests manually for walk-in residents.

    3. Kiosk Integration (Public Side):
       - specialized endpoint (`/kiosk/request`) to handle multi-item requests 
       - Deducts stock immediately upon request creation.

    4. Request Lifecycle Workflow:
       - Manages status transitions: Pending -> Paid -> Approved -> Picked-Up -> Returned.
       - Automatically adjusts inventory stock when items are Returned or Rejected.
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database import get_db
import models
from typing import List, Optional
from pydantic import BaseModel, ConfigDict # Import ConfigDict
import datetime # Import datetime for date formatting

# ==============================================================================
# Pydantic Schemas (Data Validation)
# ==============================================================================

class EquipmentItemUpdate(BaseModel):
    name: str
    total: int
    available: int
    rate: float

class RequestItem(BaseModel):
    id: int
    quantity: int

class RequestCreate(BaseModel):
    borrowerName: str
    contactNumber: str
    borrowDate: str
    returnDate: str
    purpose: str
    notes: Optional[str] = None
    selectedItem: int
    quantity: int
    totalCost: float
    
# --- Response Models ---

class ItemResponse(BaseModel):
    id: int
    name: str
    total_quantity: int
    available_quantity: int
    rate: float
    rate_per: str
    
    model_config = ConfigDict(from_attributes=True)

class RequestItemResponse(BaseModel):
    id: int
    quantity: int
    item: ItemResponse

    model_config = ConfigDict(from_attributes=True)

class RequestResponse(BaseModel):
    id: int
    borrower_name: str
    contact_number: Optional[str]
    purpose: Optional[str]
    notes: Optional[str]
    borrow_date: datetime.datetime
    return_date: datetime.datetime
    total_cost: float
    requested_via: Optional[str]
    status: str
    paid: bool
    refunded: bool
    created_at: datetime.datetime
    items: List[RequestItemResponse]

    model_config = ConfigDict(from_attributes=True)

# --- NEW SCHEMAS FOR KIOSK ---
class KioskRequestItem(BaseModel):
    id: int
    quantity: int

class KioskRequestDates(BaseModel):
    borrow: datetime.datetime
    return_date: datetime.datetime # Frontend must send 'return_date'
    days: int

class KioskRequestInfo(BaseModel):
    contactPerson: str
    contactNumber: str
    purpose: str
    notes: Optional[str] = None

class KioskRequestCreate(BaseModel):
    equipment: List[KioskRequestItem]
    dates: KioskRequestDates
    info: KioskRequestInfo
    total: float
# --- END OF NEW SCHEMAS ---


# ==============================================================================
# Router
# ==============================================================================

router = APIRouter(
    prefix="/equipment",
    tags=["Equipment"]
)

# === INVENTORY ENDPOINTS ===

@router.get("/inventory", response_model=List[ItemResponse])
def get_all_inventory(db: Session = Depends(get_db)):
    """
    Fetches all equipment inventory items.
    """
    inventory = db.query(models.EquipmentInventory).all()
    return inventory

@router.put("/inventory/{item_id}", response_model=ItemResponse)
def update_inventory_item(item_id: int, item_data: EquipmentItemUpdate, db: Session = Depends(get_db)):
    """
    Updates an inventory item.
    """
    db_item = db.query(models.EquipmentInventory).filter(models.EquipmentInventory.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.name = item_data.name
    db_item.total_quantity = item_data.total
    db_item.available_quantity = item_data.available
    db_item.rate = item_data.rate
    
    db.commit()
    db.refresh(db_item)
    
    return db_item

# === REQUEST ENDPOINTS ===

@router.get("/requests", response_model=List[RequestResponse])
def get_all_requests(status: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Fetches all equipment requests, optionally filtering by status.
    """
    query = db.query(models.EquipmentRequest)
    if status:
        query = query.filter(models.EquipmentRequest.status == status)
    
    requests = query.order_by(models.EquipmentRequest.created_at.desc()).all()
    return requests

@router.post("/requests", status_code=201)
def create_equipment_request(request_data: RequestCreate, db: Session = Depends(get_db)):
    """
    Creates a new equipment request (from Admin Panel).
    """
    
    db_item = db.query(models.EquipmentInventory).filter(models.EquipmentInventory.id == request_data.selectedItem).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Selected item not found")
    
    if request_data.quantity > db_item.available_quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")
        
    new_request = models.EquipmentRequest(
        borrower_name=request_data.borrowerName,
        contact_number=request_data.contactNumber,
        borrow_date=request_data.borrowDate,
        return_date=request_data.returnDate,
        purpose=request_data.purpose,
        notes=request_data.notes,
        total_cost=request_data.totalCost,
        requested_via="Admin", 
        status="Pending"
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    new_request_item = models.EquipmentRequestItem(
        request_id=new_request.id,
        item_id=db_item.id,
        quantity=request_data.quantity
    )
    db.add(new_request_item)
    
    db_item.available_quantity = db_item.available_quantity - request_data.quantity
    
    db.commit()
    
    return {"message": "Request created successfully", "request_id": new_request.id}

# --- Generic Status Update Function ---
def get_request_and_update(request_id: int, db: Session):
    db_request = db.query(models.EquipmentRequest).filter(models.EquipmentRequest.id == request_id).first()
    if not db_request:
        raise HTTPException(status_code=404, detail="Request not found")
    return db_request

# --- Status Update Endpoints ---

@router.put("/requests/{request_id}/pay")
def mark_request_paid(request_id: int, db: Session = Depends(get_db)):
    db_request = get_request_and_update(request_id, db)
    db_request.paid = True
    db.commit()
    return {"message": "Request marked as paid"}

@router.put("/requests/{request_id}/approve")
def approve_request(request_id: int, db: Session = Depends(get_db)):
    db_request = get_request_and_update(request_id, db)
    if not db_request.paid:
         raise HTTPException(status_code=400, detail="Request must be paid before approval")
    db_request.status = "Approved"
    db.commit()
    return {"message": "Request approved"}

@router.put("/requests/{request_id}/reject")
def reject_request(request_id: int, db: Session = Depends(get_db)):
    db_request = get_request_and_update(request_id, db)
    db_request.status = "Rejected"
    
    for item_link in db_request.items:
        db_item = db.query(models.EquipmentInventory).filter(models.EquipmentInventory.id == item_link.item_id).first()
        if db_item:
            db_item.available_quantity += item_link.quantity
            
    db.commit()
    return {"message": "Request rejected and stock returned"}

@router.put("/requests/{request_id}/pickup")
def mark_request_picked_up(request_id: int, db: Session = Depends(get_db)):
    db_request = get_request_and_update(request_id, db)
    if db_request.status != "Approved":
        raise HTTPException(status_code=400, detail="Only approved requests can be picked up")
    db_request.status = "Picked-Up"
    db.commit()
    return {"message": "Request marked as Picked-Up"}

@router.put("/requests/{request_id}/return")
def mark_request_returned(request_id: int, db: Session = Depends(get_db)):
    db_request = get_request_and_update(request_id, db)
    if db_request.status != "Picked-Up":
        raise HTTPException(status_code=400, detail="Only picked-up requests can be returned")
    db_request.status = "Returned"
    
    for item_link in db_request.items:
        db_item = db.query(models.EquipmentInventory).filter(models.EquipmentInventory.id == item_link.item_id).first()
        if db_item:
            db_item.available_quantity += item_link.quantity

    db.commit()
    return {"message": "Request marked as Returned and stock updated"}

@router.put("/requests/{request_id}/refund")
def issue_request_refund(request_id: int, db: Session = Depends(get_db)):
    db_request = get_request_and_update(request_id, db)
    if db_request.status != "Rejected":
        raise HTTPException(status_code=400, detail="Only rejected requests can be refunded")
    if not db_request.paid:
         raise HTTPException(status_code=400, detail="This request was not paid, no refund needed")
    
    db_request.refunded = True
    db.commit()
    return {"message": "Request marked as refunded"}

# --- NEW ENDPOINT FOR KIOSK ---
@router.post("/kiosk/request", status_code=201)
def create_kiosk_request(request_data: KioskRequestCreate, db: Session = Depends(get_db)):
    """
    Creates a new equipment request from the KIOSK interface.
    This handles multiple items in a single request.
    """
    
    # 1. Check stock for ALL items before doing anything
    for item_data in request_data.equipment:
        db_item = db.query(models.EquipmentInventory).filter(models.EquipmentInventory.id == item_data.id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail=f"Item ID {item_data.id} not found")
        if item_data.quantity > db_item.available_quantity:
            raise HTTPException(status_code=400, detail=f"Not enough stock for {db_item.name}")

    # 2. All items are in stock. Create the main request.
    new_request = models.EquipmentRequest(
        borrower_name=request_data.info.contactPerson,
        contact_number=request_data.info.contactNumber,
        borrow_date=request_data.dates.borrow,
        return_date=request_data.dates.return_date,
        purpose=request_data.info.purpose,
        notes=request_data.info.notes,
        total_cost=request_data.total,
        requested_via="Kiosk - Guest", # Set the source
        status="Pending",
        paid=False
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # 3. Create join table entries and update inventory
    for item_data in request_data.equipment:
        # Create the link
        new_request_item = models.EquipmentRequestItem(
            request_id=new_request.id,
            item_id=item_data.id,
            quantity=item_data.quantity
        )
        db.add(new_request_item)
        
        # Update the inventory count
        db_item = db.query(models.EquipmentInventory).filter(models.EquipmentInventory.id == item_data.id).first()
        if db_item:
            db_item.available_quantity -= item_data.quantity

    db.commit()
    
    return {"message": "Request created successfully", "request_id": new_request.id}