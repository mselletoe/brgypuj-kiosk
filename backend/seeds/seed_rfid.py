from app.db.session import SessionLocal
from app.models.resident import ResidentRFID, Resident
import random

# How many residents to assign RFIDs to
RFID_COUNT = 10


def generate_rfid_uid(index: int) -> str:
    """Generate a zero-padded 10-digit RFID UID."""
    return str(index + 1).zfill(10)


def seed_rfids():
    db = SessionLocal()
    try:
        if db.query(ResidentRFID).count() > 0:
            print("✅ RFIDs already seeded")
            return

        residents = db.query(Resident).all()
        if not residents:
            print("❌ No residents found. Seed residents first.")
            return

        # Pick a random subset of residents to assign RFIDs to
        count = min(RFID_COUNT, len(residents))
        selected = random.sample(residents, count)

        for idx, resident in enumerate(selected):
            db.add(ResidentRFID(
                resident_id=resident.id,
                rfid_uid=generate_rfid_uid(idx),
            ))
            print(f"   📇 Assigned {generate_rfid_uid(idx)} → "
                  f"{resident.first_name} {resident.last_name}")

        db.commit()
        print(f"🌱 {count} RFID(s) seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding RFID: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_rfids()