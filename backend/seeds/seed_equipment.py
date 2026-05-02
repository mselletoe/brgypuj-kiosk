"""
seeds/seed_equipment.py

Seeds equipment inventory items and borrowing requests
with realistic status progressions within the deployment window.

Resident restriction:
    Only the 31 residents listed in TRANSACTION_RESIDENTS are used as
    requestors. These are the real residents from the source data who
    actually made document/equipment transactions.
"""

import random
from datetime import timedelta
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, progression, DEPLOY_START, DEPLOY_END
from app.models.equipment import EquipmentInventory, EquipmentRequest, EquipmentRequestItem
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Residents allowed to appear in equipment transactions.
# Stored as (last_name, first_name_start) — matched
# case-insensitively against the Resident table after seeding.
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


def _get_transaction_residents(db: Session) -> list:
    """
    Return the subset of Resident ORM objects that match TRANSACTION_RESIDENTS.
    Matching is done by last_name (exact, title-case) and the start of first_name
    (covers compound first names like 'Ma. Monica Yinley').
    Only residents with an active RFID card are included — consistent with how
    the kiosk authenticates requestors.
    """
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
                break  # one match per entry is enough

    if not matched:
        raise RuntimeError(
            "No transaction-eligible residents found. "
            "Run seed_residents first and make sure RFID cards are assigned."
        )

    return matched


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


def _generate_transaction_no(db: Session) -> str:
    while True:
        number         = random.randint(1000, 9999)
        transaction_no = f"ER-{number}"
        exists         = db.query(EquipmentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


def _days_between(start, end) -> int:
    return max(1, (end - start).days)


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

    # ── Restrict to the 31 real transaction residents ─────────────
    try:
        residents = _get_transaction_residents(db)
    except RuntimeError as e:
        print(f"  ↳ {e}")
        return

    print(f"  ↳ Transaction-eligible residents loaded: {len(residents)}")

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
        resident     = random.choice(residents)
        requested_at = rand_dt()

        # Borrow window
        borrow_start = requested_at + timedelta(days=random.randint(1, 4))
        borrow_end   = borrow_start  + timedelta(days=random.randint(1, 3))
        if borrow_end > DEPLOY_END:
            borrow_end = DEPLOY_END - timedelta(hours=1)

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