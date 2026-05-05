"""
seeds/backdate_pdfs.py

Backfills missing PDF files for both regular document requests and
Barangay ID applications.

Notes:
    - Regular document requests use req.doctype.file.
    - Barangay ID applications are intentionally stored with doctype_id=None,
      so they do not have req.doctype. For those rows, this script uses the
      dedicated DocumentType marked is_id_application=True as the template.
    - PDFs are generated under freezegun using each request's requested_at value
      so generated date placeholders remain backdated.
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin7890@db:5432/kioskdb",
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


def _is_id_application(req) -> bool:
    """Return True for seeded Barangay ID application DocumentRequest rows."""
    form_data = req.form_data or {}
    return (
        req.doctype_id is None
        and (
            form_data.get("request_type") == "ID Application"
            or str(req.transaction_no or "").startswith("ID-")
        )
    )


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
        id_doc_type = (
            db.query(DocumentType)
            .filter(
                DocumentType.is_available == True,
                DocumentType.is_id_application == True,
            )
            .first()
        )

        requests = (
            db.query(DocumentRequest)
            .filter(DocumentRequest.request_file_path.is_(None))
            .all()
        )

        print(f"Found {len(requests)} request(s) missing PDFs.")

        patched = skipped = failed = 0
        id_patched = regular_patched = 0

        for req in requests:
            is_id = _is_id_application(req)
            doc_type = id_doc_type if is_id else req.doctype

            if not doc_type:
                skipped += 1
                kind = "ID template" if is_id else "document type"
                print(f"  ⚠  {req.transaction_no}: skipped — no {kind} found")
                continue

            if not doc_type.file:
                skipped += 1
                print(
                    f"  ⚠  {req.transaction_no}: skipped — no template for "
                    f"{doc_type.doctype_name}"
                )
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
                if is_id:
                    id_patched += 1
                else:
                    regular_patched += 1

                print(f"  ✅ {req.transaction_no} → {fake_dt_str}")

            except Exception as e:
                failed += 1
                print(f"  ❌ {req.transaction_no}: {e}")

        db.commit()

        print(
            "\nDone — "
            f"patched: {patched} "
            f"(ID: {id_patched}, regular: {regular_patched}) | "
            f"skipped: {skipped} | failed: {failed}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    run()
