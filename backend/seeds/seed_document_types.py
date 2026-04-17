# seeds/seed_document_types.py
#
# Field schema per entry:
#   name      – template placeholder key
#   label     – display label shown to the user
#   type      – "text" | "number" | "date" | "select"
#   required  – whether the field must be filled before submitting
#   autofill  – (optional) True = pre-populated from resident profile; user cannot edit
#   source    – resident model attribute to pull the autofill value from
#   options   – (select only) list of allowed values
#
# Templates:
#   Place .docx files in: seeds/templates/
#   Naming convention:    seeds/templates/<doctype_name>.docx
#   Example:              seeds/templates/Barangay Clearance.docx
#
#   If a template file is found, it will be stored in the DB (doc_type.file)
#   and PDFs will be auto-generated during seed_documents.

from pathlib import Path
from app.models.document import DocumentType

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"


def _load_template(doctype_name: str) -> bytes | None:
    """Load a .docx template file for the given document type name, if it exists."""
    path = TEMPLATES_DIR / f"{doctype_name}.docx"
    if path.exists():
        print(f"    📄 Template loaded: {path.name}")
        return path.read_bytes()
    print(f"    ⚠  No template found for: {doctype_name} (expected: {path.name})")
    return None


def seed_document_types(db):
    print("\n[document_types] Seeding document types …")
    print(f"  ↳ Looking for templates in: {TEMPLATES_DIR}")

    existing = db.query(DocumentType).count()
    if existing > 0:
        print(f"  ↳ Skipped — {existing} document types already exist.")
        return

    TYPES = [
        # ── Certificate of Indigency ──────────────────────────────────
        dict(
            doctype_name="Certificate of Indigency",
            price=0,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name", "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "age",       "label": "Age",       "type": "number", "required": True, "autofill": True, "source": "age"},
                {"name": "purpose",   "label": "Purpose",   "type": "select", "required": True,
                 "options": [
                     "Subsistence Burial Assistance",
                     "Medical Assistance",
                     "Financial Assistance",
                     "Educational Assistance",
                 ]},
            ]
        ),

        # ── Barangay Clearance ────────────────────────────────────────
        dict(
            doctype_name="Barangay Clearance",
            price=50,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name", "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "purpose",   "label": "Purpose",   "type": "select", "required": True,
                 "options": [
                     "Employment",
                     "Bank Account",
                     "LTOPF",
                 ]},
            ]
        ),

        # ── Barangay Clearance w/ Good Moral ──────────────────────────
        dict(
            doctype_name="Barangay Clearance w Good Moral",
            price=50,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",          "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "house_no",  "label": "House No.",          "type": "number", "required": True, "autofill": True, "source": "house_no"},
                {"name": "yr_res",    "label": "Years of Residency", "type": "number", "required": True, "autofill": True, "source": "years_residency"},
                {"name": "purpose",   "label": "Purpose",            "type": "select", "required": True,
                 "options": [
                     "Employment",
                     "Bank Account",
                     "LTOPF",
                 ]},
            ]
        ),

        # ── Clearance for Construction ────────────────────────────────
        dict(
            doctype_name="Clearance for Construction",
            price=100,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name",     "label": "Full Name", "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "address",       "label": "Address",   "type": "text",   "required": True, "autofill": True, "source": "full_address"},
                {"name": "other_purpose", "label": "Purpose",   "type": "select", "required": True,
                 "options": [
                     "Construction of Commercial Bldg.",
                     "Construction of Residential House",
                     "Road Construction",
                     "Electric Construction",
                     "Water Supply Installation",
                     "Construction of Perimeter Fence",
                 ]},
                {"name": "month_day1", "label": "From", "type": "date", "required": True},
                {"name": "month_day2", "label": "To",   "type": "date", "required": True},
            ]
        ),

        # ── PWD / Senior / Solo Parent ────────────────────────────────
        dict(
            doctype_name="PWD_Senior_Solo_Parent",
            price=0,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",          "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "address",   "label": "Address",            "type": "text",   "required": True, "autofill": True, "source": "full_address"},
                {"name": "age",       "label": "Age",                "type": "number", "required": True, "autofill": True, "source": "age"},
                {"name": "yr_res",    "label": "Years of Residency", "type": "number", "required": True, "autofill": True, "source": "years_residency"},
                {"name": "purpose",   "label": "Purpose",            "type": "select", "required": True,
                 "options": [
                     "PWD",
                     "Solo Parent",
                     "Senior Citizen",
                 ]},
            ]
        ),

        # ── 1st Time Job Seeker ───────────────────────────────────────
        dict(
            doctype_name="1st Time Job Seeker",
            price=0,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",          "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "house_no",  "label": "House No.",          "type": "number", "required": True, "autofill": True, "source": "house_no"},
                {"name": "age",       "label": "Age",                "type": "number", "required": True, "autofill": True, "source": "age"},
                {"name": "purok",     "label": "Purok",              "type": "text",   "required": True, "autofill": True, "source": "purok_name"},
                {"name": "brgy",      "label": "Barangay",           "type": "text",   "required": True, "autofill": True, "source": "barangay"},
                {"name": "city",      "label": "City",               "type": "text",   "required": True, "autofill": True, "source": "municipality"},
                {"name": "prov",      "label": "Province",           "type": "text",   "required": True, "autofill": True, "source": "province"},
                {"name": "yr_res",    "label": "Years of Residency", "type": "number", "required": True, "autofill": True, "source": "years_residency"},
            ]
        ),

        # ── Certificate of Residency ──────────────────────────────────
        dict(
            doctype_name="Certificate of Residency",
            price=30,
            is_available=True,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",          "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "house_no",  "label": "House No.",          "type": "number", "required": True, "autofill": True, "source": "house_no"},
                {"name": "yr_res",    "label": "Years of Residency", "type": "number", "required": True, "autofill": True, "source": "years_residency"},
                {"name": "purpose",   "label": "Purpose",            "type": "text",   "required": True},
            ]
        ),
    ]

    docs = []
    templates_found = 0

    for t in TYPES:
        name = t["doctype_name"]
        template_bytes = _load_template(name)
        if template_bytes:
            templates_found += 1

        docs.append(DocumentType(
            doctype_name   = name,
            price          = t["price"],
            is_available   = t["is_available"],
            is_id_application = t["is_id_application"],
            fields         = t["fields"],
            file           = template_bytes,  # None if not found — that's fine
        ))

    db.add_all(docs)
    db.commit()

    print(f"  ↳ Inserted {len(docs)} document types ({templates_found} with templates).")
    if templates_found == 0:
        print("  ⚠  No templates loaded — PDFs will not be generated during seeding.")
        print("     Upload .docx files via the admin panel, then run: python -m seeds.backdate_pdfs")