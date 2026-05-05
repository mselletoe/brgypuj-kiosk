"""
seeds/seed_equipment.py

Seeds equipment inventory items and borrowing requests
with realistic status progressions within the deployment window.

Resident restriction:
    Only the 31 residents listed in TRANSACTION_RESIDENTS are used as
    requestors. These are the real residents from the source data who
    actually made document/equipment transactions.

ID prerequisite:
    This seeder mirrors seed_documents.py. Equipment requests are anchored
    to each resident's survey date / issued Barangay ID date so requests do
    not appear before the resident is eligible to use the kiosk.
"""

import random
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from seeds.utils import DEPLOY_END
from app.models.barangayid import BarangayID
from app.models.equipment import EquipmentInventory, EquipmentRequest, EquipmentRequestItem
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Residents allowed to appear in equipment transactions.
# Stored as (last_name, first_name) — matched case-insensitively
# against the Resident table after seeding.
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
# Survey dates — copied from seed_documents.py.
# Order matches TRANSACTION_RESIDENTS exactly.
# Equipment requested_at dates are generated from these dates, unless an
# issued BarangayID row exists, in which case the ID issued date is used as
# the earliest kiosk-eligible date.
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


# ── Inventory catalogue ──────────────────────────────────────────
EQUIPMENT_CATALOGUE = [
    {"name": "Plastic Chairs (set of 50)",  "total": 6,  "rate": 150.00},
    {"name": "Folding Tables (set of 10)",  "total": 4,  "rate": 200.00},
    {"name": "Tarpaulin / Tent (3x3m)",     "total": 5,  "rate": 300.00},
    {"name": "Sound System (PA Set)",       "total": 2,  "rate": 500.00},
    {"name": "Portable Generator",          "total": 2,  "rate": 800.00},
    {"name": "Karaoke Machine",             "total": 2,  "rate": 250.00},
    {"name": "Projector",                   "total": 2,  "rate": 400.00},
    {"name": "Extension Cord (10m)",        "total": 10, "rate":  50.00},
    {"name": "Electric Fan (stand)",        "total": 8,  "rate":  80.00},
    {"name": "Water Dispenser",             "total": 3,  "rate": 100.00},
]

PURPOSES = [
    "Birthday Celebration",
    "Town Fiesta Preparation",
    "Wedding Reception",
    "Graduation Party",
    "Purok Meeting",
    "Livelihood Training",
    "Community Clean-Up Awards Night",
    "PTA Meeting",
    "Barangay Sports Event",
    "Wake / Lamay",
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


def _generate_transaction_no(db: Session) -> str:
    while True:
        number         = random.randint(1000, 9999)
        transaction_no = f"ER-{number}"
        exists         = db.query(EquipmentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


def _days_between(start, end) -> int:
    return max(1, (end - start).days)


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

    if not matched_pairs:
        raise RuntimeError(
            "No transaction-eligible residents found. "
            "Run seed_residents first and make sure RFID cards are assigned."
        )

    return matched_pairs


def _kiosk_ready_date(db: Session, resident: Resident, survey_date: date) -> date:
    """
    Prefer the resident's active Barangay ID issued date, because the updated
    document seeder creates released ID applications before kiosk activity.
    Fall back to the survey date if equipment is seeded independently.
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
    Return a realistic equipment requested_at datetime for this resident.

    The request date starts from the resident's ID issued date when available,
    otherwise from their survey date. A 0–3 day random offset is added, weekends
    are shifted to Monday, and the result is capped inside the deployment window.
    """
    base_date   = _kiosk_ready_date(db, resident, survey_date)
    target_date = _next_business_day(base_date + timedelta(days=random.randint(0, 3)))

    target_dt = _as_seed_datetime(
        target_date,
        random.randint(8, 16),
        random.randint(0, 59),
        random.randint(0, 59),
    )

    # Keep enough room for a future borrow window whenever possible.
    latest_request_dt = DEPLOY_END - timedelta(days=5) if isinstance(DEPLOY_END, datetime) else None
    if latest_request_dt and target_dt > latest_request_dt:
        target_dt = latest_request_dt - timedelta(minutes=random.randint(1, 60))

    if isinstance(DEPLOY_END, datetime) and target_dt > DEPLOY_END:
        target_dt = DEPLOY_END - timedelta(minutes=random.randint(1, 60))

    return target_dt


# ── Main seeder ──────────────────────────────────────────────────

def seed_equipment(db: Session):
    print("\n[equipment] Seeding equipment inventory and requests …")

    # ── Inventory ─────────────────────────────────────────────────
    existing_inv = db.query(EquipmentInventory).count()
    if existing_inv == 0:
        for item in EQUIPMENT_CATALOGUE:
            inv = EquipmentInventory(
                name               = item["name"],
                total_quantity     = item["total"],
                available_quantity = item["total"],
                rate_per_day       = item["rate"],
            )
            db.add(inv)
        db.commit()
        print(f"  ↳ Inserted {len(EQUIPMENT_CATALOGUE)} inventory items.")
    else:
        print(f"  ↳ Inventory: {existing_inv} items already exist — skipping inventory insert.")

    inventory = db.query(EquipmentInventory).all()
    if not inventory:
        print("  ↳ No equipment inventory available — skipping requests.")
        return

    # ── Restrict to the 31 real transaction residents ─────────────
    try:
        resident_pairs = _get_transaction_resident_pairs(db)
    except RuntimeError as e:
        print(f"  ↳ {e}")
        return

    print(
        f"  ↳ Transaction-eligible residents loaded: "
        f"{len(resident_pairs)}/{len(TRANSACTION_RESIDENTS)}"
    )

    existing_req = db.query(EquipmentRequest).count()
    if existing_req >= 10:
        print(f"  ↳ Skipped requests — {existing_req} already exist.")
        return

    # ── Requests ──────────────────────────────────────────────────
    STATUS_WEIGHTS = [
        ("Returned",   40),
        ("Picked-Up",  20),
        ("Approved",   20),
        ("Rejected",   10),
        ("Pending",    10),
    ]
    statuses, weights = zip(*STATUS_WEIGHTS)

    count  = 0
    TARGET = 25

    for _ in range(TARGET):
        resident, survey_date = random.choice(resident_pairs)
        requested_at          = _resident_request_dt(db, resident, survey_date)

        # Borrow window
        borrow_start = requested_at + timedelta(days=random.randint(1, 4))
        borrow_end   = borrow_start  + timedelta(days=random.randint(1, 3))
        if borrow_end > DEPLOY_END:
            borrow_end = DEPLOY_END - timedelta(hours=1)
        if borrow_end <= borrow_start:
            borrow_start = max(requested_at, DEPLOY_END - timedelta(days=2))
            borrow_end   = DEPLOY_END - timedelta(hours=1)

        days   = max(1, _days_between(borrow_start, borrow_end))
        status = random.choices(statuses, weights=weights, k=1)[0]

        payment_status = "unpaid"
        returned_at    = None
        if status in ("Picked-Up", "Returned"):
            payment_status = "paid"
        if status == "Returned":
            returned_at = borrow_end + timedelta(hours=random.randint(0, 12))
            if returned_at > DEPLOY_END:
                returned_at = DEPLOY_END

        # Pick items
        chosen_items = random.sample(inventory, k=random.randint(1, min(3, len(inventory))))
        quantities   = [random.randint(1, max(1, item.total_quantity // 2)) for item in chosen_items]

        total_cost = sum(
            item.rate_per_day * qty * days
            for item, qty in zip(chosen_items, quantities)
        )

        req = EquipmentRequest(
            transaction_no = _generate_transaction_no(db),
            resident_id    = resident.id,
            contact_person = f"{resident.first_name} {resident.last_name}",
            contact_number = resident.phone_number or "09000000000",
            purpose        = random.choice(PURPOSES),
            status         = status,
            notes          = None,
            borrow_date    = borrow_start,
            return_date    = borrow_end,
            returned_at    = returned_at,
            total_cost     = round(total_cost, 2),
            payment_status = payment_status,
            is_refunded    = False,
            requested_at   = requested_at,
        )

        db.add(req)
        db.flush()

        for item, qty in zip(chosen_items, quantities):
            req_item = EquipmentRequestItem(
                equipment_request_id = req.id,
                item_id              = item.id,
                quantity             = qty,
            )
            db.add(req_item)

        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} equipment requests.")
