from app.db.session import SessionLocal
from app.models.admin import Admin
from app.models.resident import Resident
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_admin():
    db = SessionLocal()
    try:
        if db.query(Admin).count() > 0:
            print("✅ Admin already exists")
            return

        resident = db.query(Resident).first()

        admin = Admin(
            resident_id=resident.id,
            username="admin",
            password=pwd.hash("admin123"),
            role="superadmin"
        )

        db.add(admin)
        db.commit()
        print("🌱 Admin seeded")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding admin:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()