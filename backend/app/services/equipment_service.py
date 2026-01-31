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
    requested_quantity: int
) -> bool:
    equipment = _validate_equipment_item(db, item_id)

    if equipment.available_quantity < requested_quantity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only {equipment.available_quantity} units of '{equipment.name}' available"
        )

    return True


def _calculate_total_cost(
    db: Session,
    items: list,
    borrow_date: datetime,
    return_date: datetime
) -> float:
    
    days = max(1, (return_date - borrow_date).days)
    
    total_cost = 0
    
    for item in items:
        equipment = _validate_equipment_item(db, item.item_id)
        item_cost = float(equipment.rate_per_day) * item.quantity * days
        total_cost += item_cost
    
    return total_cost


def _generate_transaction_no(db: Session) -> str:
    while True:
        number = random.randint(1000, 9999)
        transaction_no = f"ER-{number}"
        exists = db.query(EquipmentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


def _update_equipment_availability(db: Session, request_id: int, action: str):
    request = db.query(EquipmentRequest).filter(EquipmentRequest.id == request_id).first()
    
    if not request:
        return
    
    for item in request.items:
        equipment = db.query(EquipmentInventory).filter(
            EquipmentInventory.id == item.item_id
        ).first()
        
        if not equipment:
            continue
        
        if action == "decrease":
            equipment.available_quantity -= item.quantity
        elif action == "increase":
            equipment.available_quantity += item.quantity
        
        equipment.available_quantity = max(0, min(equipment.available_quantity, equipment.total_quantity))


# -------------------------------------------------
# Kiosk Service Functions
# -------------------------------------------------

def get_available_equipment(db: Session):
    return (
        db.query(EquipmentInventory)
        .order_by(EquipmentInventory.name.asc())
        .all()
    )


def get_equipment_autofill_data(db: Session, resident_id: int) -> EquipmentAutofillData:
    from app.services.resident_service import get_resident_autofill_data
    
    resident_data = get_resident_autofill_data(db, resident_id)
    
    if not resident_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )
    
    # Map resident data to equipment form fields
    return EquipmentAutofillData(
        contact_person=resident_data['full_name'],
        contact_number=resident_data['phone_number']
    )


def create_equipment_request(
    db: Session, 
    payload: EquipmentRequestCreate
) -> EquipmentRequestKioskResponse:

    if payload.resident_id is not None:
        _validate_resident(db, payload.resident_id)
    
    for item in payload.items:
        _validate_equipment_item(db, item.item_id)
        _check_equipment_availability(
            db,
            item.item_id,
            item.quantity
        )
    
    total_cost = _calculate_total_cost(
        db,
        payload.items,
        payload.borrow_date,
        payload.return_date
    )
    
    request = EquipmentRequest(
        resident_id=payload.resident_id,
        contact_person=payload.contact_person,
        contact_number=payload.contact_number,
        purpose=payload.purpose,
        borrow_date=payload.borrow_date,
        return_date=payload.return_date,
        total_cost=total_cost,
        transaction_no=_generate_transaction_no(db)
    )
    
    db.add(request)
    db.flush()
    
    for item in payload.items:
        request_item = EquipmentRequestItem(
            equipment_request_id=request.id,
            item_id=item.item_id,
            quantity=item.quantity
        )
        db.add(request_item)
    
    db.flush()

    _update_equipment_availability(db, request.id, "decrease")

    db.commit()
    db.refresh(request)
    
    return EquipmentRequestKioskResponse(
        transaction_no=request.transaction_no,
        total_cost=request.total_cost
    )


def get_kiosk_request_history(db: Session, resident_id: int):
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
    return (
        db.query(EquipmentInventory)
        .order_by(EquipmentInventory.name.asc())
        .all()
    )


def create_equipment_inventory(db: Session, payload: EquipmentInventoryCreate):
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

    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.id == equipment_id)
        .first()
    )
    
    if not equipment:
        return None
    
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
    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.id == equipment_id)
        .first()
    )
    
    if not equipment:
        return None
    
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


def bulk_delete_equipment_inventory(db: Session, ids: list[int]):
    equipment_items = db.query(EquipmentInventory).filter(EquipmentInventory.id.in_(ids)).all()
    
    deleted_count = 0
    
    for equipment in equipment_items:
        in_use = (
            db.query(EquipmentRequestItem)
            .filter(EquipmentRequestItem.item_id == equipment.id)
            .count()
        )
        
        if in_use == 0:
            db.delete(equipment)
            deleted_count += 1
    
    db.commit()
    return deleted_count


# -------------------------------------------------
# Equipment Request Management (Admin)
# -------------------------------------------------

def _get_request(db: Session, request_id: int):
    return db.query(EquipmentRequest).filter(EquipmentRequest.id == request_id).first()


def get_all_equipment_requests(db: Session):
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
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status != "Pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve request with status: {req.status}"
        )
    
    req.status = "Approved"
    db.commit()
    return True


def reject_equipment_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status == "Pending":
        _update_equipment_availability(db, request_id, "increase")

    req.status = "Rejected"
    db.commit()
    return True


def mark_as_picked_up(db: Session, request_id: int):
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
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status != "Picked-Up":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only mark Picked-Up requests as Returned"
        )
    
    _update_equipment_availability(db, request_id, "increase")
    
    req.status = "Returned"
    req.returned_at = datetime.now()
    db.commit()
    return True


def mark_request_paid(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.payment_status = "paid"
    db.commit()
    return True


def mark_request_unpaid(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.payment_status = "unpaid"
    db.commit()
    return True


def toggle_refund_status(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    
    req.is_refunded = not req.is_refunded
    db.commit()
    return True


def undo_equipment_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False

    status_undo_map = {
        "Approved": "Pending",
        "Picked-Up": "Approved",
        "Returned": "Picked-Up",
        "Rejected": "Pending",
    }

    if req.status not in status_undo_map:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Undo is not available for status: {req.status}"
        )

    old_status = req.status
    new_status = status_undo_map[old_status]

    if old_status in ("Rejected", "Returned"):
        _update_equipment_availability(db, request_id, "decrease")

    req.status = new_status

    if new_status == "Picked-Up":
        req.returned_at = None

    db.commit()
    return True


def bulk_undo_equipment_requests(db: Session, ids: list[int]):
    requests = db.query(EquipmentRequest).filter(
        EquipmentRequest.id.in_(ids)
    ).all()

    status_undo_map = {
        "Approved": "Pending",
        "Picked-Up": "Approved",
        "Returned": "Picked-Up",
        "Rejected": "Pending",
    }

    updated_count = 0

    for req in requests:
        if req.status not in status_undo_map:
            continue

        old_status = req.status
        new_status = status_undo_map[old_status]

        if old_status in ("Rejected", "Returned"):
            _update_equipment_availability(db, req.id, "decrease")

        req.status = new_status

        if new_status == "Picked-Up":
            req.returned_at = None

        updated_count += 1

    db.commit()
    return updated_count


def delete_equipment_request(db: Session, request_id: int):
    req = _get_request(db, request_id)
    if not req:
        return False
    
    if req.status in ["Pending", "Approved", "Picked-Up"]:
        _update_equipment_availability(db, request_id, "increase")
    
    db.delete(req)
    db.commit()
    return True


def bulk_delete_equipment_requests(db: Session, ids: list[int]):
    requests = db.query(EquipmentRequest).filter(EquipmentRequest.id.in_(ids)).all()
    
    for req in requests:
        if req.status in ["Pending", "Approved", "Picked-Up"]:
            _update_equipment_availability(db, req.id, "increase")
    
    count = len(requests)
    
    for req in requests:
        db.delete(req)
    
    db.commit()
    return count


def get_request_notes(db: Session, request_id: int) -> str:
    req = _get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    return req.notes or ""


def update_request_notes(db: Session, request_id: int, notes: str) -> str:
    req = _get_request(db, request_id)
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    req.notes = notes
    db.commit()
    db.refresh(req)
    return req.notes