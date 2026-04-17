"""
seeds/seed_all.py
"""

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin7890@localhost:5432/kioskdb"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def seed_all():
    db = SessionLocal()
    try:
        print("=" * 60)
        print("  BARANGAY SEED — Deployment Window 2026-03-16 → 2026-04-13")
        print("=" * 60)

        from seeds.seed_residents import seed_residents
        from seeds.seed_document_types import seed_document_types
        from seeds.seed_documents import seed_documents
        from seeds.seed_announcements import seed_announcements
        from seeds.seed_equipment import seed_equipment
        from seeds.seed_blotter import seed_blotter
        from seeds.seed_feedback import seed_feedback
        from seeds.seed_notifications import seed_notifications
        from seeds.seed_sms import seed_sms
        from seeds.seed_audit import seed_audit
        from seeds.seed_transactions import seed_transactions
        from seeds.seed_admin import seed_admin
        from seeds.seed_puroks import seed_puroks

        # ── ORDER MATTERS ─────────────────────────────
        seed_puroks(db)
        seed_residents(db)
        seed_document_types(db)   # REQUIRED FIRST
        seed_announcements(db)
        seed_blotter(db)
        seed_documents(db)
        seed_equipment(db)
        seed_feedback(db)
        seed_notifications(db)
        seed_sms(db)
        seed_audit(db)
        seed_admin(db)
        seed_transactions(db)

        print("\n✅  All seeds completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"\n❌  Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_all()