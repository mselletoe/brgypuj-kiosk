from sqlalchemy.orm import Session, joinedload
from app.models.transaction import TransactionHistory


DOCUMENT_STATUS_MAP = {
    "Released": "Completed",
    "Rejected": "Rejected",
}

EQUIPMENT_STATUS_MAP = {
    "Returned": "Completed",
    "Rejected": "Rejected",
}


def _get_resident_rfid(resident) -> str | None:
    if not resident or not hasattr(resident, "rfids"):
        return None
    return next((r.rfid_uid for r in resident.rfids if r.is_active), None)


def _entry_exists(db: Session, transaction_no: str) -> bool:
    return (
        db.query(TransactionHistory)
        .filter(TransactionHistory.transaction_no == transaction_no)
        .first()
        is not None
    )


def _build_equipment_title(request) -> str:
    try:
        parts = [f"{item.quantity}x {item.item_name}" for item in request.items]
        return ", ".join(parts) if parts else "Equipment Request"
    except Exception:
        return "Equipment Request"


def record_document_transaction(db: Session, request) -> None:
    history_status = DOCUMENT_STATUS_MAP.get(request.status)
    if not history_status:
        return

    if _entry_exists(db, request.transaction_no):
        return 
    rfid_uid = _get_resident_rfid(request.resident) if request.resident else None

    if request.doctype_id is None:
        transaction_name = "I.D Application"
    else:
        try:
            transaction_name = request.doctype.doctype_name
        except Exception:
            transaction_name = "Document Request"

    entry = TransactionHistory(
        transaction_type="document",  
        transaction_name=transaction_name,
        transaction_no=request.transaction_no,
        resident_id=request.resident_id,
        rfid_uid=rfid_uid,
        status=history_status,
    )
    db.add(entry)
    db.commit()


def record_equipment_transaction(db: Session, request) -> None:
    history_status = EQUIPMENT_STATUS_MAP.get(request.status)
    if not history_status:
        return

    if _entry_exists(db, request.transaction_no):
        return

    rfid_uid = _get_resident_rfid(request.resident) if request.resident else None

    transaction_name = _build_equipment_title(request)

    entry = TransactionHistory(
        transaction_type="equipment", 
        transaction_name=transaction_name, 
        transaction_no=request.transaction_no,
        resident_id=request.resident_id,
        rfid_uid=rfid_uid,
        status=history_status,
    )
    db.add(entry)
    db.commit()


def get_transaction_history(db: Session, resident_id: int) -> list[dict]:
    entries = (
        db.query(TransactionHistory)
        .filter(TransactionHistory.resident_id == resident_id)
        .order_by(TransactionHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": entry.id,
            "transaction_type": entry.transaction_type, 
            "transaction_name": entry.transaction_name, 
            "transaction_no": entry.transaction_no,
            "rfid_uid": entry.rfid_uid,
            "status": entry.status,
            "created_at": entry.created_at,
        }
        for entry in entries
    ]