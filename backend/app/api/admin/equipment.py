"""
Equipment Borrowing API - Admin Endpoints
---------------------------
Administrative endpoints for managing equipment inventory and processing
borrowing requests. Requires admin authentication.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
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


# =========================================================
# EQUIPMENT INVENTORY MANAGEMENT
# =========================================================

@router.get("/inventory", response_model=List[EquipmentInventoryOut])
def get_equipment_inventory(db: Session = Depends(get_db)):
    """
    **Admin:** Retrieve all equipment items in inventory.
    
    Returns comprehensive inventory information including:
    - Item name
    - Total quantity owned
    - Available quantity
    - Rate per day
    """
    return equipment_service.get_all_equipment_inventory(db)


@router.post("/inventory", response_model=EquipmentInventoryOut, status_code=status.HTTP_201_CREATED)
def create_equipment_item(
    payload: EquipmentInventoryCreate,
    db: Session = Depends(get_db)
):
    """
    **Admin:** Add a new equipment item to inventory.
    
    Request body should include:
    - name: Equipment item name (must be unique)
    - total_quantity: Total number of units owned
    - available_quantity: Number of units available (≤ total_quantity)
    - rate_per_day: Rental rate per day
    """
    return equipment_service.create_equipment_inventory(db, payload)


@router.put("/inventory/{equipment_id}", response_model=EquipmentInventoryOut)
def update_equipment_item(
    equipment_id: int,
    payload: EquipmentInventoryUpdate,
    db: Session = Depends(get_db)
):
    """
    **Admin:** Update an existing equipment item in inventory.
    
    Supports partial updates - only include fields you want to change.
    """
    result = equipment_service.update_equipment_inventory(db, equipment_id, payload)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    return result


@router.delete("/inventory/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_equipment_item(equipment_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Delete an equipment item from inventory.
    
    Cannot delete if the item is referenced in any borrowing requests.
    """
    result = equipment_service.delete_equipment_inventory(db, equipment_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment item not found"
        )
    
    return None


@router.post("/inventory/bulk-delete", status_code=status.HTTP_200_OK)
def bulk_delete_inventory(ids: List[int], db: Session = Depends(get_db)):
    """
    **Admin:** Bulk delete multiple equipment items from inventory.
    
    Skips items that are referenced in existing requests.
    Returns the number of items successfully deleted.
    """
    count = equipment_service.bulk_delete_equipment_inventory(db, ids)
    return {"message": f"{count} equipment item(s) deleted"}


# =========================================================
# EQUIPMENT REQUEST MANAGEMENT
# =========================================================

@router.get("/requests", response_model=List[EquipmentRequestAdminOut])
def get_equipment_requests(db: Session = Depends(get_db)):
    """
    **Admin:** Retrieve all equipment borrowing requests.
    
    Returns comprehensive request information including:
    - Transaction number
    - Resident information
    - Borrowing details (dates, items, quantities)
    - Status and payment information
    """
    return equipment_service.get_all_equipment_requests(db)


@router.get("/requests/{request_id}", response_model=EquipmentRequestAdminDetail)
def get_equipment_request_detail(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Retrieve detailed information for a specific equipment request.
    
    Includes all request details plus calculated fields like borrowing period.
    """
    result = equipment_service.get_equipment_request_by_id(db, request_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return result


# =========================================================
# REQUEST STATUS MANAGEMENT
# =========================================================

@router.post("/requests/{request_id}/approve", status_code=status.HTTP_200_OK)
def approve_request(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Approve an equipment borrowing request.
    
    - Changes status from Pending → Approved
    - Decreases available inventory for the borrowing period
    """
    success = equipment_service.approve_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request approved successfully"}


@router.post("/requests/{request_id}/reject", status_code=status.HTTP_200_OK)
def reject_request(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Reject an equipment borrowing request.
    
    Changes status to Rejected.
    """
    success = equipment_service.reject_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request rejected successfully"}


@router.post("/requests/{request_id}/picked-up", status_code=status.HTTP_200_OK)
def mark_picked_up(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Mark an approved request as picked up.
    
    Changes status from Approved → Picked-Up.
    """
    success = equipment_service.mark_as_picked_up(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request marked as picked up"}


@router.post("/requests/{request_id}/returned", status_code=status.HTTP_200_OK)
def mark_returned(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Mark equipment as returned.
    
    - Changes status from Picked-Up → Returned
    - Increases available inventory
    - Records return timestamp
    """
    success = equipment_service.mark_as_returned(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Equipment marked as returned"}


@router.post("/requests/{request_id}/mark-paid", status_code=status.HTTP_200_OK)
def mark_paid(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Mark a request's payment as paid.
    """
    success = equipment_service.mark_request_paid(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request marked as paid"}


@router.post("/requests/{request_id}/mark-unpaid", status_code=status.HTTP_200_OK)
def mark_unpaid(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Mark a request's payment as unpaid.
    """
    success = equipment_service.mark_request_unpaid(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request marked as unpaid"}


@router.post("/requests/{request_id}/toggle-refund", status_code=status.HTTP_200_OK)
def toggle_refund(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Toggle the refund status of a request.
    """
    success = equipment_service.toggle_refund_status(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Refund status toggled"}


@router.post("/requests/{request_id}/undo", status_code=status.HTTP_200_OK)
def undo_request(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Undo a request status change.
    
    Status transitions:
    - Approved → Pending (restores inventory)
    - Picked-Up → Approved
    - Returned → Picked-Up (decreases inventory)
    - Rejected → Pending
    """
    success = equipment_service.undo_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return {"message": "Request status reverted"}


@router.post("/requests/bulk-undo", status_code=status.HTTP_200_OK)
def bulk_undo(ids: List[int], db: Session = Depends(get_db)):
    """
    **Admin:** Bulk undo operation for multiple requests.
    
    Only processes requests that are in undoable states.
    Returns the number of requests successfully undone.
    """
    count = equipment_service.bulk_undo_equipment_requests(db, ids)
    return {"message": f"{count} request(s) reverted"}


# =========================================================
# REQUEST DELETION
# =========================================================

@router.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Delete an equipment request.
    
    Automatically restores inventory if the request was approved or picked up.
    """
    success = equipment_service.delete_equipment_request(db, request_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment request not found"
        )
    
    return None


@router.post("/requests/bulk-delete", status_code=status.HTTP_200_OK)
def bulk_delete(ids: List[int], db: Session = Depends(get_db)):
    """
    **Admin:** Bulk delete multiple equipment requests.
    
    Automatically restores inventory for approved/picked-up requests.
    Returns the number of requests successfully deleted.
    """
    count = equipment_service.bulk_delete_equipment_requests(db, ids)
    return {"message": f"{count} request(s) deleted"}


# =========================================================
# REQUEST NOTES
# =========================================================

@router.get("/requests/{request_id}/notes", response_model=str)
def get_notes(request_id: int, db: Session = Depends(get_db)):
    """
    **Admin:** Retrieve notes for a specific request.
    """
    return equipment_service.get_request_notes(db, request_id)


@router.put("/requests/{request_id}/notes", response_model=str)
def update_notes(request_id: int, notes: str, db: Session = Depends(get_db)):
    """
    **Admin:** Update notes for a specific request.
    """
    return equipment_service.update_request_notes(db, request_id, notes)