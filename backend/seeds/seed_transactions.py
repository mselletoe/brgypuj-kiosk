"""
seeds/seed_transactions.py

Seeds TransactionHistory for completed/rejected document and equipment requests.
Run AFTER seed_documents and seed_equipment so real request data exists.

Resident restriction:
    Standalone historical entries (seeded for volume) are restricted to the
    same 31 transaction-eligible residents used in seed_documents and
    seed_equipment — not drawn from the full resident pool.
"""

import random
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, progression
from app.models.transaction import TransactionHistory
from app.models.document import DocumentRequest
from app.models.equipment import EquipmentRequest
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Same 31 transaction-eligible residents as the other seeders.
# ─────────────────────────────────────────────────────────────

TRANSACTION_RESIDENTS = [
    ("Vibandor",   "Mylene"),
    ("Angcaya",    "Joana"),
    ("Delarmino",  "Chariel Althea"),
    ("Bataclan",   "Jenna Rose"),
    ("Angcaya",    "Ma. Monica Yinley"),
    ("Dela Rea",   "Justine Carl"),
    ("Jamon",      "Alliah Mae"),
    ("Plaganas",   "Maria Aleth"),
    ("Gutierrez",  "Gillian Lou"),
    ("Bayas",      "Allister Marvin"),
    ("Angcaya",    "Micah Angelie"),
    ("Cruz",       "Kenjie Ryle"),
    ("Sipat",      "Marife"),
    ("Ramos",      "Naomi Rose"),
    ("Ramos",      "Winona Kylie"),
    ("Barrera",    "Lourella"),
    ("Dela Rea",   "Kristal Joy"),
    ("Panganiban", "Arvin"),
    ("Dela Rea",   "Carissa Mae"),
    ("Dimayuga",   "Ghia Larize"),
    ("Sumagui",    "Emil"),
    ("Sumagui",    "Niel"),
    ("Sumagui",    "Emmanuel"),
    ("San Martin", "Bobby"),
    ("Fresco",     "Veronica Anne"),
    ("San Martin", "Franco"),
    ("Mora",       "Mary Joy"),
    ("Madera",     "Aubrey Rose"),
    ("Bayot",      "Rochelle Ann"),
    ("Villamor",   "Keith Beau Allen"),
    ("Ambion",     "Johanne Alecs"),
]

# ─────────────────────────────────────────────────────────────
# Earliest allowed request date per resident.
# Standalone transaction history entries use the resident's
# assigned date + 0–3 days offset + random business-hours time,
# mirroring the logic in seed_documents / seed_equipment.
# ─────────────────────────────────────────────────────────────

RESIDENT_REQUEST_DATES: dict[tuple, date] = {
    ("Vibandor",   "Mylene"):           date(2026, 3, 16),
    ("Angcaya",    "Joana"):            date(2026, 3, 16),
    ("Delarmino",  "Chariel Althea"):   date(2026, 3, 16),
    ("Bataclan",   "Jenna Rose"):       date(2026, 3, 16),
    ("Angcaya",    "Ma. Monica Yinley"):date(2026, 3, 17),
    ("Dela Rea",   "Justine Carl"):     date(2026, 3, 20),
    ("Jamon",      "Alliah Mae"):       date(2026, 3, 20),
    ("Plaganas",   "Maria Aleth"):      date(2026, 3, 21),
    ("Gutierrez",  "Gillian Lou"):      date(2026, 3, 21),
    ("Bayas",      "Allister Marvin"):  date(2026, 3, 23),
    ("Angcaya",    "Micah Angelie"):    date(2026, 3, 26),
    ("Cruz",       "Kenjie Ryle"):      date(2026, 3, 26),
    ("Sipat",      "Marife"):           date(2026, 3, 26),
    ("Ramos",      "Naomi Rose"):       date(2026, 3, 28),
    ("Ramos",      "Winona Kylie"):     date(2026, 3, 28),
    ("Barrera",    "Lourella"):         date(2026, 3, 28),
    ("Dela Rea",   "Kristal Joy"):      date(2026, 3, 30),
    ("Panganiban", "Arvin"):            date(2026, 4,  1),
    ("Dela Rea",   "Carissa Mae"):      date(2026, 4,  3),
    ("Dimayuga",   "Ghia Larize"):      date(2026, 4,  3),
    ("Sumagui",    "Emil"):             date(2026, 4,  4),
    ("Sumagui",    "Niel"):             date(2026, 4,  4),
    ("Sumagui",    "Emmanuel"):         date(2026, 4,  7),
    ("San Martin", "Bobby"):            date(2026, 4,  8),
    ("Fresco",     "Veronica Anne"):    date(2026, 4, 10),
    ("San Martin", "Franco"):           date(2026, 4, 10),
    ("Mora",       "Mary Joy"):         date(2026, 4, 10),
    ("Madera",     "Aubrey Rose"):      date(2026, 4, 13),
    ("Bayot",      "Rochelle Ann"):     date(2026, 4, 15),
    ("Villamor",   "Keith Beau Allen"): date(2026, 4, 18),
    ("Ambion",     "Johanne Alecs"):    date(2026, 4, 18),
}

from seeds.utils import DEPLOY_END  # noqa: E402  (already imported rand_dt above)


def _resident_request_dt(resident) -> datetime:
    """
    Return a datetime on or up to 3 days after the resident's assigned
    earliest request date, at a random business-hours time (08:00–16:59).
    Falls back to rand_dt() if the resident isn't in the map.
    """
    last_norm  = resident.last_name.strip().lower()
    first_norm = resident.first_name.strip().lower()

    base_date: date | None = None
    for (last, first_start), d in RESIDENT_REQUEST_DATES.items():
        if (
            last.strip().lower() == last_norm
            and first_norm.startswith(first_start.strip().lower())
        ):
            base_date = d
            break

    if base_date is None:
        return rand_dt()

    offset    = random.randint(0, 3)
    target_dt = datetime(base_date.year, base_date.month, base_date.day) + timedelta(days=offset)
    target_dt += timedelta(
        hours=random.randint(8, 16),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59),
    )

    if target_dt > DEPLOY_END:
        target_dt = DEPLOY_END - timedelta(minutes=random.randint(1, 60))

    return target_dt


def _get_transaction_residents(db: Session) -> list:
    all_residents = (
        db.query(Resident)
        .join(Resident.rfids)
        .filter(ResidentRFID.is_active == True)
        .all()
    )
    matched = []
    for last, first_start in TRANSACTION_RESIDENTS:
        last_norm  = last.strip().lower()
        first_norm = first_start.strip().lower()
        for r in all_residents:
            if (
                r.last_name.strip().lower() == last_norm
                and r.first_name.strip().lower().startswith(first_norm)
            ):
                matched.append(r)
                break
    return matched


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
    # Restricted to the 31 real transaction-eligible residents only.
    residents = _get_transaction_residents(db)
    if residents:
        for _ in range(15):
            resident = random.choice(residents)
            t_type   = random.choice(["document", "equipment"])
            prefix   = "DR" if t_type == "document" else "ER"
            no       = f"{prefix}-{random.randint(9000, 9999)}"

            th = TransactionHistory(
                transaction_type = t_type,
                transaction_name = random.choice([
                    "Barangay Clearance",
                    "Certificate of Indigency",
                    "Certificate of Residency",
                    "Plastic Chairs (set of 50)",
                    "Sound System (PA Set)",
                    "Barangay ID",
                ]),
                transaction_no   = no,
                resident_id      = resident.id,
                rfid_uid         = None,
                status           = random.choices(["Completed", "Rejected"], weights=[85, 15])[0],
                created_at       = _resident_request_dt(resident),
            )
            db.add(th)
            count += 1
    else:
        print("  ⚠  No transaction-eligible residents found — standalone entries skipped.")

    db.commit()
    print(f"  ↳ Inserted {count} transaction history entries.")