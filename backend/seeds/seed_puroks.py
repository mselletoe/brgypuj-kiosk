from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal
from app.models.resident import Purok

# Amadeo, Cavite typically uses numbered puroks
DEFAULT_PUROKS = [f"Purok {i}" for i in range(1, 11)]  # Purok 1–10


def seed_puroks():
    db = SessionLocal()
    try:
        seeded = 0
        for name in DEFAULT_PUROKS:
            if not db.query(Purok).filter(Purok.purok_name == name).first():
                db.add(Purok(purok_name=name))
                seeded += 1
        db.commit()
        if seeded:
            print(f"🌱 {seeded} purok(s) seeded.")
        else:
            print("✅ Puroks already seeded")
    except SQLAlchemyError as e:
        db.rollback()
        print("❌ Error seeding puroks:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_puroks()