from datetime import date
import base64
import secrets
from passlib.context import CryptContext
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.resident import Resident, Address, ResidentRFID, Purok
from app.models.barangayid import BarangayID
from app.schemas.resident import (
    ResidentCreate,
    ResidentUpdate,
    AddressUpdate,
    ResidentRFIDUpdate
)
from typing import List, Optional, Dict

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Helper Functions
# ============================================================================

def calculate_age(birthdate: date) -> int:
    today = date.today()
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age


def calculate_residency_duration(residency_start_date: date) -> dict:
    today = date.today()
    years = today.year - residency_start_date.year
    if (today.month, today.day) < (residency_start_date.month, residency_start_date.day):
        years -= 1
    years = max(0, years)
    start_after_years = residency_start_date.replace(year=residency_start_date.year + years)
    months = (today.year - start_after_years.year) * 12 + (today.month - start_after_years.month)
    if today.day < start_after_years.day:
        months = max(0, months - 1)
    if years == 0:
        label = f"{months} month{'s' if months != 1 else ''}" if months > 0 else "Less than a month"
    elif months == 0:
        label = f"{years} year{'s' if years != 1 else ''}"
    else:
        label = f"{years} year{'s' if years != 1 else ''}, {months} month{'s' if months != 1 else ''}"
    return {"years": years, "months": months, "label": label}


def calculate_years_of_residency(residency_start_date: date) -> int:
    return calculate_residency_duration(residency_start_date)["years"]


def build_full_name(first_name: str, middle_name: Optional[str],
                    last_name: str, suffix: Optional[str]) -> str:
    name_parts = [first_name]
    if middle_name:
        name_parts.append(middle_name)
    name_parts.append(last_name)
    if suffix:
        name_parts.append(suffix)
    return " ".join(name_parts)


def build_full_address(address: Address) -> str:
    address_parts = [
        address.house_no_street,
        address.purok.purok_name if address.purok else None,
        address.barangay,
        address.municipality,
        address.province,
    ]
    return ", ".join(filter(None, address_parts))


def _get_brgy_id_fields(resident: Resident) -> dict:
    """
    Returns brgy_id_number and brgy_id_expiration_date from the resident's
    active BarangayID row. Assumes barangay_ids is already eagerly loaded.
    """
    active_brgy_id = next(
        (b for b in resident.barangay_ids if b.is_active),
        None
    )
    return {
        "brgy_id_number": active_brgy_id.brgy_id_number if active_brgy_id else None,
        "brgy_id_expiration_date": (
            str(active_brgy_id.expiration_date)
            if active_brgy_id and active_brgy_id.expiration_date
            else None
        ),
    }


# ============================================================================
# CRUD Operations - READ
# ============================================================================

def get_all_residents_list(db: Session) -> List[Dict]:
    residents = (
        db.query(Resident)
        .options(
            joinedload(Resident.addresses).joinedload(Address.purok),
            joinedload(Resident.rfids)
        )
        .order_by(Resident.last_name, Resident.first_name)
        .all()
    )

    result = []
    for resident in residents:
        current_address = next((addr for addr in resident.addresses if addr.is_current), None)
        active_rfid = next((rfid for rfid in resident.rfids if rfid.is_active), None)
        any_rfid = active_rfid or (
            max(resident.rfids, key=lambda r: r.created_at) if resident.rfids else None
        )
        if active_rfid:
            rfid_display = active_rfid.rfid_uid
        elif any_rfid:
            rfid_display = "Inactive"
        else:
            rfid_display = None

        result.append({
            "id": resident.id,
            "full_name": build_full_name(
                resident.first_name, resident.middle_name,
                resident.last_name, resident.suffix
            ),
            "gender": resident.gender,
            "phone_number": resident.phone_number,
            "rfid_no": rfid_display,
            "purok_id": current_address.purok_id if current_address else None,
            "current_address": build_full_address(current_address) if current_address else None
        })

    return result


def get_residents_dropdown(db: Session) -> List[Dict]:
    residents = (
        db.query(Resident)
        .order_by(Resident.last_name, Resident.first_name)
        .all()
    )
    return [
        {
            "id": resident.id,
            "full_name": build_full_name(
                resident.first_name, resident.middle_name,
                resident.last_name, resident.suffix
            )
        }
        for resident in residents
    ]


def get_resident_by_id(db: Session, resident_id: int) -> Optional[Resident]:
    return (
        db.query(Resident)
        .options(
            joinedload(Resident.addresses).joinedload(Address.purok),
            joinedload(Resident.rfids),
            joinedload(Resident.barangay_ids),   # ← needed for brgy_id_number + expiry
        )
        .filter(Resident.id == resident_id)
        .first()
    )


def get_resident_detail(db: Session, resident_id: int) -> Optional[Dict]:
    resident = get_resident_by_id(db, resident_id)
    if not resident:
        return None

    current_address = next((addr for addr in resident.addresses if addr.is_current), None)

    rfid_card = None
    if resident.rfids:
        active = next((r for r in resident.rfids if r.is_active), None)
        rfid_card = active or max(resident.rfids, key=lambda r: r.created_at)

    age = calculate_age(resident.birthdate)
    residency = calculate_residency_duration(resident.residency_start_date)

    return {
        # Basic Info
        "id": resident.id,
        "first_name": resident.first_name,
        "middle_name": resident.middle_name,
        "last_name": resident.last_name,
        "suffix": resident.suffix,
        "full_name": build_full_name(
            resident.first_name, resident.middle_name,
            resident.last_name, resident.suffix
        ),
        "gender": resident.gender,
        "birthdate": resident.birthdate.strftime("%m/%d/%Y"),
        "age": age,
        "photo": base64.b64encode(resident.photo).decode("utf-8") if resident.photo else None,

        # Contact Info
        "email": resident.email,
        "phone_number": resident.phone_number,

        # Residency Info
        "residency_start_date": resident.residency_start_date.strftime("%m/%d/%Y"),
        "years_of_residency": residency["years"],
        "residency_months": residency["months"],
        "residency_label": residency["label"],

        # Address Info
        "current_address": {
            "id": current_address.id,
            "house_no_street": current_address.house_no_street,
            "purok_id": current_address.purok_id,
            "purok": {
                "id": current_address.purok.id,
                "purok_name": current_address.purok.purok_name
            } if current_address.purok else None,
            "barangay": current_address.barangay,
            "municipality": current_address.municipality,
            "province": current_address.province,
            "region": current_address.region,
            "is_current": current_address.is_current
        } if current_address else None,

        # RFID Info
        "active_rfid": {
            "id": rfid_card.id,
            "rfid_uid": rfid_card.rfid_uid,
            "is_active": rfid_card.is_active,
            "created_at": rfid_card.created_at.isoformat(),
            "expiration_date": rfid_card.expiration_date,   # included for completeness
        } if rfid_card else None,

        # Barangay ID Info — active card only              ← NEW
        **_get_brgy_id_fields(resident),

        # Timestamps
        "registered_at": resident.registered_at.isoformat()
    }


def get_resident_autofill_data(db: Session, resident_id: int) -> Optional[dict]:
    resident = (
        db.query(Resident)
        .options(
            joinedload(Resident.addresses).joinedload(Address.purok),
            joinedload(Resident.rfids)
        )
        .filter(Resident.id == resident_id)
        .first()
    )
    if not resident:
        return None

    current_address = next((addr for addr in resident.addresses if addr.is_current), None)
    active_rfid = next((rfid for rfid in resident.rfids if rfid.is_active), None)

    name_parts = [resident.first_name]
    if resident.middle_name:
        name_parts.append(resident.middle_name)
    name_parts.append(resident.last_name)
    if resident.suffix:
        name_parts.append(resident.suffix)
    full_name = " ".join(name_parts)

    full_address = None
    if current_address:
        address_parts = [
            current_address.house_no_street,
            current_address.purok.purok_name if current_address.purok else None,
            current_address.barangay,
            current_address.municipality,
            current_address.province,
        ]
        full_address = ", ".join(filter(None, address_parts))

    age = calculate_age(resident.birthdate)
    years_residency = calculate_years_of_residency(resident.residency_start_date)

    return {
        "full_name": full_name,
        "first_name": resident.first_name,
        "middle_name": resident.middle_name,
        "last_name": resident.last_name,
        "suffix": resident.suffix,
        "gender": resident.gender,
        "birthdate": resident.birthdate.strftime("%m/%d/%Y"),
        "age": age,
        "email": resident.email,
        "phone_number": resident.phone_number,
        "unit_blk_street": current_address.house_no_street if current_address else None,
        "purok_name": current_address.purok.purok_name if current_address and current_address.purok else None,
        "barangay": current_address.barangay if current_address else None,
        "municipality": current_address.municipality if current_address else None,
        "province": current_address.province if current_address else None,
        "region": current_address.region if current_address else None,
        "full_address": full_address,
        "years_residency": years_residency,
        "residency_start_date": resident.residency_start_date.strftime("%m/%d/%Y"),
        "rfid_uid": active_rfid.rfid_uid if active_rfid else None,
    }


# ============================================================================
# CRUD Operations - CREATE
# ============================================================================

def create_resident(db: Session, resident_data: ResidentCreate) -> Resident:
    residency_start_date = resident_data.residency_start_date or date.today()

    purok = db.query(Purok).filter(Purok.id == resident_data.address.purok_id).first()
    if not purok:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purok with ID {resident_data.address.purok_id} not found"
        )

    if resident_data.rfid:
        existing_rfid = db.query(ResidentRFID).filter(
            ResidentRFID.rfid_uid == resident_data.rfid.rfid_uid
        ).first()
        if existing_rfid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"RFID UID '{resident_data.rfid.rfid_uid}' is already registered"
            )

    if resident_data.email:
        existing_email = db.query(Resident).filter(
            Resident.email == resident_data.email
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email '{resident_data.email}' is already registered"
            )

    try:
        # Generate a random 6-digit PIN and hash it; can be changed later via profile
        random_pin = str(secrets.randbelow(900000) + 100000)  # always 6 digits
        hashed_pin = pwd_context.hash(random_pin)

        new_resident = Resident(
            first_name=resident_data.first_name,
            middle_name=resident_data.middle_name,
            last_name=resident_data.last_name,
            suffix=resident_data.suffix,
            gender=resident_data.gender,
            birthdate=resident_data.birthdate,
            residency_start_date=residency_start_date,
            email=resident_data.email,
            phone_number=resident_data.phone_number,
            rfid_pin=hashed_pin
        )
        db.add(new_resident)
        db.flush()

        new_address = Address(
            resident_id=new_resident.id,
            house_no_street=resident_data.address.house_no_street,
            purok_id=resident_data.address.purok_id,
            barangay=resident_data.address.barangay,
            municipality=resident_data.address.municipality,
            province=resident_data.address.province,
            region=resident_data.address.region,
            is_current=True
        )
        db.add(new_address)

        if resident_data.rfid:
            new_rfid = ResidentRFID(
                resident_id=new_resident.id,
                rfid_uid=resident_data.rfid.rfid_uid,
                is_active=resident_data.rfid.is_active
            )
            db.add(new_rfid)

        db.commit()
        db.refresh(new_resident)
        return new_resident

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Database integrity error. Please check your input data."
        )


# ============================================================================
# CRUD Operations - UPDATE
# ============================================================================

def update_resident(db: Session, resident_id: int, resident_data: ResidentUpdate) -> Resident:
    resident = get_resident_by_id(db, resident_id)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Resident with ID {resident_id} not found")

    if resident_data.email and resident_data.email != resident.email:
        existing = db.query(Resident).filter(
            Resident.email == resident_data.email,
            Resident.id != resident_id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Email '{resident_data.email}' is already in use")

    update_data = resident_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(resident, field, value)

    db.commit()
    db.refresh(resident)
    return resident


def update_resident_address(db: Session, resident_id: int, address_data: AddressUpdate) -> Address:
    resident = get_resident_by_id(db, resident_id)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Resident with ID {resident_id} not found")

    current_address = next((addr for addr in resident.addresses if addr.is_current), None)
    if not current_address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No current address found for this resident")

    if address_data.purok_id:
        purok = db.query(Purok).filter(Purok.id == address_data.purok_id).first()
        if not purok:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Purok with ID {address_data.purok_id} not found")

    update_data = address_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_address, field, value)

    db.commit()
    db.refresh(current_address)
    return current_address


def update_resident_rfid(db: Session, resident_id: int, rfid_data: ResidentRFIDUpdate) -> ResidentRFID:
    resident = get_resident_by_id(db, resident_id)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Resident with ID {resident_id} not found")

    target_rfid = next((rfid for rfid in resident.rfids if rfid.is_active), None)
    if not target_rfid and resident.rfids:
        target_rfid = max(resident.rfids, key=lambda r: r.created_at)

    if not target_rfid:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No RFID card found for this resident")

    if rfid_data.rfid_uid and rfid_data.rfid_uid != target_rfid.rfid_uid:
        existing = db.query(ResidentRFID).filter(
            ResidentRFID.rfid_uid == rfid_data.rfid_uid,
            ResidentRFID.id != target_rfid.id
        ).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"RFID UID '{rfid_data.rfid_uid}' is already registered")

    update_data = rfid_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(target_rfid, field, value)

    db.commit()
    db.refresh(target_rfid)
    return target_rfid


# ============================================================================
# CRUD Operations - DELETE
# ============================================================================

def delete_resident(db: Session, resident_id: int) -> bool:
    resident = get_resident_by_id(db, resident_id)
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Resident with ID {resident_id} not found")
    try:
        db.delete(resident)
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete resident. They may have related records that prevent deletion."
        )


# ============================================================================
# Utility Functions
# ============================================================================

def get_all_puroks(db: Session) -> List[Purok]:
    return db.query(Purok).order_by(Purok.purok_name).all()