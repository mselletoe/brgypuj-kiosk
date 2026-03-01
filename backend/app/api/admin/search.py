from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, cast, String
from app.api.deps import get_db
from app.models.resident import Resident
from app.models.document import DocumentRequest
from app.models.equipment import EquipmentInventory, EquipmentRequest
from app.models.blotter import BlotterRecord

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("")
def global_search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    term = f"%{q.lower()}%"
    results = {}

    # ── Residents ─────────────────────────────────────────────────────────
    residents = (
        db.query(Resident)
        .filter(
            or_(
                Resident.first_name.ilike(term),
                Resident.last_name.ilike(term),
                Resident.middle_name.ilike(term),
                Resident.phone_number.ilike(term),
                cast(Resident.id, String).ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["members"] = [
        {
            "id": r.id,
            "label": f"{r.first_name} {r.last_name}",
            "subtitle": f"Resident · ID #{r.id}",
            "route": "/residents-management",
            "type": "member",
        }
        for r in residents
    ]

    # ── Document Requests ──────────────────────────────────────────────────
    doc_requests = (
        db.query(DocumentRequest)
        .options(
            joinedload(DocumentRequest.resident),
            joinedload(DocumentRequest.doctype)
        )
        .filter(
            or_(
                DocumentRequest.transaction_no.ilike(term),
                DocumentRequest.status.ilike(term),
                DocumentRequest.payment_status.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["documents"] = [
        {
            "id": d.id,
            "label": (
                d.doctype.doctype_name if d.doctype else "I.D Application"
            ) + (
                f" – {d.resident.first_name} {d.resident.last_name}"
                if d.resident else ""
            ),
            "subtitle": f"{d.transaction_no} · {d.status}",
            "route": f"/document-requests/{d.status}",
            "type": "document",
        }
        for d in doc_requests
    ]

    # ── Equipment Inventory ────────────────────────────────────────────────
    equipment = (
        db.query(EquipmentInventory)
        .filter(EquipmentInventory.name.ilike(term))
        .limit(5)
        .all()
    )
    results["equipment"] = [
        {
            "id": e.id,
            "label": e.name,
            "subtitle": f"Equipment · {e.available_quantity}/{e.total_quantity} available",
            "route": "/equipment-inventory",
            "type": "equipment",
        }
        for e in equipment
    ]

    # ── Equipment Requests ─────────────────────────────────────────────────
    equip_requests = (
        db.query(EquipmentRequest)
        .options(joinedload(EquipmentRequest.resident))
        .filter(
            or_(
                EquipmentRequest.transaction_no.ilike(term),
                EquipmentRequest.status.ilike(term),
                EquipmentRequest.purpose.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["equipment_requests"] = [
        {
            "id": er.id,
            "label": (
                f"Equipment Request – {er.resident.first_name} {er.resident.last_name}"
                if er.resident else f"Request #{er.id}"
            ),
            "subtitle": f"{er.transaction_no} · {er.status}",
            "route": f"/equipment-requests/{er.status}",
            "type": "equipment_request",
        }
        for er in equip_requests
    ]

    # ── Blotter Records ────────────────────────────────────────────────────
    blotter = (
        db.query(BlotterRecord)
        .filter(
            or_(
                BlotterRecord.blotter_no.ilike(term),
                BlotterRecord.complainant_name.ilike(term),
                BlotterRecord.respondent_name.ilike(term),
                BlotterRecord.incident_type.ilike(term),
            )
        )
        .limit(5)
        .all()
    )
    results["blotter"] = [
        {
            "id": b.id,
            "label": f"{b.blotter_no} – {b.incident_type or 'Blotter Record'}",
            "subtitle": f"vs. {b.respondent_name or 'Unknown'} · {str(b.incident_date) if b.incident_date else 'No date'}",
            "route": "/blotter-kp-logs",
            "type": "blotter",
        }
        for b in blotter
    ]

    return {k: v for k, v in results.items() if v}