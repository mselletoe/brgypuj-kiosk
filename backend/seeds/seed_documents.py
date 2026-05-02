"""
seeds/seed_documents.py

Seeds document requests with realistic status progressions
(Pending → Approved → Ready → Released, or Rejected).

PDF generation is done inline during seeding for ALL requests whose
DocumentType has a template (doc_type.file is not None/empty),
regardless of status — including Pending and Rejected.

Date faking:
    form_data always contains backdated date_today / issued_date / day /
    month / year keys matching requested_at, so PDF templates render the
    correct fake date regardless of which variable they reference.
    freezegun is used as an additional safety net when calling
    _generate_pdf_from_template so that any datetime.now() call inside
    the service is also frozen to requested_at.

Resident restriction:
    Only the 31 residents listed in TRANSACTION_RESIDENTS are used as
    requestors. These are the real residents from the source data who
    actually made document/equipment transactions.
"""

import random
from datetime import datetime, date
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, progression, DEPLOY_START, DEPLOY_END

from app.models.document import DocumentType, DocumentRequest
from app.models.resident import Resident, ResidentRFID


# ─────────────────────────────────────────────────────────────
# Residents allowed to appear in document transactions.
# Stored as (last_name, first_name) — matched case-insensitively
# against the Resident table after seeding.
# ─────────────────────────────────────────────────────────────

TRANSACTION_RESIDENTS = [
    ("Vibandor",   "Mylene"),
    ("Angcaya",    "Joana"),
    ("Delarmino",  "Chariel Althea"),
    ("Bataclan",   "Jenna Rose"),
    ("Angcaya",    "Ma."),           # MA. MONICA YINLEY — matched by first token
    ("Dela Rea",   "Justine Carl"),
    ("Jamon",      "Alliah Mae"),
    ("Plaganas",   "Maria Aleth"),
    ("Gutierrez",  "Gillian Lou"),
    ("Bayas",      "Allister Marvin"),
    ("Angcaya",    "Micah Angelie"),
    ("Cruz",       "Kenjie Ryle"),
    ("Sipat",      "Marife"),
    ("Ramos",      "Naomi Rose"),
    ("Ramos",      "Winona Kylie"),
    ("Barrera",    "Lourella"),
    ("Dela Rea",   "Kristal Joy"),
    ("Panganiban", "Arvin"),
    ("Dela Rea",   "Carissa Mae"),
    ("Dimayuga",   "Ghia Larize"),
    ("Sumagui",    "Emil"),
    ("Sumagui",    "Niel"),
    ("Sumagui",    "Emmanuel"),
    ("San Martin", "Bobby"),
    ("Fresco",     "Veronica Anne"),
    ("San Martin", "Franco"),
    ("Mora",       "Mary Joy"),
    ("Madera",     "Aubrey Rose"),
    ("Bayot",      "Rochelle Ann"),
    ("Villamor",   "Keith Beau Allen"),
    ("Ambion",     "Johanne Alecs"),
]


def _get_transaction_residents(db: Session) -> list:
    """
    Return the subset of Resident ORM objects that match TRANSACTION_RESIDENTS.
    Matching is done by last_name (exact, title-case) and the start of first_name
    (covers compound first names like 'Ma. Monica Yinley').
    Only residents with an active RFID card are included — consistent with how
    the kiosk authenticates requestors.
    """
    all_residents = (
        db.query(Resident)
        .join(Resident.rfids)
        .filter(ResidentRFID.is_active == True)
        .all()
    )

    matched = []
    for last, first_start in TRANSACTION_RESIDENTS:
        last_norm  = last.strip().lower()
        first_norm = first_start.strip().lower()
        for r in all_residents:
            if (
                r.last_name.strip().lower() == last_norm
                and r.first_name.strip().lower().startswith(first_norm)
            ):
                matched.append(r)
                break  # one match per entry is enough

    if not matched:
        raise RuntimeError(
            "No transaction-eligible residents found. "
            "Run seed_residents first and make sure RFID cards are assigned."
        )

    return matched


# ── Helpers ──────────────────────────────────────────────────────

def _ordinal(day: int) -> str:
    if 10 <= day % 100 <= 20:
        return f"{day}th"
    return f"{day}{({1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th'))}"


def _fake_date_fields(dt: datetime) -> dict:
    return {
        "date_today":  dt.strftime("%B %d, %Y"),
        "day":         _ordinal(dt.day),
        "month":       dt.strftime("%B"),
        "year":        str(dt.year),
        "issued_date": dt.strftime("%B %d, %Y"),
    }


def _sample_form_data(doctype_name: str, resident, issued_at: datetime) -> dict:
    full_name = f"{resident.first_name} {resident.middle_name or ''} {resident.last_name}".strip()
    age       = (date.today().year - resident.birthdate.year) if resident.birthdate else ""
    yr_res    = str(random.randint(1, 20))

    base = {
        # ── Identity ─────────────────────────────
        "full_name":   full_name,
        "first_name":  resident.first_name,
        "middle_name": resident.middle_name or "",
        "last_name":   resident.last_name,
        "suffix":      resident.suffix or "",

        # ── Personal info ────────────────────────
        "gender":    resident.gender,
        "birthdate": resident.birthdate.strftime("%B %d, %Y") if resident.birthdate else "",
        "age":       age,

        # ── Contact ──────────────────────────────
        "email":        resident.email,
        "phone_number": resident.phone_number,

        # ── Address ──────────────────────────────
        "unit_blk_street": "",
        "house_no":        str(random.randint(1, 999)),
        "address":         f"Purok {random.randint(1, 5)}, Poblacion Uno, Amadeo, Cavite",
        "purok":           f"Purok {random.randint(1, 5)}",
        "purok_name":      f"Purok {random.randint(1, 5)}",
        "brgy":            "Poblacion Uno",
        "barangay":        "Poblacion Uno",
        "city":            "Amadeo",
        "municipality":    "Amadeo",
        "prov":            "Cavite",
        "province":        "Cavite",
        "region":          "Region IV-A",
        "full_address":    "Poblacion Uno, Amadeo, Cavite",

        # ── Residency ────────────────────────────
        "yr_res":               yr_res,
        "years_residency":      yr_res,
        "residency_start_date": resident.residency_start_date.strftime("%B %d, %Y"),

        # ── RFID ─────────────────────────────────
        "rfid_uid": getattr(resident.rfids[0], "rfid_uid", "") if resident.rfids else "",

        # ── Date fields ──────────────────────────
        "date_today":  issued_at.strftime("%B %d, %Y"),
        "day":         _ordinal(issued_at.day),
        "month":       issued_at.strftime("%B"),
        "year":        issued_at.strftime("%Y"),
        "issued_date": issued_at.strftime("%B %d, %Y"),
    }

    # ── Per-doctype specific fields ───────────────────────────────
    name = doctype_name.strip().lower()

    if "indigency" in name:
        base.update({
            "purpose": random.choice([
                "Subsistence Burial Assistance",
                "Medical Assistance",
                "Financial Assistance",
                "Educational Assistance",
            ]),
        })

    elif "clearance" in name and "good moral" not in name and "construction" not in name:
        base.update({
            "purpose": random.choice([
                "Employment",
                "Bank Account",
                "LTOPF",
            ]),
        })

    elif "good moral" in name:
        base.update({
            "purpose": random.choice([
                "Employment",
                "Bank Account",
                "LTOPF",
            ]),
        })

    elif "construction" in name:
        start   = issued_at.replace(day=1)
        end_day = random.randint(15, 28)
        base.update({
            "other_purpose": random.choice([
                "Construction of Commercial Bldg.",
                "Construction of Residential House",
                "Road Construction",
                "Electric Construction",
                "Water Supply Installation",
                "Construction of Perimeter Fence",
            ]),
            "month_day1": start.strftime("%B %d, %Y"),
            "month_day2": start.replace(day=end_day).strftime("%B %d, %Y"),
        })

    elif "pwd" in name or "senior" in name:
        base.update({
            "purpose": random.choice([
                "PWD",
                "Solo Parent",
                "Senior Citizen",
            ]),
        })

    elif "job seeker" in name:
        pass  # all fields already in base

    elif "residency" in name:
        base.update({
            "purpose": random.choice([
                "For school enrollment",
                "For employment purposes",
                "For bank requirements",
                "For NBI clearance",
            ]),
        })

    return base


def _generate_transaction_no(db: Session) -> str:
    while True:
        number         = random.randint(1000, 9999)
        transaction_no = f"DR-{number}"
        exists         = db.query(DocumentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


# ── Main seeder ──────────────────────────────────────────────────

def seed_documents(db: Session):
    print("\n[documents] Seeding document requests …")

    # Fetch ALL available doc types (with and without templates).
    all_doc_types      = db.query(DocumentType).filter(DocumentType.is_available == True).all()
    templated_doc_types    = [dt for dt in all_doc_types if dt.file]
    templateless_doc_types = [dt for dt in all_doc_types if not dt.file]  # noqa: F841

    if not all_doc_types:
        print("  ↳ No document types found — skipping.")
        return

    # ── Restrict to the 31 real transaction residents ─────────────
    try:
        residents = _get_transaction_residents(db)
    except RuntimeError as e:
        print(f"  ↳ {e}")
        return

    print(f"  ↳ Transaction-eligible residents loaded: {len(residents)}")

    if not templated_doc_types:
        print("  ⚠  No DocumentType rows have a template file (.file is NULL for all).")
        print("     All requests will be seeded WITHOUT a PDF.")
        print("     Upload .docx templates via the admin panel and re-run backdate_pdfs.py.")

    existing = db.query(DocumentRequest).count()
    if existing >= 20:
        print(f"  ↳ Skipped — {existing} document requests already exist.")
        return

    # Try to import PDF helpers once up-front.
    try:
        from app.services.document_service import _save_request_pdf  # noqa: F401
        save_pdf_available = True
    except ImportError:
        save_pdf_available = False
        print("  ⚠  _save_request_pdf not importable — PDFs won't be saved to disk.")

    try:
        from freezegun import freeze_time as _ft  # noqa: F401
        freeze_available = True
    except ImportError:
        freeze_available = False
        print("  ⚠  freezegun not installed — PDF dates won't be frozen to requested_at.")
        print("     Run: pip install freezegun")

    STATUS_WEIGHTS = [
        ("Released", 45),
        ("Approved",  15),
        ("Ready",     10),
        ("Rejected",  15),
        ("Pending",   15),
    ]
    statuses, weights = zip(*STATUS_WEIGHTS)

    TARGET   = 40
    counter  = 0
    pdf_ok   = 0
    pdf_skip = 0

    for _ in range(TARGET):
        resident     = random.choice(residents)
        requested_at = rand_dt()
        status       = random.choices(statuses, weights=weights, k=1)[0]

        # All statuses get a PDF as long as the doc type has a template.
        if templated_doc_types:
            doc_type = random.choice(templated_doc_types)
        else:
            doc_type = random.choice(all_doc_types)

        approved_at = None
        released_at = None
        if status in ("Approved", "Ready", "Released"):
            approved_at = progression(requested_at, 1, 8)
        if status in ("Ready", "Released"):
            released_at = progression(approved_at, 1, 24)

        payment_status = "unpaid"
        if status == "Released":
            payment_status = "paid"
        elif status in ("Approved", "Ready"):
            payment_status = random.choice(["paid", "unpaid"])

        form_data      = _sample_form_data(doc_type.doctype_name, resident, requested_at)
        transaction_no = _generate_transaction_no(db)

        req = DocumentRequest(
            transaction_no = transaction_no,
            resident_id    = resident.id,
            doctype_id     = doc_type.id,
            price          = doc_type.price,
            status         = status,
            payment_status = payment_status,
            form_data      = form_data,
            requested_at   = requested_at,
            notes          = None,
        )
        db.add(req)
        db.flush()  # populate req.id so transaction_no is safely usable

        # ── Generate and save PDF ─────────────────────────────────
        if doc_type.file and save_pdf_available:
            fake_dt_str = requested_at.strftime("%Y-%m-%d %H:%M:%S")
            try:
                from app.services.document_service import (
                    _generate_pdf_from_template,
                    _save_request_pdf,
                )
                if freeze_available:
                    from freezegun import freeze_time
                    with freeze_time(fake_dt_str):
                        pdf_bytes = _generate_pdf_from_template(
                            template_bytes=doc_type.file,
                            form_data=form_data,
                        )
                else:
                    pdf_bytes = _generate_pdf_from_template(
                        template_bytes=doc_type.file,
                        form_data=form_data,
                    )

                rel_path              = _save_request_pdf(transaction_no, pdf_bytes)
                req.request_file_path = rel_path
                pdf_ok += 1

            except Exception as e:
                print(f"  ⚠  PDF failed for {transaction_no}: {e}")
                pdf_skip += 1
        else:
            pdf_skip += 1

        counter += 1

    db.commit()
    print(f"  ↳ Inserted {counter} document requests.")
    print(f"  ↳ PDFs generated: {pdf_ok}  |  skipped (no template / error): {pdf_skip}")