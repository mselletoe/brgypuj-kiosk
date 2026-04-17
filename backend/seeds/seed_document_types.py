# seeds/seed_document_types.py

from app.models.document import DocumentType


def seed_document_types(db):
    print("\n[document_types] Seeding document types …")

    existing = db.query(DocumentType).count()
    if existing > 0:
        print(f"  ↳ Skipped — {existing} document types already exist.")
        return

    docs = [
        DocumentType(
            doctype_name="Barangay Clearance",
            price=50,
            is_available=True,
            file=None  # you can upload later via admin
        ),
        DocumentType(
            doctype_name="Certificate of Indigency",
            price=0,
            is_available=True,
            file=None
        ),
        DocumentType(
            doctype_name="Certificate of Residency",
            price=30,
            is_available=True,
            file=None
        ),
        DocumentType(
            doctype_name="Business Clearance",
            price=100,
            is_available=True,
            file=None
        ),
    ]

    db.add_all(docs)
    db.commit()

    print(f"  ↳ Inserted {len(docs)} document types.")