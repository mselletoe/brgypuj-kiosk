from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    AddressUpdate,
    ResidentRFIDUpdate,
    ResidentListItem,
    ResidentDetailResponse,
    ResidentDropdownItem,
    PurokResponse
)
from app.services.resident_service import (
    get_all_residents_list,
    get_residents_dropdown,
    get_resident_detail,
    create_resident,
    update_resident,
    update_resident_address,
    update_resident_rfid,
    delete_resident,
    get_all_puroks
)
from app.api.deps import get_db

router = APIRouter(prefix="/residents")


@router.get("/", response_model=List[ResidentListItem])
def list_residents(db: Session = Depends(get_db)):
    return get_all_residents_list(db)


@router.get("/dropdown", response_model=List[ResidentDropdownItem])
def list_residents_dropdown(db: Session = Depends(get_db)):
    return get_residents_dropdown(db)


@router.get("/{resident_id}", response_model=ResidentDetailResponse)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    resident = get_resident_detail(db, resident_id)
    
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resident with ID {resident_id} not found"
        )
    
    return resident


@router.post("/", response_model=ResidentDetailResponse, status_code=status.HTTP_201_CREATED)
def create_new_resident(resident_data: ResidentCreate, db: Session = Depends(get_db)):
    new_resident = create_resident(db, resident_data)
    
    return get_resident_detail(db, new_resident.id)


@router.patch("/{resident_id}", response_model=ResidentDetailResponse)
def update_resident_info(
    resident_id: int,
    resident_data: ResidentUpdate,
    db: Session = Depends(get_db)
):
    updated_resident = update_resident(db, resident_id, resident_data)
    
    return get_resident_detail(db, updated_resident.id)


@router.patch("/{resident_id}/address", response_model=ResidentDetailResponse)
def update_resident_address_info(
    resident_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db)
):
    update_resident_address(db, resident_id, address_data)
    
    return get_resident_detail(db, resident_id)


@router.patch("/{resident_id}/rfid", response_model=ResidentDetailResponse)
def update_resident_rfid_info(
    resident_id: int,
    rfid_data: ResidentRFIDUpdate,
    db: Session = Depends(get_db)
):
    update_resident_rfid(db, resident_id, rfid_data)
    
    return get_resident_detail(db, resident_id)


@router.delete("/{resident_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resident_record(resident_id: int, db: Session = Depends(get_db)):
    delete_resident(db, resident_id)
    return None


@router.get("/utils/puroks", response_model=List[PurokResponse])
def list_puroks(db: Session = Depends(get_db)):
    return get_all_puroks(db)