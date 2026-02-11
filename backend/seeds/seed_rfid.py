from app.db.session import SessionLocal
from app.models.resident import ResidentRFID, Resident

# RFID assignments - linking specific residents to their RFID cards
RFID_ASSIGNMENTS = [
    {
        "first_name": "Maxpein Zin",
        "last_name": "del Valle",
        "rfid_uid": "0029536238"
    },
    {
        "first_name": "Maxwell Laurent",
        "last_name": "del Valle",
        "rfid_uid": "0054973429"
    },
]

def seed_rfids():
    db = SessionLocal()
    try:
        if db.query(ResidentRFID).count() > 0:
            print("✅ RFID already seeded")
            return

        for assignment in RFID_ASSIGNMENTS:
            # Find the resident by first and last name
            resident = db.query(Resident).filter(
                Resident.first_name == assignment["first_name"],
                Resident.last_name == assignment["last_name"]
            ).first()
            
            if resident:
                rfid_entry = ResidentRFID(
                    resident_id=resident.id,
                    rfid_uid=assignment["rfid_uid"]
                )
                db.add(rfid_entry)
                print(f"   📇 Assigned RFID {assignment['rfid_uid']} to {assignment['first_name']} {assignment['last_name']}")
            else:
                print(f"   ⚠️  Resident not found: {assignment['first_name']} {assignment['last_name']}")

        db.commit()
        print("🌱 RFID seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding RFID: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_rfids()