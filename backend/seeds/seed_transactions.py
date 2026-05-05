"""
seeds/seed_transactions.py

Seeds TransactionHistory for completed/rejected document and equipment requests.
Run AFTER seed_documents and seed_equipment so real request data exists.

Resident restriction:
    Standalone historical entries (seeded for volume) are restricted to the
    same 31 transaction-eligible residents used in seed_documents and
    seed_equipment — not drawn from the full resident pool.

ID prerequisite:
    This mirrors the updated document/equipment seeders. Standalone history
    entries are anchored to each resident's survey date / issued Barangay ID
    date so seeded activity does not appear before kiosk eligibility.
"""

import random
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, progression, DEPLOY_END
from app.models.barangayid import BarangayID
from app.models.transaction import TransactionHistory
from app.models.document import DocumentRequest
from app.models.equipment import EquipmentRequest
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Same 31 transaction-eligible residents as the other seeders.
#
# NOTE:
#   This intentionally matches seed_documents.py. Resident.first_name only
#   stores the first token from seed_residents.py, so matching uses only the
#   first token of compound names such as "Chariel Althea" or
#   "Ma. Monica Yinley".
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
# Survey dates — order matches TRANSACTION_RESIDENTS exactly.
# Kept in list form to mirror seed_documents.py and prevent the
# compound-name matching bugs caused by dict lookups.
# ─────────────────────────────────────────────────────────────

SURVEY_DATES = [
    date(2026, 3, 16),   # Vibandor, Mylene
    date(2026, 3, 16),   # Angcaya, Joana
    date(2026, 3, 16),   # Delarmino, Chariel Althea
    date(2026, 3, 16),   # Bataclan, Jenna Rose
    date(2026, 3, 17),   # Angcaya, Ma. Monica Yinley
    date(2026, 3, 20),   # Dela Rea, Justine Carl
    date(2026, 3, 20),   # Jamon, Alliah Mae
    date(2026, 3, 21),   # Plaganas, Maria Aleth
    date(2026, 3, 21),   # Gutierrez, Gillian Lou
    date(2026, 3, 23),   # Bayas, Allister Marvin
    date(2026, 3, 26),   # Angcaya, Micah Angelie
    date(2026, 3, 26),   # Cruz, Kenjie Ryle
    date(2026, 3, 26),   # Sipat, Marife
    date(2026, 3, 28),   # Ramos, Naomi Rose
    date(2026, 3, 28),   # Ramos, Winona Kylie
    date(2026, 3, 28),   # Barrera, Lourella
    date(2026, 3, 30),   # Dela Rea, Kristal Joy
    date(2026, 4,  1),   # Panganiban, Arvin
    date(2026, 4,  3),   # Dela Rea, Carissa Mae
    date(2026, 4,  3),   # Dimayuga, Ghia Larize
    date(2026, 4,  4),   # Sumagui, Emil
    date(2026, 4,  4),   # Sumagui, Niel
    date(2026, 4,  7),   # Sumagui, Emmanuel
    date(2026, 4,  8),   # San Martin, Bobby
    date(2026, 4, 10),   # Fresco, Veronica Anne
    date(2026, 4, 10),   # San Martin, Franco
    date(2026, 4, 10),   # Mora, Mary Joy
    date(2026, 4, 13),   # Madera, Aubrey Rose
    date(2026, 4, 15),   # Bayot, Rochelle Ann
    date(2026, 4, 18),   # Villamor, Keith Beau Allen
    date(2026, 4, 18),   # Ambion, Johanne Alecs
]


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _deploy_tzinfo():
    """Return DEPLOY_END's timezone if it is timezone-aware; otherwise None."""
    if isinstance(DEPLOY_END, datetime) and DEPLOY_END.tzinfo is not None:
        return DEPLOY_END.tzinfo
    return None


def _as_seed_datetime(d: date, hour: int, minute: int, second: int = 0) -> datetime:
    """Build a datetime that is comparable with DEPLOY_END."""
    return datetime(d.year, d.month, d.day, hour, minute, second, tzinfo=_deploy_tzinfo())


def _next_business_day(d: date) -> date:
    """Shift Saturday/Sunday dates to Monday; leave weekdays unchanged."""
    if d.weekday() == 5:      # Saturday
        return d + timedelta(days=2)
    if d.weekday() == 6:      # Sunday
        return d + timedelta(days=1)
    return d


def _safe_progression(start: datetime, min_hours: int, max_hours: int) -> datetime:
    """
    Call the shared progression helper, then cap the result at DEPLOY_END
    when DEPLOY_END is available/comparable.
    """
    created_at = progression(start, min_hours, max_hours)

    if isinstance(DEPLOY_END, datetime):
        if created_at.tzinfo is None and DEPLOY_END.tzinfo is not None:
            created_at = created_at.replace(tzinfo=DEPLOY_END.tzinfo)
        elif created_at.tzinfo is not None and DEPLOY_END.tzinfo is None:
            created_at = created_at.replace(tzinfo=None)

        if created_at > DEPLOY_END:
            created_at = DEPLOY_END - timedelta(minutes=random.randint(1, 60))

    return created_at


def _get_transaction_resident_pairs(db: Session) -> list[tuple[Resident, date]]:
    """
    Return matched (Resident, survey_date) pairs for the 31 transaction
    residents, preserving the same resident/date relationship as
    seed_documents.py.

    Matching strategy:
      - last_name  : exact, case-insensitive
      - first_name : match only the FIRST TOKEN of the configured first name,
                     because seed_residents.py stores only the first word in
                     Resident.first_name.
      - only residents with an active RFID are eligible.
    """
    if len(TRANSACTION_RESIDENTS) != len(SURVEY_DATES):
        raise RuntimeError(
            "TRANSACTION_RESIDENTS and SURVEY_DATES must have the same length."
        )

    all_residents = (
        db.query(Resident)
        .join(Resident.rfids)
        .filter(ResidentRFID.is_active == True)
        .all()
    )

    matched_pairs: list[tuple[Resident, date]] = []
    missing = []

    for (last, first_start), survey_date in zip(TRANSACTION_RESIDENTS, SURVEY_DATES):
        last_norm        = last.strip().lower()
        first_token_norm = first_start.strip().lower().split()[0]

        found = None
        for r in all_residents:
            if (
                r.last_name.strip().lower() == last_norm
                and r.first_name.strip().lower().split()[0] == first_token_norm
            ):
                found = r
                break

        if found is None:
            missing.append((last, first_start))
        else:
            matched_pairs.append((found, survey_date))

    if missing:
        names = ", ".join(f"{last} {first}" for last, first in missing)
        print(f"  ⚠  Could not match {len(missing)} resident(s): {names}")

    return matched_pairs


def _kiosk_ready_date(db: Session, resident: Resident, survey_date: date) -> date:
    """
    Prefer the resident's active Barangay ID issued date, because the updated
    document seeder creates released ID applications before kiosk activity.
    Fall back to the survey date if transactions are seeded independently.
    """
    active_id = (
        db.query(BarangayID)
        .filter(
            BarangayID.resident_id == resident.id,
            BarangayID.is_active == True,
        )
        .order_by(BarangayID.issued_date.desc())
        .first()
    )

    if active_id and active_id.issued_date:
        issued = active_id.issued_date
        return issued.date() if isinstance(issued, datetime) else issued

    return survey_date


def _resident_request_dt(db: Session, resident: Resident, survey_date: date) -> datetime:
    """
    Return a realistic standalone TransactionHistory created_at datetime.

    The date starts from the resident's ID issued date when available,
    otherwise from their survey date. A 0–3 day random offset is added,
    weekends are shifted to Monday, and the result is capped inside the
    deployment window.
    """
    base_date   = _kiosk_ready_date(db, resident, survey_date)
    target_date = _next_business_day(base_date + timedelta(days=random.randint(0, 3)))

    target_dt = _as_seed_datetime(
        target_date,
        random.randint(8, 16),
        random.randint(0, 59),
        random.randint(0, 59),
    )

    if isinstance(DEPLOY_END, datetime) and target_dt > DEPLOY_END:
        target_dt = DEPLOY_END - timedelta(minutes=random.randint(1, 60))

    return target_dt


def _active_rfid_uid(resident: Resident | None) -> str | None:
    """Return the resident's active RFID UID, if one exists."""
    if resident is None:
        return None

    active_rfid = next((r for r in getattr(resident, "rfids", []) if r.is_active), None)
    return active_rfid.rfid_uid if active_rfid else None


def _request_rfid_uid(req) -> str | None:
    """
    Prefer the RFID captured in form_data, then fall back to the resident's
    active RFID card.
    """
    form_data = req.form_data if isinstance(getattr(req, "form_data", None), dict) else {}

    captured = form_data.get("session_rfid") or form_data.get("rfid_uid")
    if captured and captured != "Guest Mode":
        return captured

    return _active_rfid_uid(getattr(req, "resident", None))


def _document_transaction_name(req: DocumentRequest) -> str:
    """
    Name document transactions correctly, including ID applications whose
    DocumentRequest.doctype_id is intentionally NULL in the updated seeder.
    """
    if req.doctype:
        return req.doctype.doctype_name

    form_data = req.form_data if isinstance(req.form_data, dict) else {}
    if form_data.get("request_type") == "ID Application":
        return "Barangay ID"

    return "Document"


def _standalone_transaction_no(db: Session, prefix: str) -> str:
    """Generate a unique standalone transaction number for TransactionHistory."""
    while True:
        no = f"{prefix}-{random.randint(9000, 9999)}"
        exists = (
            db.query(TransactionHistory)
            .filter(TransactionHistory.transaction_no == no)
            .first()
        )
        if not exists:
            return no


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
        status = "Completed" if req.status == "Released" else "Rejected"

        th = TransactionHistory(
            transaction_type = "document",
            transaction_name = _document_transaction_name(req),
            transaction_no   = req.transaction_no,
            resident_id      = req.resident_id,
            rfid_uid         = _request_rfid_uid(req),
            status           = status,
            created_at       = _safe_progression(req.requested_at, 1, 72),
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
            rfid_uid         = _request_rfid_uid(req),
            status           = status,
            created_at       = req.returned_at or _safe_progression(req.requested_at, 24, 96),
        )
        db.add(th)
        count += 1

    # ── Standalone historical entries (for volume) ────────────────
    # Restricted to the 31 real transaction-eligible residents only.
    resident_pairs = _get_transaction_resident_pairs(db)
    if resident_pairs:
        for _ in range(15):
            resident, survey_date = random.choice(resident_pairs)
            t_type = random.choice(["document", "equipment"])
            prefix = "DR" if t_type == "document" else "ER"

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
                transaction_no   = _standalone_transaction_no(db, prefix),
                resident_id      = resident.id,
                rfid_uid         = _active_rfid_uid(resident),
                status           = random.choices(["Completed", "Rejected"], weights=[85, 15])[0],
                created_at       = _resident_request_dt(db, resident, survey_date),
            )
            db.add(th)
            count += 1
    else:
        print("  ⚠  No transaction-eligible residents found — standalone entries skipped.")

    db.commit()
    print(f"  ↳ Inserted {count} transaction history entries.")
