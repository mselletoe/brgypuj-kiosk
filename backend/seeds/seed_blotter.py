"""
seeds/seed_blotter.py

Seeds realistic barangay blotter records within the deployment window.
"""

import random
from datetime import timedelta, time
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, rand_date, DEPLOY_START, DEPLOY_END
from app.models.blotter import BlotterRecord
from app.models.resident import Resident


INCIDENT_TYPES = [
    "Noise Complaint",
    "Physical Altercation",
    "Verbal Abuse / Threats",
    "Property Damage",
    "Theft / Pilferage",
    "Trespassing",
    "Domestic Disturbance",
    "Stray Animals",
    "Illegal Gambling",
    "Unpaid Debt Dispute",
]

NARRATIVES = [
    "Complainant alleged that respondent caused disturbance in the neighborhood late at night, disrupting the peace of nearby residents.",
    "Complainant reported that respondent uttered threatening and offensive words in public view, causing alarm and distress.",
    "Complainant claims respondent's livestock repeatedly entered and damaged his/her garden and property without permission.",
    "Complainant alleged that respondent physically struck complainant during an argument over a land boundary dispute.",
    "Complainant reported that respondent has been playing loud music past midnight repeatedly, despite prior verbal warnings.",
    "Complainant claims respondent borrowed money amounting to several thousand pesos and has refused to repay despite multiple demands.",
    "Complainant reported finding personal belongings missing after respondent allegedly visited the property.",
    "Complainant alleged that respondent has been spreading false and malicious rumors causing damage to complainant's reputation.",
]

RECORDERS = [
    "Brgy. Secretary Maria Santos",
    "Brgy. Kagawad Pedro Reyes",
    "Brgy. Secretary Nelia Cruz",
    "Brgy. Captain Assistant Ramon Garcia",
]


def _fake_blotter_no(existing_nos: set) -> str:
    """Generate unique blotter number like BL-2026-001."""
    year = 2026
    for _ in range(200):
        num = random.randint(1, 99)
        no  = f"BL-{year}-{num:03d}"
        if no not in existing_nos:
            existing_nos.add(no)
            return no
    raise RuntimeError("Could not generate unique blotter number")


def seed_blotter(db: Session):
    print("\n[blotter] Seeding blotter records …")

    existing = db.query(BlotterRecord).count()
    if existing >= 5:
        print(f"  ↳ Skipped — {existing} blotter records already exist.")
        return

    residents = db.query(Resident).all()
    if len(residents) < 2:
        print("  ↳ Not enough residents — skipping.")
        return

    existing_nos: set = {r.blotter_no for r in db.query(BlotterRecord).all()}
    count = 0
    TARGET = 12

    for _ in range(TARGET):
        created_at    = rand_dt()
        incident_date = rand_date(DEPLOY_START.date(), DEPLOY_END.date())
        incident_time = time(random.randint(6, 22), random.choice([0, 15, 30, 45]))

        complainant = random.choice(residents)
        # Ensure respondent is a different person
        respondent = random.choice([r for r in residents if r.id != complainant.id])

        status = random.choices(
            ["active", "resolved"],
            weights=[60, 40],
            k=1,
        )[0]
        resolved_at = None
        if status == "resolved":
            resolved_at = created_at + timedelta(days=random.randint(1, 10))
            if resolved_at > DEPLOY_END:
                resolved_at = DEPLOY_END

        record = BlotterRecord(
            blotter_no          = _fake_blotter_no(existing_nos),
            complainant_id      = complainant.id,
            complainant_name    = f"{complainant.first_name} {complainant.last_name}",
            complainant_age     = random.randint(20, 65),
            complainant_address = "Poblacion Uno, Amadeo, Cavite",
            respondent_id       = respondent.id,
            respondent_name     = f"{respondent.first_name} {respondent.last_name}",
            respondent_age      = random.randint(20, 65),
            respondent_address  = "Poblacion Uno, Amadeo, Cavite",
            incident_date       = incident_date,
            incident_time       = incident_time,
            incident_place      = "Barangay Poblacion Uno, Amadeo, Cavite",
            incident_type       = random.choice(INCIDENT_TYPES),
            narrative           = random.choice(NARRATIVES),
            recorded_by         = random.choice(RECORDERS),
            contact_no          = complainant.phone_number or "09000000000",
            status              = status,
            created_at          = created_at,
            resolved_at         = resolved_at,
        )
        db.add(record)
        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} blotter records.")