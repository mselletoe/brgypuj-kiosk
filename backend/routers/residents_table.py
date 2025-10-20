from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from models import Resident, Address, Purok, RfidUID

router = APIRouter(prefix="/residents", tags=["Residents"])

@router.get("/puroks")
def get_puroks(db: Session = Depends(get_db)):
    puroks = db.query(Purok.id, Purok.purok_name).all()
    return [{"id": p.id, "purok_name": p.purok_name} for p in puroks]

@router.get("/")
def get_residents(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    query: str = "",
    filter: str = "all",
    purok_ids: str = ""
):
    q = db.query(
        Resident.id,
        Resident.first_name,
        Resident.last_name,
        Resident.middle_name,
        Address.unit_blk_street,
        Purok.purok_name.label("purok"),
        Resident.phone_number,
        RfidUID.rfid_uid
    ).join(Address, Address.resident_id == Resident.id, isouter=True
    ).join(Purok, Purok.id == Address.purok_id, isouter=True
    ).join(RfidUID, RfidUID.resident_id == Resident.id, isouter=True)

    # Apply search filters
    if query:
        if filter == "first_name":
            q = q.filter(Resident.first_name.ilike(f"%{query}%"))
        elif filter == "last_name":
            q = q.filter(Resident.last_name.ilike(f"%{query}%"))
        elif filter == "middle_name":
            q = q.filter(Resident.middle_name.ilike(f"%{query}%"))
        elif filter == "phone_number":
            q = q.filter(Resident.phone_number.ilike(f"%{query}%"))
        else:
            q = q.filter(
                or_(
                    Resident.first_name.ilike(f"%{query}%"),
                    Resident.last_name.ilike(f"%{query}%"),
                    Resident.middle_name.ilike(f"%{query}%"),
                    Resident.phone_number.ilike(f"%{query}%")
                )
            )

    if purok_ids:
        purok_list = [int(pid) for pid in purok_ids.split(",") if pid.isdigit()]
        if purok_list:
            q = q.filter(Purok.id.in_(purok_list))

    total = q.count()
    residents = q.offset((page - 1) * limit).limit(limit).all()

    # ✅ Convert Row objects into dictionaries
    residents_list = [
        {
            "id": r.id,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "middle_name": r.middle_name,
            "unit_blk_street": r.unit_blk_street,
            "purok": r.purok,
            "phone_number": r.phone_number,
            "rfid_uid": r.rfid_uid
        }
        for r in residents
    ]

    return {"total": total, "residents": residents_list}
