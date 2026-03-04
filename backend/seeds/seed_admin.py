"""
Seed Superadmin
---------------
Run this ONCE on first deployment to bootstrap the initial superadmin account.
After this, all future accounts are created through the admin dashboard.

Usage:
    python -m app.scripts.seed_admin
    or
    python seed_admin.py
"""
from app.db.session import SessionLocal
from app.models.admin import Admin
from app.models.resident import Resident
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_superadmin():
    db = SessionLocal()
    try:
        # Guard: never overwrite an existing superadmin
        existing = db.query(Admin).filter(Admin.system_role == "superadmin").first()
        if existing:
            print(f"✅ Superadmin already exists: '{existing.username}'")
            return

        # A superadmin account must be linked to a real resident record
        resident = db.query(Resident).first()
        if not resident:
            print("❌ Cannot seed: no residents found. Seed residents first.")
            return

        admin = Admin(
            resident_id=resident.id,
            username="superadmin",
            password=pwd.hash("superadmin123"),   # ⚠️  Change this immediately after first login
            position="Barangay Captain",           # Adjust as needed
            system_role="superadmin",
            is_active=True,
        )

        db.add(admin)
        db.commit()
        print("🌱 Superadmin seeded successfully.")
        print("   Username : superadmin")
        print("   Password : superadmin123  ← change this on first login!")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding superadmin:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_superadmin()