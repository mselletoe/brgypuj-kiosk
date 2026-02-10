from app.db.session import SessionLocal
from app.models.document import DocumentType

DOCUMENT_TYPES = [
    {
        "doctype_name": "Barangay Clearance",
        "description": "Official clearance from barangay",
        "price": 50.00,
        "fields": [
            {"name": "purpose", "label": "Purpose", "type": "text"}
        ],
    },
    {
        "doctype_name": "Certificate of Residency",
        "description": "Proof of residency",
        "price": 30.00,
        "fields": [
            {"name": "years_residing", "label": "Years Residing", "type": "number"}
        ],
    },
]

def seed_document_types():
    db = SessionLocal()
    try:
        if db.query(DocumentType).count() > 0:
            print("✅ Document types already seeded")
            return

        for doc in DOCUMENT_TYPES:
            db.add(DocumentType(**doc))

        db.commit()
        print("🌱 Document types seeded")

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_document_types()