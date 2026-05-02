"""
seeds/seed_feedback.py  (also contains RFIDReport seeding)

Rules:
- Feedbacks submitted by RFID residents → real resident_id, linked to their account
- Feedbacks submitted in Guest Mode     → resident_id = None
- RFID Reports must always come from a resident who HAS an active RFID
  (they are reporting a problem with their own card)

Resident restriction:
    Only the 31 transaction-eligible residents are used as identified
    feedback submitters and RFID report filers — not the full resident pool.
"""

import random
from sqlalchemy.orm import Session

from seeds.utils import rand_dt
from app.models.misc import Feedback, RFIDReport
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Same 31 transaction-eligible residents as the other seeders.
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


FEEDBACK_COMMENTS = {
    "Service Quality": [
        "The staff were very accommodating and professional.",
        "Processing was smooth and the admin explained everything clearly.",
        "The service was a bit slow but the staff were polite.",
        "I was impressed with how quickly my request was processed.",
        None,
    ],
    "Interface Design": [
        "The kiosk was easy to navigate even for seniors.",
        "The screen buttons are clear and readable.",
        "I had some trouble finding the right menu option at first.",
        None,
    ],
    "System Speed": [
        "The system responded quickly without any delays.",
        "There was a slight lag when uploading my information.",
        "Everything loaded fast, no issues.",
        None,
    ],
    "Accessibility": [
        "The kiosk height is a bit tall for shorter residents.",
        "I appreciate that instructions are in Filipino.",
        "Would be great to have a larger font option.",
        None,
    ],
    "General Experience": [
        "Overall a very positive experience. Great improvement from before.",
        "The digital system saves a lot of time compared to manual processing.",
        "Would recommend this to other barangays.",
        "Satisfied with the service. Keep it up!",
        None,
    ],
}

CATEGORIES = list(FEEDBACK_COMMENTS.keys())


def seed_feedback(db: Session):
    print("\n[feedback] Seeding feedback and RFID reports …")

    # ── Restrict to the 31 real transaction-eligible residents ─────
    rfid_residents = _get_transaction_residents(db)

    if not rfid_residents:
        print("  ↳ No transaction-eligible residents found — skipping.")
        return

    # ── Seed Feedbacks ────────────────────────────────────────────
    existing_fb = db.query(Feedback).count()
    if existing_fb < 10:
        count = 0
        for _ in range(30):
            category = random.choice(CATEGORIES)
            rating   = random.choices(
                [1, 2, 3, 4, 5],
                weights=[3, 5, 12, 40, 40],
                k=1,
            )[0]
            comment = random.choice(FEEDBACK_COMMENTS[category])

            # ~30% chance of Guest Mode submission (resident_id = None)
            is_guest = random.random() < 0.30

            fb = Feedback(
                resident_id         = None if is_guest else random.choice(rfid_residents).id,
                category            = category,
                rating              = rating,
                additional_comments = comment,
                created_at          = rand_dt(),
            )
            db.add(fb)
            count += 1

        db.commit()
        print(f"  ↳ Inserted {count} feedback records (mix of RFID-linked and Guest Mode).")
    else:
        print(f"  ↳ Skipped feedback — {existing_fb} already exist.")

    # ── Seed RFID Reports ─────────────────────────────────────────
    # Only residents WITH an active RFID can file an RFID report
    # (they are reporting an issue with their own card).
    existing_rfid_rep = db.query(RFIDReport).count()
    if existing_rfid_rep < 3:
        rcount = 0
        for _ in range(8):
            resident = random.choice(rfid_residents)
            status   = random.choice(["Pending", "Resolved"])
            rr = RFIDReport(
                resident_id = resident.id,
                status      = status,
                created_at  = rand_dt(),
            )
            db.add(rr)
            rcount += 1

        db.commit()
        print(f"  ↳ Inserted {rcount} RFID reports.")
    else:
        print(f"  ↳ Skipped RFID reports — {existing_rfid_rep} already exist.")