from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal
from app.models.resident import Purok

# List of default puroks
default_puroks = [
    "Purok 1", "Purok 2", "Purok 3", "Purok 4", "Purok 5",
    "Purok 6", "Purok 7", "Purok 8", "Purok 9", "Purok 10"
]

def seed_puroks():
    db = SessionLocal()
    try:
        for name in default_puroks:
            # Check if purok already exists
            existing = db.query(Purok).filter(Purok.purok_name == name).first()
            if not existing:
                db.add(Purok(purok_name=name))
        db.commit()
        print("✅ Successfully seeded puroks.")
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Error seeding puroks:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_puroks()