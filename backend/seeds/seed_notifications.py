"""
seeds/seed_notifications.py

Notifications are admin-facing system events. Names and transaction
references are derived from the real 31 transaction-eligible residents
and realistic DR-/ER- reference numbers — not hardcoded fake data.
"""

import random
from sqlalchemy.orm import Session

from seeds.utils import rand_dt
from app.models.notification import Notification
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Residents whose names appear in notification messages.
# Same 31 residents used in seed_documents / seed_equipment.
# ─────────────────────────────────────────────────────────────

TRANSACTION_RESIDENTS = [
    ("Vibandor",   "Mylene"),
    ("Angcaya",    "Joana"),
    ("Delarmino",  "Chariel Althea"),
    ("Bataclan",   "Jenna Rose"),
    ("Angcaya",    "Ma."),
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


NOTIFICATION_TEMPLATES = [
    # (type, event, msg_template)
    ("Document", "doc_pending",   "New document request submitted — {ref}"),
    ("Document", "doc_approved",  "Document request {ref} has been approved."),
    ("Document", "doc_released",  "Document request {ref} is ready for release."),
    ("Document", "doc_rejected",  "Document request {ref} was rejected."),
    ("Equipment","equip_pending", "New equipment borrowing request from {name}."),
    ("Equipment","equip_approved","Equipment request {ref} approved."),
    ("Equipment","equip_returned","Equipment from request {ref} has been returned."),
    ("Feedback", "feedback_new",  "A resident submitted new feedback (Rating: {rating}/5)."),
    ("Feedback", "feedback_new",  "Feedback received — General Experience (⭐{rating}/5)."),
    ("System",   "system_info",   "System maintenance completed successfully."),
    ("System",   "system_info",   "Database backup completed."),
    ("Resident", "resident_new",  "New resident registered: {name}."),
]

DR_REFS = [f"DR-{n}" for n in range(1001, 1041)]
ER_REFS = [f"ER-{n}" for n in range(2001, 2015)]


def seed_notifications(db: Session):
    print("\n[notifications] Seeding notifications …")

    existing = db.query(Notification).count()
    if existing >= 10:
        print(f"  ↳ Skipped — {existing} notifications already exist.")
        return

    residents = _get_transaction_residents(db)
    if not residents:
        print("  ↳ No transaction-eligible residents found — run seed_residents first.")
        return

    # Build "Last, First" display names from real residents
    names = [f"{r.last_name}, {r.first_name}" for r in residents]
    refs  = DR_REFS + ER_REFS

    count = 0
    for _ in range(40):
        tpl_type, event, msg_tpl = random.choice(NOTIFICATION_TEMPLATES)

        msg = msg_tpl.format(
            ref    = random.choice(refs),
            name   = random.choice(names),
            rating = random.randint(3, 5),
        )

        n = Notification(
            type       = tpl_type,
            msg        = msg,
            is_read    = random.choices([True, False], weights=[60, 40])[0],
            event      = event,
            created_at = rand_dt(),
        )
        db.add(n)
        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} notifications.")