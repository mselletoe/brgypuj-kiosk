"""
Equipment Borrowing Service Layer
---------------------------
Handles the business logic for equipment management, including administrative 
configuration of equipment inventory and resident-facing borrowing request processing.
"""
import random
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import HTTPException, status
from app.models.equipment import EquipmentInventory, EquipmentRequest, EquipmentRequestItem
from app.models.resident import Resident, ResidentRFID
from app.schemas.equipment import (
    EquipmentRequestCreate,
    EquipmentRequestKioskResponse,
    EquipmentInventoryCreate,
    EquipmentInventoryUpdate,
    EquipmentAutofillData,
)


# -------------------------------------------------
# Internal Helpers
# -------------------------------------------------

def _validate_equipment_item(db: Session, item_id: int) -> EquipmentInventory:
    """
    Verifies the existence of a specific equipment item in inventory.
    """
    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.id == item_id)
        .first()
    )

    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Equipment item with ID {item_id} not found"
        )

    return equipment


def _validate_resident(db: Session, resident_id: int) -> Resident:
    """
    Ensures the resident exists in the database.
    """
    resident = db.query(Resident).filter(Resident.id == resident_id).first()

    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    return resident


def _check_equipment_availability(
    db: Session, 
    item_id: int, 
    requested_quantity: int,
    borrow_date: datetime,
    return_date: datetime
) -> bool:
    """
    Checks if the requested quantity of equipment is available during the specified period.
    Considers existing approved/picked-up requests that overlap with the requested dates.
    """
    equipment = _validate_equipment_item(db, item_id)
    
    # Find overlapping requests that are approved or picked-up
    overlapping_requests = (
        db.query(EquipmentRequestItem)
        .join(EquipmentRequest)
        .filter(
            EquipmentRequestItem.item_id == item_id,
            EquipmentRequest.status.in_(['Approved', 'Picked-Up']),
            and_(
                EquipmentRequest.borrow_date < return_date,
                EquipmentRequest.return_date > borrow_date
            )
        )
        .all()
    )
    
    # Calculate total quantity already borrowed during this period
    borrowed_quantity = sum(item.quantity for item in overlapping_requests)
    
    # Check if enough equipment is available
    available = equipment.available_quantity - borrowed_quantity
    
    if available < requested_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {available} units of '{equipment.name}' available during this period"
        )
    
    return True


def _calculate_total_cost(
    db: Session,
    items: list,
    borrow_date: datetime,
    return_date: datetime
) -> float:
    """
    Calculates the total cost for borrowing equipment based on:
    - Number of days (rounded up)
    - Quantity of each item
    - Rate per day for each item
    """
    # Calculate number of days (minimum 1 day)
    days = max(1, (return_date - borrow_date).days)
    
    total_cost = 0
    
    for item in items:
        equipment = _validate_equipment_item(db, item.item_id)
        item_cost = float(equipment.rate_per_day) * item.quantity * days
        total_cost += item_cost
    
    return total_cost


def _generate_transaction_no(db: Session) -> str:
    """
    Generates a unique transaction number in the format ER-XXXX (Equipment Request)
    """
    while True:
        number = random.randint(1000, 9999)
        transaction_no = f"ER-{number}"
        exists = db.query(EquipmentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


def _update_equipment_availability(db: Session, request_id: int, status_change: str):
    """
    Updates equipment availability based on request status changes.
    - Approved: Decrease available quantity
    - Returned/Rejected: Increase available quantity back
    """
    request = db.query(EquipmentRequest).filter(EquipmentRequest.id == request_id).first()
    
    if not request:
        return
    
    for item in request.items:
        equipment = db.query(EquipmentInventory).filter(
            EquipmentInventory.id == item.item_id
        ).first()
        
        if not equipment:
            continue
        
        if status_change == "approve":
            # Decrease available quantity when approved
            equipment.available_quantity -= item.quantity
        elif status_change == "return_or_reject":
            # Increase available quantity when returned or rejected
            equipment.available_quantity += item.quantity
        
        # Ensure we don't go below 0 or above total
        equipment.available_quantity = max(0, min(equipment.available_quantity, equipment.total_quantity))


# -------------------------------------------------
# Kiosk Service Functions
# -------------------------------------------------

def get_available_equipment(db: Session):
    """
    Retrieves all equipment items in inventory for the kiosk display.
    """
    return (
        db.query(EquipmentInventory)
        .order_by(EquipmentInventory.name.asc())
        .all()
    )


def get_equipment_autofill_data(db: Session, resident_id: int) -> EquipmentAutofillData:
    """
    Retrieves resident data for autofilling the borrowing form.
    Uses the resident_service function for consistency.
    """
    from app.services.resident_service import get_resident_autofill_data
    
    resident_data = get_resident_autofill_data(db, resident_id)
    
    if not resident_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    
    # Map resident data to equipment form fields
    return EquipmentAutofillData(
        borrower_name=resident_data['full_name'],
        contact_person=resident_data['full_name'],
        contact_number=resident_data['phone_number']
    )


def create_equipment_request(
    db: Session, 
    payload: EquipmentRequestCreate
) -> EquipmentRequestKioskResponse:
    """
    Processes a new equipment borrowing request from the kiosk.
    Executes comprehensive validation of the resident, equipment availability, 
    and borrowing period.
    """
    
    # 1. Validate resident if provided
    if payload.resident_id is not None:
        _validate_resident(db, payload.resident_id)
    
    # 2. Validate all requested equipment items and check availability
    for item in payload.items:
        _validate_equipment_item(db, item.item_id)
        _check_equipment_availability(
            db,
            item.item_id,
            item.quantity,
            payload.borrow_date,
            payload.return_date
        )
    
    # 3. Calculate total cost
    total_cost = _calculate_total_cost(
        db,
        payload.items,
        payload.borrow_date,
        payload.return_date
    )
    
    # 4. Create the equipment request
    request = EquipmentRequest(
        resident_id=payload.resident_id,
        borrower_name=payload.borrower_name,
        contact_person=payload.contact_person,
        contact_number=payload.contact_number,
        purpose=payload.purpose,
        borrow_date=payload.borrow_date,
        return_date=payload.return_date,
        total_cost=total_cost,
        transaction_no=_generate_transaction_no(db)
    )
    
    db.add(request)
    db.flush()  # Get the request ID without committing
    
    # 5. Add equipment items to the request
    for item in payload.items:
        request_item = EquipmentRequestItem(
            equipment_request_id=request.id,
            item_id=item.item_id,
            quantity=item.quantity
        )
        db.add(request_item)
    
    db.commit()
    db.refresh(request)
    
    return EquipmentRequestKioskResponse(
        transaction_no=request.transaction_no,
        total_cost=request.total_cost
    )


def get_kiosk_request_history(db: Session, resident_id: int):
    """
    Retrieves the equipment borrowing history for a specific resident.
    """
    from sqlalchemy.orm import joinedload
    
    return (
        db.query(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.items).joinedload(EquipmentRequestItem.inventory_item)
        )
        .filter(EquipmentRequest.resident_id == resident_id)
        .order_by(EquipmentRequest.requested_at.desc())
        .all()
    )


# -------------------------------------------------
# Equipment Inventory Management (Admin)
# -------------------------------------------------

def get_all_equipment_inventory(db: Session):
    """
    Admin: Lists all equipment items in inventory.
    """
    return (
        db.query(EquipmentInventory)
        .order_by(EquipmentInventory.name.asc())
        .all()
    )


def create_equipment_inventory(db: Session, payload: EquipmentInventoryCreate):
    """
    Admin: Adds a new equipment item to inventory.
    """
    # Check for duplicate name
    existing = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.name == payload.name)
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Equipment item '{payload.name}' already exists"
        )
    
    equipment = EquipmentInventory(
        name=payload.name,
        total_quantity=payload.total_quantity,
        available_quantity=payload.available_quantity,
        rate_per_day=payload.rate_per_day,
    )
    
    db.add(equipment)
    db.commit()
    db.refresh(equipment)
    
    return equipment


def update_equipment_inventory(
    db: Session, 
    equipment_id: int, 
    payload: EquipmentInventoryUpdate
):
    """
    Admin: Updates an existing equipment item in inventory.
    """
    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.id == equipment_id)
        .first()
    )
    
    if not equipment:
        return None
    
    # Check for duplicate name if name is being updated
    if payload.name and payload.name != equipment.name:
        existing = (
            db.query(EquipmentInventory)
            .filter(EquipmentInventory.name == payload.name)
            .first()
        )
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Equipment item '{payload.name}' already exists"
            )
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(equipment, field, value)
    
    db.commit()
    db.refresh(equipment)
    
    return equipment


def delete_equipment_inventory(db: Session, equipment_id: int):
    """
    Admin: Deletes an equipment item from inventory.
    Prevents deletion if the item is referenced in any requests.
    """
    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.id == equipment_id)
        .first()
    )
    
    if not equipment:
        return None
    
    # Check if equipment is used in any requests
    in_use = (
        db.query(EquipmentRequestItem)
        .filter(EquipmentRequestItem.item_id == equipment_id)
        .count()
    )
    
    if in_use > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete equipment: it is referenced in existing requests"
        )
    
    db.delete(equipment)
    db.commit()
    
    return True


# -------------------------------------------------
# Equipment Request Management (Admin)
# -------------------------------------------------

def _get_request(db: Session, request_id: int):
    """Helper to get a request by ID"""
    return db.query(EquipmentRequest).filter(EquipmentRequest.id == request_id).first()


def get_all_equipment_requests(db: Session):
    """
    Admin: Monitors all incoming equipment borrowing requests with resident information.
    """
    from sqlalchemy.orm import joinedload
    
    return (
        db.query(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.resident).joinedload(Resident.rfids),
            joinedload(EquipmentRequest.items).joinedload(EquipmentRequestItem.inventory_item)
        )
        .order_by(EquipmentRequest.requested_at.desc())
        .all()
    )


def get_equipment_request_by_id(db: Session, request_id: int):
    """
    Admin: Fetches detailed information for a specific equipment request.
    """
    from sqlalchemy.orm import joinedload
    
    return (
        db.query(EquipmentRequest)
        .options(
            joinedload(EquipmentRequest.resident).joinedload(Resident.rfids),
            joinedload(EquipmentRequest.items).joinedload(EquipmentRequestItem.inventory_item)
        )
        .filter(EquipmentRequest.id == request_id)
        .first()
    )


def approve_equipment_request(db: Session, request_id: int):
    """
    Admin: Approves an equipment request and decreases available inventory.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status: {req.status}"
        )
    
    # Update inventory availability
    _update_equipment_availability(db, request_id, "approve")
    
    req.status = "Approved"
    db.commit()
    return True


def reject_equipment_request(db: Session, request_id: int):
    """
    Admin: Rejects an equipment request.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.status = "Rejected"
    db.commit()
    return True


def mark_as_picked_up(db: Session, request_id: int):
    """
    Admin: Marks an approved request as picked up.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status != "Approved":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only mark Approved requests as Picked-Up"
        )
    
    req.status = "Picked-Up"
    db.commit()
    return True


def mark_as_returned(db: Session, request_id: int):
    """
    Admin: Marks equipment as returned and increases available inventory.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status != "Picked-Up":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only mark Picked-Up requests as Returned"
        )
    
    # Update inventory availability
    _update_equipment_availability(db, request_id, "return_or_reject")
    
    req.status = "Returned"
    req.returned_at = datetime.now()
    db.commit()
    return True


def mark_request_paid(db: Session, request_id: int):
    """
    Admin: Marks an equipment request as paid.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.payment_status = "paid"
    db.commit()
    return True


def mark_request_unpaid(db: Session, request_id: int):
    """
    Admin: Marks an equipment request as unpaid.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.payment_status = "unpaid"
    db.commit()
    return True


def toggle_refund_status(db: Session, request_id: int):
    """
    Admin: Toggles the refund status of a request.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.is_refunded = not req.is_refunded
    db.commit()
    return True


def undo_equipment_request(db: Session, request_id: int):
    """
    Moves a request back to its previous status based on current status:
    - Approved → Pending (restore inventory)
    - Picked-Up → Approved
    - Returned → Picked-Up (decrease inventory)
    - Rejected → Pending
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    # Define status transitions for undo
    status_undo_map = {
        "Approved": "Pending",
        "Picked-Up": "Approved",
        "Returned": "Picked-Up",
        "Rejected": "Pending",
    }
    
    # Check if undo is allowed for current status
    if req.status not in status_undo_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Undo is not available for status: {req.status}"
        )
    
    # Handle inventory adjustments
    if req.status == "Approved":
        # Undoing approval: restore inventory
        _update_equipment_availability(db, request_id, "return_or_reject")
    elif req.status == "Returned":
        # Undoing return: decrease inventory again
        _update_equipment_availability(db, request_id, "approve")
    
    # Update to previous status
    req.status = status_undo_map[req.status]
    
    # Clear returned_at if undoing from Returned
    if status_undo_map[req.status] == "Picked-Up":
        req.returned_at = None
    
    db.commit()
    return True


def bulk_undo_equipment_requests(db: Session, ids: list[int]):
    """
    Bulk undo operation for multiple equipment requests.
    Only processes requests that are in undoable states.
    """
    requests = db.query(EquipmentRequest).filter(EquipmentRequest.id.in_(ids)).all()
    
    status_undo_map = {
        "Approved": "Pending",
        "Picked-Up": "Approved",
        "Returned": "Picked-Up",
        "Rejected": "Pending",
    }
    
    updated_count = 0
    for req in requests:
        if req.status in status_undo_map:
            # Handle inventory adjustments
            if req.status == "Approved":
                _update_equipment_availability(db, req.id, "return_or_reject")
            elif req.status == "Returned":
                _update_equipment_availability(db, req.id, "approve")
            
            req.status = status_undo_map[req.status]
            
            if status_undo_map[req.status] == "Picked-Up":
                req.returned_at = None
            
            updated_count += 1
    
    db.commit()
    return updated_count


def delete_equipment_request(db: Session, request_id: int):
    """
    Admin: Deletes an equipment request.
    Restores inventory if the request was approved or picked up.
    """
    req = _get_request(db, request_id)
    if not req:
        return False
    
    # If request was approved or picked-up, restore inventory
    if req.status in ["Approved", "Picked-Up"]:
        _update_equipment_availability(db, request_id, "return_or_reject")
    
    db.delete(req)
    db.commit()
    return True


def bulk_delete_equipment_requests(db: Session, ids: list[int]):
    """
    Admin: Bulk deletes multiple equipment requests.
    Restores inventory for approved/picked-up requests.
    """
    requests = db.query(EquipmentRequest).filter(EquipmentRequest.id.in_(ids)).all()
    
    for req in requests:
        if req.status in ["Approved", "Picked-Up"]:
            _update_equipment_availability(db, req.id, "return_or_reject")
    
    count = len(requests)
    
    for req in requests:
        db.delete(req)
    
    db.commit()
    return count


def get_request_notes(db: Session, request_id: int) -> str:
    """
    Admin: Retrieves notes for a specific request.
    """
    req = _get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req.notes or ""


def update_request_notes(db: Session, request_id: int, notes: str) -> str:
    """
    Admin: Updates notes for a specific request.
    """
    req = _get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.notes = notes
    db.commit()
    db.refresh(req)
    return req.notes