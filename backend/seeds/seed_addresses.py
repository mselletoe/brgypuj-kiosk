import random
from app.db.session import SessionLocal
from app.models.resident import Address, Resident, Purok

# Street names common in Poblacion I, Amadeo, Cavite
STREET_NAMES = [
    "M. Roxas St.", "Rizal St.", "Bonifacio St.", "Mabini St.",
    "Aguinaldo St.", "Quezon St.", "Laurel St.", "Luna St.",
    "del Pilar St.", "Osmena St.", "Burgos St.", "Jacinto St.",
]

BARANGAY   = "Poblacion I"
MUNICIPALITY = "Amadeo"
PROVINCE   = "Cavite"
REGION     = "Region IV-A (CALABARZON)"


def seed_addresses():
    db = SessionLocal()
    try:
        if db.query(Address).count() > 0:
            print("✅ Addresses already seeded")
            return

        residents = db.query(Resident).all()
        puroks    = db.query(Purok).all()

        if not residents:
            print("❌ No residents found. Seed residents first.")
            return
        if not puroks:
            print("❌ No puroks found. Seed puroks first.")
            return

        for idx, res in enumerate(residents):
            purok  = puroks[idx % len(puroks)]
            street = random.choice(STREET_NAMES)
            blk    = random.randint(1, 20)
            lot    = random.randint(1, 15)

            db.add(Address(
                resident_id=res.id,
                purok_id=purok.id,
                house_no_street=f"Blk {blk} Lot {lot} {street}",
                barangay=BARANGAY,
                municipality=MUNICIPALITY,
                province=PROVINCE,
                region=REGION,
                is_current=True,
            ))

        db.commit()
        print(f"🌱 {len(residents)} address(es) seeded — Brgy. {BARANGAY}, {MUNICIPALITY}, {PROVINCE}")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding addresses:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_addresses()