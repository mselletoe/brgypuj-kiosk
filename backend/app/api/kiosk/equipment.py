"""
Equipment Borrowing API - Kiosk Endpoints
---------------------------
Public-facing endpoints for residents to browse equipment inventory
and submit borrowing requests through the kiosk interface.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.equipment import (
    EquipmentInventoryOut,
    EquipmentRequestCreate,
    EquipmentRequestKioskResponse,
    EquipmentRequestKioskOut,
    EquipmentAutofillData,
)
from app.services import equipment_service
from app.core.sse_manager import sse_manager

router = APIRouter(prefix="/equipment")


@router.get("/inventory", response_model=List[EquipmentInventoryOut])
def get_available_equipment(db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve all available equipment items for display on the kiosk.
    """
    return equipment_service.get_available_equipment(db)


@router.get("/autofill/{resident_id}", response_model=EquipmentAutofillData)
def get_autofill_data(resident_id: int, db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve resident data for autofilling the borrowing form.
    """
    return equipment_service.get_equipment_autofill_data(db, resident_id)


@router.post("/requests", response_model=EquipmentRequestKioskResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment_request(
    payload: EquipmentRequestCreate,
    db: Session = Depends(get_db)
):
    """
    **Kiosk:** Submit a new equipment borrowing request.
    """
    result = equipment_service.create_equipment_request(db, payload)
    await sse_manager.broadcast("equipment_request_created", {
        "id": result.id,
        "transaction_no": result.transaction_no,
        "status": "pending"
    })
    return result


@router.get("/requests/history/{resident_id}", response_model=List[EquipmentRequestKioskOut])
def get_request_history(resident_id: int, db: Session = Depends(get_db)):
    """
    **Kiosk:** Retrieve equipment borrowing history for a specific resident.
    """
    return equipment_service.get_kiosk_request_history(db, resident_id)