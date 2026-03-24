"""
app/api/admin/equipment.py

Router for admin equipment management.
Handles inventory CRUD and equipment request lifecycle
(approve, reject, pickup, return, payment, refund, undo, notes).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.equipment import (
    EquipmentInventoryOut,
    EquipmentInventoryCreate,
    EquipmentInventoryUpdate,
    EquipmentRequestAdminOut,
    EquipmentRequestAdminDetail,
)
from app.services import equipment_service

router = APIRouter(prefix="/equipment")


# =================================================================================
# INTERNAL HELPERS
# =================================================================================
def _format_equipment_item(item):
    return {
        "id": item.id,
        "item_id": item.item_id,
        "item_name": item.inventory_item.name if item.inventory_item else "",
        "quantity": item.quantity,
        "rate_per_day": item.inventory_item.rate_per_day if item.inventory_item else 0,
    }


def _format_request_for_admin(request):
    rfid_display = None
    phone_number = None

    if request.resident and hasattr(request.resident, 'rfids'):
        active_rfid = next(
            (rfid.rfid_uid for rfid in request.resident.rfids if rfid.is_active),
            None
        )
        rfid_display = active_rfid
        phone_number = request.resident.phone_number

    return {
        "id": request.id,
        "transaction_no": request.transaction_no,
        "resident_id": request.resident_id,
        "resident_first_name": request.resident.first_name if request.resident else None,
        "resident_middle_name": request.resident.middle_name if request.resident else None,
        "resident_last_name": request.resident.last_name if request.resident else None,
        "resident_rfid": rfid_display,
        "resident_phone": phone_number,
        "contact_person": request.contact_person,
        "contact_number": request.contact_number,
        "purpose": request.purpose,
        "status": request.status,
        "borrow_date": request.borrow_date,
        "return_date": request.return_date,
        "returned_at": request.returned_at,
        "total_cost": request.total_cost,
        "payment_status": request.payment_status,
        "is_refunded": request.is_refunded,
        "notes": request.notes,
        "requested_at": request.requested_at,
        "items": [_format_equipment_item(item) for item in request.items],
    }


def _format_request_detail(request):
    base_data = _format_request_for_admin(request)
    
    resident_name = None
    if request.resident:
        parts = []
        if request.resident.first_name:
            parts.append(request.resident.first_name)
        if request.resident.middle_name:
            parts.append(request.resident.middle_name)
        if request.resident.last_name:
            parts.append(request.resident.last_name)
        resident_name = " ".join(parts) if parts else None
    
    borrowing_period_days = max(1, (request.return_date - request.borrow_date).days)
    
    base_data["resident_name"] = resident_name
    base_data["borrowing_period_days"] = borrowing_period_days
    
    return base_data


# =================================================================================
# INVENTORY
# =================================================================================
@router.get("/inventory", response_model=List[EquipmentInventoryOut])
def get_equipment_inventory(db: Session = Depends(get_db)):
    return equipment_service.get_all_equipment_inventory(db)


@router.post("/inventory", response_model=EquipmentInventoryOut, status_code=status.HTTP_201_CREATED)
def create_equipment_item(
    payload: EquipmentInventoryCreate,
    db: Session = Depends(get_db)
):
    return equipment_service.create_equipment_inventory(db, payload)


@router.put("/inventory/{equipment_id}", response_model=EquipmentInventoryOut)
def update_equipment_item(
    equipment_id: int,
    payload: EquipmentInventoryUpdate,
    db: Session = Depends(get_db)
):
    result = equipment_service.update_equipment_inventory(db, equipment_id, payload)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    return result


@router.delete("/inventory/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_item(equipment_id: int, db: Session = Depends(get_db)):
    result = equipment_service.delete_equipment_inventory(db, equipment_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    return None


@router.post("/inventory/bulk-delete", status_code=status.HTTP_200_OK)
def bulk_delete_inventory(ids: List[int], db: Session = Depends(get_db)):
    count = equipment_service.bulk_delete_equipment_inventory(db, ids)
    return {"message": f"{count} equipment item(s) deleted"}


# =================================================================================
# EQUIPMENT REQUESTS — READ
# =================================================================================
@router.get("/requests", response_model=List[EquipmentRequestAdminOut])
def get_equipment_requests(db: Session = Depends(get_db)):
    requests = equipment_service.get_all_equipment_requests(db)
    return [_format_request_for_admin(req) for req in requests]


@router.get("/requests/{request_id}", response_model=EquipmentRequestAdminDetail)
def get_equipment_request_detail(request_id: int, db: Session = Depends(get_db)):
    result = equipment_service.get_equipment_request_by_id(db, request_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return _format_request_detail(result)


# =================================================================================
# EQUIPMENT REQUESTS — LIFECYCLE ACTIONS
# =================================================================================
@router.post("/requests/{request_id}/approve", status_code=status.HTTP_200_OK)
def approve_request(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.approve_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request approved successfully"}


@router.post("/requests/{request_id}/reject", status_code=status.HTTP_200_OK)
def reject_request(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.reject_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request rejected successfully"}


@router.post("/requests/{request_id}/picked-up", status_code=status.HTTP_200_OK)
def mark_picked_up(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.mark_as_picked_up(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request marked as picked up"}


@router.post("/requests/{request_id}/returned", status_code=status.HTTP_200_OK)
def mark_returned(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.mark_as_returned(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Equipment marked as returned"}


@router.post("/requests/{request_id}/mark-paid", status_code=status.HTTP_200_OK)
def mark_paid(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.mark_request_paid(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request marked as paid"}


@router.post("/requests/{request_id}/mark-unpaid", status_code=status.HTTP_200_OK)
def mark_unpaid(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.mark_request_unpaid(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request marked as unpaid"}


@router.post("/requests/{request_id}/toggle-refund", status_code=status.HTTP_200_OK)
def toggle_refund(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.toggle_refund_status(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Refund status toggled"}


@router.post("/requests/{request_id}/undo", status_code=status.HTTP_200_OK)
def undo_request(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.undo_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request status reverted"}


@router.post("/requests/bulk-undo", status_code=status.HTTP_200_OK)
def bulk_undo(ids: List[int], db: Session = Depends(get_db)):
    count = equipment_service.bulk_undo_equipment_requests(db, ids)
    return {"message": f"{count} request(s) reverted"}


# =================================================================================
# EQUIPMENT REQUESTS — NOTES & DELETE
# =================================================================================
@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    success = equipment_service.delete_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return None


@router.post("/requests/bulk-delete", status_code=status.HTTP_200_OK)
def bulk_delete(ids: List[int], db: Session = Depends(get_db)):
    count = equipment_service.bulk_delete_equipment_requests(db, ids)
    return {"message": f"{count} request(s) deleted"}


@router.get("/requests/{request_id}/notes")
def get_notes(request_id: int, db: Session = Depends(get_db)):
    notes = equipment_service.get_request_notes(db, request_id)
    return {"notes": notes}


@router.put("/requests/{request_id}/notes")
def update_notes(request_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    notes = equipment_service.update_request_notes(db, request_id, payload.get("notes", ""))
    return {"notes": notes}