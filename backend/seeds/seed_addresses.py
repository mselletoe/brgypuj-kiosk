from app.db.session import SessionLocal
from app.models.resident import Address, Resident, Purok

def seed_addresses():
    db = SessionLocal()
    try:
        if db.query(Address).count() > 0:
            print("✅ Addresses already seeded")
            return

        residents = db.query(Resident).all()
        puroks = db.query(Purok).all()

        for idx, res in enumerate(residents):
            purok = puroks[idx % len(puroks)]  # Distribute across puroks
            db.add(Address(
                resident_id=res.id,
                purok_id=purok.id,
                house_no_street=f"Blk {idx+1} Lot {(idx % 10) + 1}"
            ))

        db.commit()
        print("🌱 Addresses seeded")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding addresses:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_addresses()
