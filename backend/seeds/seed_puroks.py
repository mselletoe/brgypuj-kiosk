"""
seeds/seed_puroks.py

Seeds Purok 1 through Purok 5 for Barangay Poblacion Uno.
Safe to run multiple times (skips if already seeded).
"""

from sqlalchemy.orm import Session
from app.models.resident import Purok


def seed_puroks(db: Session):
    print("\n[puroks] Seeding puroks …")

    existing = db.query(Purok).count()
    if existing >= 5:
        print(f"  ↳ Skipped — {existing} puroks already exist.")
        return

    puroks = [Purok(purok_name=f"Purok {i}") for i in range(1, 6)]
    db.add_all(puroks)
    db.commit()

    print(f"  ↳ Inserted {len(puroks)} puroks (Purok 1 – Purok 5).")
    return puroks