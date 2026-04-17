"""
seeds/backdate_pdfs.py
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


def run():
    try:
        from freezegun import freeze_time
    except ImportError:
        print("❌ freezegun not installed. Run: pip install freezegun")
        sys.exit(1)

    from app.models.document import DocumentRequest, DocumentType
    from app.services.document_service import (
        _generate_pdf_from_template,
        _save_request_pdf,
    )

    db = SessionLocal()

    try:
        requests = (
            db.query(DocumentRequest)
            .filter(
                DocumentRequest.status.in_(["Approved", "Ready", "Released"]),
                DocumentRequest.request_file_path == None  # IMPORTANT FIX
            )
            .all()
        )

        print(f"Found {len(requests)} requests to backdate PDFs.")

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
                print(f"  ✅ {req.transaction_no} → {fake_dt_str}")

            except Exception as e:
                failed += 1
                print(f"  ❌ {req.transaction_no}: {e}")

        db.commit()

        print(
            f"\nDone — patched: {patched} | skipped: {skipped} | failed: {failed}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    run()