"""
Transaction History Service Layer
---------------------------
Handles recording and retrieval of unified transaction history.
Records are written automatically when document/equipment requests reach
a terminal state: "Released" → Completed, "Returned" → Completed,
"Rejected" → Rejected.

RFID uid is snapshotted at write time so history is accurate even if
a resident later replaces their RFID card.

RFID activities will plug in here once that module is ready.
"""

from sqlalchemy.orm import Session, joinedload
from app.models.transaction import TransactionHistory


# -------------------------------------------------
# Terminal Status Mapping
# -------------------------------------------------

DOCUMENT_STATUS_MAP = {
    "Released": "Completed",
    "Rejected": "Rejected",
}

EQUIPMENT_STATUS_MAP = {
    "Returned": "Completed",
    "Rejected": "Rejected",
}

# RFID_STATUS_MAP will be added here once the RFID module is built.
# RFID_STATUS_MAP = {
#     "Issued": "Completed",
#     "Rejected": "Rejected",
# }


# -------------------------------------------------
# Internal Helpers
# -------------------------------------------------

def _get_resident_rfid(resident) -> str | None:
    """Extracts the active RFID UID from a resident relationship, if available."""
    if not resident or not hasattr(resident, "rfids"):
        return None
    return next((r.rfid_uid for r in resident.rfids if r.is_active), None)


def _entry_exists(db: Session, transaction_no: str) -> bool:
    """Prevents duplicate history entries for the same transaction_no."""
    return (
        db.query(TransactionHistory)
        .filter(TransactionHistory.transaction_no == transaction_no)
        .first()
        is not None
    )


def _build_equipment_title(request) -> str:
    """
    Builds a human-readable summary of the borrowed items.
    e.g. "2x Tent, 30x Monobloc Chair"
    Falls back to "Equipment Request" if items are not loaded.
    """
    try:
        parts = [f"{item.quantity}x {item.item_name}" for item in request.items]
        return ", ".join(parts) if parts else "Equipment Request"
    except Exception:
        return "Equipment Request"


# -------------------------------------------------
# Writers (called from document_service / equipment_service)
# -------------------------------------------------

def record_document_transaction(db: Session, request) -> None:
    """
    Records a document request in transaction history when it reaches
    a terminal state (Released → Completed, Rejected → Rejected).

    Call this inside document_service AFTER db.commit() on a status change.
    The RFID is snapshotted here so future card replacements don't affect
    historical records.

    Args:
        db: Active database session.
        request: DocumentRequest ORM instance (with .resident and .doctype eagerly loaded).
    """
    history_status = DOCUMENT_STATUS_MAP.get(request.status)
    if not history_status:
        return  # Not a terminal state — nothing to record

    if _entry_exists(db, request.transaction_no):
        return  # Guard against duplicates (e.g. re-release after undo)

    # Snapshot the RFID at this moment in time
    rfid_uid = _get_resident_rfid(request.resident) if request.resident else None

    # ID Applications have doctype_id = NULL — use the fixed label directly.
    # Otherwise use the specific document type name (e.g. "Barangay Clearance").
    # Falls back to the generic label if the relationship isn't loaded.
    if request.doctype_id is None:
        transaction_name = "I.D Application"
    else:
        try:
            transaction_name = request.doctype.doctype_name
        except Exception:
            transaction_name = "Document Request"

    entry = TransactionHistory(
        transaction_type="document",          # ← clean type enum for the frontend
        transaction_name=transaction_name,    # ← e.g. "Barangay Clearance"
        transaction_no=request.transaction_no,
        resident_id=request.resident_id,
        rfid_uid=rfid_uid,
        status=history_status,
    )
    db.add(entry)
    db.commit()


def record_equipment_transaction(db: Session, request) -> None:
    """
    Records an equipment request in transaction history when it reaches
    a terminal state (Returned → Completed, Rejected → Rejected).

    Call this inside equipment_service AFTER db.commit() on a status change.
    The RFID is snapshotted here so future card replacements don't affect
    historical records.

    Args:
        db: Active database session.
        request: EquipmentRequest ORM instance (with .resident and .items eagerly loaded).
    """
    history_status = EQUIPMENT_STATUS_MAP.get(request.status)
    if not history_status:
        return

    if _entry_exists(db, request.transaction_no):
        return

    # Snapshot the RFID at this moment in time
    rfid_uid = _get_resident_rfid(request.resident) if request.resident else None

    # Build a readable item summary as the title (e.g. "2x Tent, 30x Monobloc Chair")
    transaction_name = _build_equipment_title(request)

    entry = TransactionHistory(
        transaction_type="equipment",         # ← clean type enum for the frontend
        transaction_name=transaction_name,    # ← e.g. "2x Tent, 30x Monobloc Chair"
        transaction_no=request.transaction_no,
        resident_id=request.resident_id,
        rfid_uid=rfid_uid,
        status=history_status,
    )
    db.add(entry)
    db.commit()


# Placeholder — wire this up when the RFID module is ready.
# def record_rfid_transaction(db: Session, activity) -> None:
#     history_status = RFID_STATUS_MAP.get(activity.status)
#     if not history_status or _entry_exists(db, activity.transaction_no):
#         return
#     rfid_uid = activity.rfid_uid  # Already known from the activity itself
#     entry = TransactionHistory(
#         transaction_type="rfid",
#         transaction_name="Gate Entry Log",
#         transaction_no=activity.transaction_no,
#         resident_id=activity.resident_id,
#         rfid_uid=rfid_uid,
#         status=history_status,
#     )
#     db.add(entry)
#     db.commit()


# -------------------------------------------------
# Readers
# -------------------------------------------------

def get_transaction_history(db: Session, resident_id: int) -> list[dict]:
    """
    Kiosk & Admin: Returns a resident's unified transaction history.
    Uses the snapshotted rfid_uid stored on the record — not the current
    active RFID — so the history is always accurate regardless of card changes.
    Ordered by most recent first.
    """
    entries = (
        db.query(TransactionHistory)
        .filter(TransactionHistory.resident_id == resident_id)
        .order_by(TransactionHistory.created_at.desc())
        .all()
    )

    return [
        {
            "id": entry.id,
            "transaction_type": entry.transaction_type,   # "document" | "equipment" | "rfid"
            "transaction_name": entry.transaction_name,   # e.g. "Barangay Clearance"
            "transaction_no": entry.transaction_no,
            "rfid_uid": entry.rfid_uid,
            "status": entry.status,
            "created_at": entry.created_at,
        }
        for entry in entries
    ]