"""
seeds/seed_residents.py

Each resident is now FULLY REGISTERED:
✔ Resident profile
✔ Address
✔ RFID issuance (ResidentRFID)
✔ Barangay ID issuance (BarangayID)

This enforces system rule:
No resident exists without identity issuance.
"""

import random
import hashlib
import uuid
from datetime import date, timedelta
from sqlalchemy.orm import Session

from seeds.utils import (
    rand_historic_date, rand_date, fake_name, fake_phone, fake_email,
    STREETS, DEPLOY_START, DEPLOY_END,
)

# Models
from app.models.resident import Resident, Address, Purok, ResidentRFID
from app.models.barangayid import BarangayID


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _fake_birthdate(min_age: int = 18, max_age: int = 75) -> date:
    today = date.today()
    days = random.randint(min_age * 365, max_age * 365)
    return today - timedelta(days=days)


def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()


def _get_or_create_puroks(db: Session) -> list:
    puroks = db.query(Purok).all()
    if not puroks:
        for i in range(1, 6):
            db.add(Purok(purok_name=f"Purok {i}"))
        db.commit()
        puroks = db.query(Purok).all()
    return puroks


# ─────────────────────────────────────────────────────────────
# Core creation logic
# ─────────────────────────────────────────────────────────────

def _create_resident(
    db: Session,
    puroks: list,
    gender: str,
    registered_at,
    residency_start: date,
) -> Resident:

    name = fake_name(gender)

    # ── 1. Create Resident ─────────────────────────────
    resident = Resident(
        last_name=name["last_name"],
        first_name=name["first_name"],
        middle_name=name["middle_name"],
        suffix=None,
        gender=gender,
        birthdate=_fake_birthdate(),
        residency_start_date=residency_start,
        email=fake_email(name["first_name"], name["last_name"]),
        phone_number=fake_phone(),
        rfid_pin=_hash_pin(str(random.randint(1000, 9999))),
        registered_at=registered_at,
    )

    db.add(resident)
    db.flush()  # get resident.id

    # ── 2. Create Address ─────────────────────────────
    purok = random.choice(puroks)

    address = Address(
        resident_id=resident.id,
        house_no_street=f"{random.randint(1, 200)} {random.choice(STREETS)}",
        purok_id=purok.id,
        barangay="Poblacion Uno",
        municipality="Amadeo",
        province="Cavite",
        region="Region IV-A",
        is_current=True,
        created_at=registered_at,
    )

    db.add(address)

    # ── 3. ISSUE RFID (IMPORTANT FIX) ──────────────────
    rfid_number = str(random.randint(10000000000, 99999999999))  # 11 digits

    rfid = ResidentRFID(
        resident_id=resident.id,
        rfid_uid=rfid_number,
        is_active=True,
        created_at=registered_at,
    )

    db.add(rfid)
    db.flush()

    # ── 4. ISSUE BARANGAY ID ───────────────────────────
    brgy_number = str(random.randint(100000, 999999))  # 6 digits

    brgy_id = BarangayID(
        brgy_id_number=brgy_number,
        resident_id=resident.id,
        rfid_id=rfid.id,
        issued_date=registered_at if isinstance(registered_at, date) else registered_at.date(),
        expiration_date=None,
        is_active=True,
        created_at=registered_at,
    )

    db.add(brgy_id)

    return resident


# ─────────────────────────────────────────────────────────────
# Seeder
# ─────────────────────────────────────────────────────────────

def seed_residents(db: Session):
    print("\n[residents] Seeding residents …")

    puroks = _get_or_create_puroks(db)

    existing = db.query(Resident).count()
    if existing >= 30:
        print(f"  ↳ Skipped — {existing} residents already exist.")
        return

    residents = []

    # ── 1. Long-term residents (3–10 years ago)
    for _ in range(15):
        reg_date = rand_historic_date(years_ago_min=3, years_ago_max=10)
        gender = random.choice(["male", "female"])
        r = _create_resident(db, puroks, gender, reg_date, reg_date)
        residents.append(r)

    # ── 2. Medium-term residents (1–3 years ago)
    for _ in range(10):
        reg_date = rand_historic_date(years_ago_min=1, years_ago_max=3)
        gender = random.choice(["male", "female"])
        r = _create_resident(db, puroks, gender, reg_date, reg_date)
        residents.append(r)

    # ── 3. New residents (deployment window)
    for _ in range(8):
        reg_dt = rand_date(DEPLOY_START.date(), DEPLOY_END.date())
        gender = random.choice(["male", "female"])
        r = _create_resident(db, puroks, gender, reg_dt, reg_dt)
        residents.append(r)

    db.commit()

    print(f"  ↳ Inserted {len(residents)} residents (with RFID + Barangay ID).")

    return residents