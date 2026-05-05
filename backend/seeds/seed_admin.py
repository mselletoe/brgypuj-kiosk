"""
Seed Admin Accounts
-------------------
Seeds three accounts on first deployment:
  1. superadmin   — Barangay Captain    (Joel A. Angcaya)       — full system access
  2. sk_chairman  — SK Chairman         (Jelyn Mae D. Vibandor) — standard admin access
  3. brgy_admin   — Barangay Secretary  (Ma. Judith B. Borja)   — standard admin access

All are linked to their corresponding resident records.
⚠️  Change all passwords immediately after first login.
"""
from app.models.admin import Admin
from app.models.resident import Resident
from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# resident_index matches the order in RESIDENTS_DATA in seed_residents.py:
#   0  → JOEL A. ANGCAYA
#  29  → JELYN MAE D. VIBANDOR
#  54  → MA. JUDITH B. BORJA
ADMIN_ACCOUNTS = [
    {
        "username":       "superadmin",
        "password":       "superadmin123",
        "position":       "Barangay Captain",
        "system_role":    "superadmin",
        "resident_index": 0,
    },
    {
        "username":       "sk_chairman",
        "password":       "admin123",
        "position":       "SK Chairman",
        "system_role":    "admin",
        "resident_index": 29,
    },
    {
        "username":       "brgy_admin",
        "password":       "admin123",
        "position":       "Barangay Secretary",
        "system_role":    "admin",
        "resident_index": 54,
    },
]


def seed_admin(db):
    try:
        residents = db.query(Resident).order_by(Resident.id).all()

        if not residents:
            print("❌ Cannot seed admins: no residents found. Seed residents first.")
            return

        seeded = 0

        for acct in ADMIN_ACCOUNTS:
            existing = db.query(Admin).filter(Admin.username == acct["username"]).first()
            if existing:
                print(f"✅ Admin already exists: '{acct['username']}'")
                continue

            idx = min(acct["resident_index"], len(residents) - 1)
            resident = residents[idx]

            admin = Admin(
                resident_id=resident.id,
                username=acct["username"],
                password=pwd.hash(acct["password"]),
                position=acct["position"],
                system_role=acct["system_role"],
                is_active=True,
            )

            db.add(admin)
            seeded += 1
            print(f"   👤 Queued: {acct['username']} ({acct['system_role']})")

        if seeded:
            db.commit()
            print(f"🌱 {seeded} admin account(s) seeded.\n")

            print("   ┌──────────────────────────────────────────────────────────────────┐")
            print("   │  USERNAME      PASSWORD          ROLE        POSITION            │")
            print("   ├──────────────────────────────────────────────────────────────────┤")
            print("   │  superadmin    superadmin123     superadmin  Barangay Captain     │")
            print("   │  sk_chairman   admin123          admin       SK Chairman          │")
            print("   │  brgy_admin    admin123          admin       Barangay Secretary   │")
            print("   └──────────────────────────────────────────────────────────────────┘")
            print("   ⚠️  Change all passwords on first login!")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding admins:", e)