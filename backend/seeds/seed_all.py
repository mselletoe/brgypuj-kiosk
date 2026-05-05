"""
seeds/seed_all.py

Master seeder — runs all seed modules in dependency order.
Deployment window: 2026-03-16 → 2026-04-13
"""

import os
import sys
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
        print("=" * 65)
        print("  BARANGAY SEED — Deployment Window 2026-03-16 → 2026-04-13")
        print("=" * 65)

        from seeds.seed_puroks         import seed_puroks
        from seeds.seed_residents      import seed_residents
        from seeds.seed_document_types import seed_document_types
        from seeds.seed_admin          import seed_admin
        from seeds.seed_announcements  import seed_announcements
        from seeds.seed_blotter        import seed_blotter
        from seeds.seed_documents      import seed_documents
        from seeds.seed_equipment      import seed_equipment
        from seeds.seed_feedback       import seed_feedback
        from seeds.seed_notifications  import seed_notifications
        from seeds.seed_sms            import seed_sms
        from seeds.seed_audit          import seed_audit
        from seeds.seed_transactions   import seed_transactions

        # ── ORDER MATTERS ─────────────────────────────────────────────
        seed_puroks(db)           # 1. Puroks must exist before residents
        seed_residents(db)        # 2. All 55 residents with backdated reg_at
        seed_document_types(db)   # 3. DocTypes before any requests
        seed_admin(db)            # 4. Admin accounts (linked to residents)
        seed_announcements(db)    # 5. Announcements (no dependencies)
        seed_blotter(db)          # 7. Blotter (uses non-transaction residents)
        seed_documents(db)        # 8. Document requests (needs residents + doctypes)
        seed_equipment(db)        # 10. Inventory + borrow requests
        seed_feedback(db)         # 11. Feedback (needs residents)
        seed_notifications(db)    # 12. Notifications (reads from prev tables)
        seed_sms(db)              # 13. SMS logs
        seed_audit(db)            # 14. Audit logs
        seed_transactions(db)     # 15. Financial transactions (reads Released records)

        # ── Backfill PDFs for Released/Approved requests ───────────────
        print("\n[backdate_pdfs] Backfilling missing PDFs …")
        _run_backdate_pdfs(db)

        print("\n✅  All seeds completed successfully.")

    except Exception as e:
        db.rollback()
        print(f"\n❌  Seed failed: {e}")
        raise
    finally:
        db.close()


def _run_backdate_pdfs(db):
    try:
        from freezegun import freeze_time
    except ImportError:
        print("  ⚠  freezegun not installed — skipping PDF backfill.")
        print("     Run: pip install freezegun")
        return

    try:
        from app.models.document import DocumentRequest
        from app.services.document_service import (
            _generate_pdf_from_template,
            _save_request_pdf,
        )
    except ImportError as e:
        print(f"  ⚠  Could not import required modules: {e}")
        return

    requests = (
        db.query(DocumentRequest)
        .filter(
            DocumentRequest.status.in_(["Approved", "Ready", "Released"]),
            DocumentRequest.request_file_path == None,
        )
        .all()
    )

    if not requests:
        print("  ↳ No missing PDFs — all requests already have files.")
        return

    print(f"  ↳ Found {len(requests)} request(s) without a PDF, generating now …")

    patched = skipped = failed = 0

    for req in requests:
        doc_type = req.doctype

        if not doc_type or not doc_type.file:
            skipped += 1
            continue

        fake_dt_str = req.requested_at.strftime("%Y-%m-%d %H:%M:%S")

        try:
            with freeze_time(fake_dt_str):
                pdf_bytes = _generate_pdf_from_template(
                    template_bytes=doc_type.file,
                    form_data=req.form_data or {},
                )

            rel_path = _save_request_pdf(req.transaction_no, pdf_bytes)
            req.request_file_path = rel_path
            patched += 1
            print(f"    ✅ {req.transaction_no} → {fake_dt_str}")

        except Exception as e:
            failed += 1
            print(f"    ❌ {req.transaction_no}: {e}")

    db.commit()
    print(f"  ↳ Backfilled: {patched} | skipped (no template): {skipped} | failed: {failed}")


if __name__ == "__main__":
    seed_all()