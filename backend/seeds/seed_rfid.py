from app.db.session import SessionLocal
from app.models.resident import ResidentRFID, Resident

RFIDS = [
    "0029536238",
    "0054973429",
]

def seed_rfids():
    db = SessionLocal()
    try:
        if db.query(ResidentRFID).count() > 0:
            print("✅ RFID already seeded")
            return

        residents = db.query(Resident).limit(len(RFIDS)).all()

        for res, uid in zip(residents, RFIDS):
            db.add(ResidentRFID(
                resident_id=res.id,
                rfid_uid=uid
            ))

        db.commit()
        print("🌱 RFID seeded")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding RFID:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_rfids()
