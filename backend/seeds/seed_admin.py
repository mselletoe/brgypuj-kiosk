"""
Seed Admin Accounts
-------------------
Seeds two accounts on first deployment:
  1. superadmin  — Barangay Captain    (full system access)
  2. brgy_admin  — Barangay Secretary  (standard admin access)

Both are linked to the first two generated residents.
⚠️  Change both passwords immediately after first login.
"""
from app.db.session import SessionLocal
from app.models.admin import Admin
from app.models.resident import Resident
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADMIN_ACCOUNTS = [
    {
        "username":       "superadmin",
        "password":       "superadmin123",
        "position":       "Barangay Captain",
        "system_role":    "superadmin",
        "resident_index": 0,
    },
    {
        "username":       "brgy_admin",
        "password":       "admin123",
        "position":       "Barangay Secretary",
        "system_role":    "admin",
        "resident_index": 1,
    },
]


def seed_admin():
    db = SessionLocal()
    try:
        residents = db.query(Resident).order_by(Resident.id).all()
        if not residents:
            print("❌ Cannot seed admins: no residents found. Seed residents first.")
            return

        seeded = 0
        for acct in ADMIN_ACCOUNTS:
            if db.query(Admin).filter(Admin.username == acct["username"]).first():
                print(f"✅ Admin already exists: '{acct['username']}'")
                continue

            idx      = min(acct["resident_index"], len(residents) - 1)
            resident = residents[idx]

            db.add(Admin(
                resident_id=resident.id,
                username=acct["username"],
                password=pwd.hash(acct["password"]),
                position=acct["position"],
                system_role=acct["system_role"],
                is_active=True,
            ))
            seeded += 1
            print(f"   👤 Queued: {acct['username']} ({acct['system_role']})")

        if seeded:
            db.commit()
            print(f"🌱 {seeded} admin account(s) seeded.")
            print()
            print("   ┌──────────────────────────────────────────────────────┐")
            print("   │  USERNAME      PASSWORD          ROLE                │")
            print("   ├──────────────────────────────────────────────────────┤")
            print("   │  superadmin    superadmin123     superadmin          │")
            print("   │  brgy_admin    admin123          admin               │")
            print("   └──────────────────────────────────────────────────────┘")
            print("   ⚠️  Change both passwords on first login!")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding admins:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()