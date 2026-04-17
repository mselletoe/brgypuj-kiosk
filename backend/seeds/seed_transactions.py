"""
seeds/seed_transactions.py

Seeds TransactionHistory for completed/rejected document and equipment requests.
Run AFTER seed_documents and seed_equipment so real request data exists.
"""

import random
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, progression
from app.models.transaction import TransactionHistory
from app.models.document import DocumentRequest
from app.models.equipment import EquipmentRequest
from app.models.resident import Resident


def seed_transactions(db: Session):
    print("\n[transactions] Seeding transaction history …")

    existing = db.query(TransactionHistory).count()
    if existing >= 10:
        print(f"  ↳ Skipped — {existing} transaction history entries already exist.")
        return

    count = 0

    # ── From document requests ────────────────────────────────────
    doc_requests = (
        db.query(DocumentRequest)
        .filter(DocumentRequest.status.in_(["Released", "Rejected"]))
        .all()
    )
    for req in doc_requests:
        doc_name = req.doctype.doctype_name if req.doctype else "Document"
        status   = "Completed" if req.status == "Released" else "Rejected"

        th = TransactionHistory(
            transaction_type = "document",
            transaction_name = doc_name,
            transaction_no   = req.transaction_no,
            resident_id      = req.resident_id,
            rfid_uid         = None,
            status           = status,
            created_at       = progression(req.requested_at, 1, 72),
        )
        db.add(th)
        count += 1

    # ── From equipment requests ───────────────────────────────────
    equip_requests = (
        db.query(EquipmentRequest)
        .filter(EquipmentRequest.status.in_(["Returned", "Rejected"]))
        .all()
    )
    for req in equip_requests:
        item_names = ", ".join(i.inventory_item.name for i in req.items if i.inventory_item)
        status     = "Completed" if req.status == "Returned" else "Rejected"

        th = TransactionHistory(
            transaction_type = "equipment",
            transaction_name = item_names[:100] if item_names else "Equipment",
            transaction_no   = req.transaction_no,
            resident_id      = req.resident_id,
            rfid_uid         = None,
            status           = status,
            created_at       = req.returned_at or progression(req.requested_at, 24, 96),
        )
        db.add(th)
        count += 1

    # ── Standalone historical entries (for volume) ────────────────
    residents = db.query(Resident).all()
    if residents:
        for _ in range(15):
            resident = random.choice(residents)
            t_type   = random.choice(["document", "equipment"])
            prefix   = "DR" if t_type == "document" else "ER"
            no       = f"{prefix}-{random.randint(9000, 9999)}"

            th = TransactionHistory(
                transaction_type = t_type,
                transaction_name = random.choice([
                    "Barangay Clearance", "Certificate of Indigency",
                    "Certificate of Residency", "Plastic Chairs (set of 50)",
                    "Sound System (PA Set)", "Barangay ID",
                ]),
                transaction_no   = no,
                resident_id      = resident.id,
                rfid_uid         = None,
                status           = random.choices(["Completed", "Rejected"], weights=[85, 15])[0],
                created_at       = rand_dt(),
            )
            db.add(th)
            count += 1

    db.commit()
    print(f"  ↳ Inserted {count} transaction history entries.")