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

from app.models.document import DocumentType


def seed_document_types(db):
    print("\n[document_types] Seeding document types …")

    existing = db.query(DocumentType).count()
    if existing > 0:
        print(f"  ↳ Skipped — {existing} document types already exist.")
        return

    docs = [
        # ── Certificate of Indigency ──────────────────────────────────
        DocumentType(
            doctype_name="Certificate of Indigency",
            price=0,
            is_available=True,
            file=None,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name", "type": "text",   "required": True,  "autofill": True, "source": "full_name"},
                {"name": "age",       "label": "Age",       "type": "number", "required": True,  "autofill": True, "source": "age"},
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
        DocumentType(
            doctype_name="Barangay Clearance",
            price=50,
            is_available=True,
            file=None,
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
        DocumentType(
            doctype_name="Barangay Clearance w/ Good Moral",
            price=50,
            is_available=True,
            file=None,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",         "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "house_no",  "label": "House No.",         "type": "number", "required": True, "autofill": True, "source": "house_no"},
                {"name": "yr_res",    "label": "Years of Residency","type": "number", "required": True, "autofill": True, "source": "years_residency"},
                {"name": "purpose",   "label": "Purpose",           "type": "select", "required": True,
                 "options": [
                     "Employment",
                     "Bank Account",
                     "LTOPF",
                 ]},
            ]
        ),

        # ── Clearance for Construction ────────────────────────────────
        DocumentType(
            doctype_name="Clearance for Construction",
            price=100,
            is_available=True,
            file=None,
            is_id_application=False,
            fields=[
                {"name": "full_name",     "label": "Full Name", "type": "text", "required": True, "autofill": True,  "source": "full_name"},
                {"name": "address",       "label": "Address",   "type": "text", "required": True, "autofill": True,  "source": "full_address"},
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
        DocumentType(
            doctype_name="PWD/Senior/Solo Parent",
            price=0,
            is_available=True,
            file=None,
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
        DocumentType(
            doctype_name="1st Time Job Seeker",
            price=0,
            is_available=True,
            file=None,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",         "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "house_no",  "label": "House No.",         "type": "number", "required": True, "autofill": True, "source": "house_no"},
                {"name": "age",       "label": "Age",               "type": "number", "required": True, "autofill": True, "source": "age"},
                {"name": "purok",     "label": "Purok",             "type": "text",   "required": True, "autofill": True, "source": "purok_name"},
                {"name": "brgy",      "label": "Barangay",          "type": "text",   "required": True, "autofill": True, "source": "barangay"},
                {"name": "city",      "label": "City",              "type": "text",   "required": True, "autofill": True, "source": "municipality"},
                {"name": "prov",      "label": "Province",          "type": "text",   "required": True, "autofill": True, "source": "province"},
                {"name": "yr_res",    "label": "Years of Residency","type": "number", "required": True, "autofill": True, "source": "years_residency"},
            ]
        ),

        # ── Certificate of Residency ──────────────────────────────────
        DocumentType(
            doctype_name="Certificate of Residency",
            price=30,
            is_available=True,
            file=None,
            is_id_application=False,
            fields=[
                {"name": "full_name", "label": "Full Name",         "type": "text",   "required": True, "autofill": True, "source": "full_name"},
                {"name": "house_no",  "label": "House No.",         "type": "number", "required": True, "autofill": True, "source": "house_no"},
                {"name": "yr_res",    "label": "Years of Residency","type": "number", "required": True, "autofill": True, "source": "years_residency"},
                {"name": "purpose",   "label": "Purpose",           "type": "text",   "required": True},
            ]
        ),
    ]

    db.add_all(docs)
    db.commit()

    print(f"  ↳ Inserted {len(docs)} document types.")