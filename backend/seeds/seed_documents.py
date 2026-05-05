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

ID Applications:
    Every transaction-eligible resident must have a completed (Released)
    ID application BEFORE they can use the kiosk. These are seeded first,
    using the actual survey dates collected on-site. The requested_at date
    is the survey date itself (or up to 3 days before), and the release
    date follows the Monday rule: if requested on Fri/Sat/Sun, the
    next Monday is the release date; otherwise release is the same day
    or next business day.
"""

import random
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, progression, DEPLOY_START, DEPLOY_END

from app.models.document import DocumentType, DocumentRequest
from app.models.barangayid import BarangayID
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
    ("Angcaya",    "Ma. Monica Yinley"),
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


# ─────────────────────────────────────────────────────────────
# Survey dates — the actual dates each resident filled out the
# on-site survey form. The ID application requested_at is set
# to this date (or up to 3 days before, randomly).
# Order matches TRANSACTION_RESIDENTS exactly.
# ─────────────────────────────────────────────────────────────

SURVEY_DATES = [
    date(2026, 3, 16),   # Vibandor, Mylene
    date(2026, 3, 16),   # Angcaya, Joana
    date(2026, 3, 16),   # Delarmino, Chariel Althea
    date(2026, 3, 16),   # Bataclan, Jenna Rose
    date(2026, 3, 17),   # Angcaya, Ma. Monica Yinley
    date(2026, 3, 20),   # Dela Rea, Justine Carl
    date(2026, 3, 20),   # Jamon, Alliah Mae
    date(2026, 3, 21),   # Plaganas, Maria Aleth
    date(2026, 3, 21),   # Gutierrez, Gillian Lou
    date(2026, 3, 23),   # Bayas, Allister Marvin
    date(2026, 3, 26),   # Angcaya, Micah Angelie
    date(2026, 3, 26),   # Cruz, Kenjie Ryle
    date(2026, 3, 26),   # Sipat, Marife
    date(2026, 3, 28),   # Ramos, Naomi Rose
    date(2026, 3, 28),   # Ramos, Winona Kylie
    date(2026, 3, 28),   # Barrera, Lourella
    date(2026, 3, 30),   # Dela Rea, Kristal Joy
    date(2026, 4,  1),   # Panganiban, Arvin
    date(2026, 4,  3),   # Dela Rea, Carissa Mae
    date(2026, 4,  3),   # Dimayuga, Ghia Larize
    date(2026, 4,  4),   # Sumagui, Emil
    date(2026, 4,  4),   # Sumagui, Niel
    date(2026, 4,  7),   # Sumagui, Emmanuel
    date(2026, 4,  8),   # San Martin, Bobby
    date(2026, 4, 10),   # Fresco, Veronica Anne
    date(2026, 4, 10),   # San Martin, Franco
    date(2026, 4, 10),   # Mora, Mary Joy
    date(2026, 4, 13),   # Madera, Aubrey Rose
    date(2026, 4, 15),   # Bayot, Rochelle Ann
    date(2026, 4, 18),   # Villamor, Keith Beau Allen
    date(2026, 4, 18),   # Ambion, Johanne Alecs
]


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

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


def _id_request_datetime(survey_date: date) -> datetime:
    """
    Pick a requested_at datetime: same day as survey or up to 3 days before,
    but never a weekend (Sat/Sun) if we can avoid it by shifting to Friday.
    Time is randomised to office hours.
    """
    days_back = random.randint(0, 3)
    chosen = survey_date - timedelta(days=days_back)
    # If we landed on a weekend, roll back to the previous Friday.
    if chosen.weekday() == 5:   # Saturday
        chosen -= timedelta(days=1)
    elif chosen.weekday() == 6:  # Sunday
        chosen -= timedelta(days=2)
    return datetime(
        chosen.year, chosen.month, chosen.day,
        random.randint(8, 16), random.randint(0, 59), 0,
    )


def _id_release_datetime(requested_at: datetime) -> datetime:
    """
    Release date rule:
      - Requested Mon–Thu → released same day or next weekday (same day preferred).
      - Requested Fri     → released next Monday.
      - Requested Sat/Sun → not possible (request is shifted to Fri by _id_request_datetime),
                            but guard included for safety → next Monday.
    Released time is always after the request time.
    """
    req_weekday = requested_at.weekday()  # 0=Mon … 6=Sun
    req_date    = requested_at.date()

    if req_weekday == 4:        # Friday → next Monday
        release_date = req_date + timedelta(days=3)
    elif req_weekday == 5:      # Saturday → next Monday (safety guard)
        release_date = req_date + timedelta(days=2)
    elif req_weekday == 6:      # Sunday  → next Monday (safety guard)
        release_date = req_date + timedelta(days=1)
    else:                       # Mon–Thu → same day
        release_date = req_date

    release_hour = random.randint(requested_at.hour + 1, 17)
    return datetime(
        release_date.year, release_date.month, release_date.day,
        min(release_hour, 17), random.randint(0, 59), 0,
    )


def _next_id_number(db: Session) -> str:
    from sqlalchemy import func
    max_val = db.query(func.max(BarangayID.brgy_id_number)).scalar()
    if max_val is None:
        next_num = 1
    else:
        try:
            next_num = int(max_val) + 1
        except (ValueError, TypeError):
            next_num = 1
    return str(next_num).zfill(5)


def _generate_id_transaction_no(db: Session) -> str:
    while True:
        number = random.randint(1000, 9999)
        tx_no  = f"ID-{number}"
        exists = db.query(DocumentRequest).filter_by(transaction_no=tx_no).first()
        if not exists:
            return tx_no


def _generate_doc_transaction_no(db: Session) -> str:
    while True:
        number         = random.randint(1000, 9999)
        transaction_no = f"DR-{number}"
        exists         = db.query(DocumentRequest).filter_by(transaction_no=transaction_no).first()
        if not exists:
            return transaction_no


def _get_transaction_residents(db: Session) -> list:
    """
    Return the 31 Resident ORM objects matched to TRANSACTION_RESIDENTS,
    in the same order, so they align with SURVEY_DATES by index.

    Matching strategy:
      - last_name  : exact, case-insensitive
      - first_name : match only the FIRST TOKEN of the TRANSACTION_RESIDENTS
                     entry against the DB first_name field, because _parse_name
                     in seed_residents.py stores only the first word as
                     first_name (e.g. "Chariel Althea" → first_name="Chariel").
      - When multiple residents share the same last + first token (e.g. three
        Sumaguis all have unique first tokens so this is fine), the first DB
        hit is used — consistent with the original behaviour.

    Only residents with at least one active RFID card are considered.
    None entries are preserved in the returned list to keep index alignment
    with SURVEY_DATES.
    """
    all_residents = (
        db.query(Resident)
        .join(Resident.rfids)
        .filter(ResidentRFID.is_active == True)
        .all()
    )

    matched = []
    for last, first_start in TRANSACTION_RESIDENTS:
        last_norm        = last.strip().lower()
        # Use only the first word of the first_start entry for matching,
        # because that is all _parse_name puts into Resident.first_name.
        first_token_norm = first_start.strip().lower().split()[0]
        found = None
        for r in all_residents:
            if (
                r.last_name.strip().lower() == last_norm
                and r.first_name.strip().lower().split()[0] == first_token_norm
            ):
                found = r
                break
        matched.append(found)  # None preserved to keep index alignment

    missing = [TRANSACTION_RESIDENTS[i] for i, v in enumerate(matched) if v is None]
    if missing:
        names = ", ".join(f"{l} {f}" for l, f in missing)
        print(f"  ⚠  Could not match {len(missing)} resident(s): {names}")

    valid = [r for r in matched if r is not None]
    if not valid:
        raise RuntimeError(
            "No transaction-eligible residents found. "
            "Run seed_residents first and make sure RFID cards are assigned."
        )

    return matched  # length == 31, may contain None for unmatched entries


def _sample_id_form_data(resident, requested_at: datetime, brgy_id_number: str) -> dict:
    """Build the form_data payload for an ID application request."""
    active_rfid = next((r for r in resident.rfids if r.is_active), None)
    display_rfid = active_rfid.rfid_uid if active_rfid else "Guest Mode"

    full_address = f"Poblacion Uno, Amadeo, Cavite"

    return {
        # ── ID application meta keys ──────────────────────────
        "request_type":    "ID Application",
        "request_for_id":  resident.id,
        "request_for_name": f"{resident.first_name} {resident.last_name}",
        "session_rfid":    display_rfid,
        "requested_date":  requested_at.isoformat(),
        "use_manual_data": False,
        "brgy_id_number":  brgy_id_number,

        # ── ID Application fields (from seed_document_types) ──
        "last_name":           resident.last_name,
        "first_name":          resident.first_name,
        "middle_name":         resident.middle_name or "",
        "birthdate":           resident.birthdate.strftime("%B %d, %Y") if resident.birthdate else "",
        "address":             full_address,
        "phone_number":        resident.phone_number or "",
        "contact_person_name": "Maria Santos",
        "contact_person_no":   "09171234567",

        # ── Date fields for template rendering ────────────────
        **_fake_date_fields(requested_at),
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


# ── Main seeder ──────────────────────────────────────────────────

def seed_documents(db: Session):
    print("\n[documents] Seeding document requests …")

    # ── Try to import PDF helpers once up-front ────────────────
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

    # ── Restrict to the 31 real transaction residents ──────────
    try:
        residents = _get_transaction_residents(db)
    except RuntimeError as e:
        print(f"  ↳ {e}")
        return

    valid_count = sum(1 for r in residents if r is not None)
    print(f"  ↳ Transaction-eligible residents loaded: {valid_count}/{len(residents)}")

    # ── Fetch doc types ────────────────────────────────────────
    # Regular document requests use normal document types.
    # ID applications intentionally keep doctype_id=NULL, but they still
    # use the dedicated is_id_application DocumentType as their PDF template.
    id_doc_type = (
        db.query(DocumentType)
        .filter(
            DocumentType.is_available == True,
            DocumentType.is_id_application == True,
        )
        .first()
    )

    all_doc_types = (
        db.query(DocumentType)
        .filter(
            DocumentType.is_available == True,
            DocumentType.is_id_application == False,
        )
        .all()
    )
    templated_doc_types    = [dt for dt in all_doc_types if dt.file]
    templateless_doc_types = [dt for dt in all_doc_types if not dt.file]  # noqa: F841

    if not id_doc_type:
        print("  ⚠  No ID application DocumentType found — ID PDFs will be skipped.")
    elif not id_doc_type.file:
        print("  ⚠  ID application DocumentType has no template file — ID PDFs will be skipped.")

    if not all_doc_types:
        print("  ↳ No document types found — skipping document requests.")
    if not templated_doc_types:
        print("  ⚠  No regular DocumentType rows have a template file (.file is NULL for all).")
        print("     Regular requests will be seeded WITHOUT a PDF.")
        print("     Upload .docx templates via the admin panel and re-run backdate_pdfs.py.")

    # ──────────────────────────────────────────────────────────────
    # BLOCK 1 — Seed completed ID applications (one per resident)
    # ──────────────────────────────────────────────────────────────

    existing_ids = (
        db.query(DocumentRequest)
        .filter(DocumentRequest.doctype_id.is_(None))
        .count()
    )

    if existing_ids >= len(TRANSACTION_RESIDENTS):
        print(f"  ↳ ID applications skipped — {existing_ids} already exist.")
    else:
        print(f"\n  [ID applications] Seeding {len(TRANSACTION_RESIDENTS)} released ID applications …")
        id_ok       = 0
        id_skip     = 0
        id_pdf_ok   = 0
        id_pdf_skip = 0
        id_pdf_fail = 0

        for idx, (resident, survey_date) in enumerate(zip(residents, SURVEY_DATES)):
            if resident is None:
                print(f"    ⚠  Skipping index {idx} — resident not found in DB.")
                id_skip += 1
                continue

            requested_at = _id_request_datetime(survey_date)
            released_at  = _id_release_datetime(requested_at)
            brgy_id_number = _next_id_number(db)
            tx_no          = _generate_id_transaction_no(db)
            form_data      = _sample_id_form_data(resident, requested_at, brgy_id_number)

            req = DocumentRequest(
                transaction_no = tx_no,
                resident_id    = resident.id,
                doctype_id     = None,          # ID applications always have NULL doctype_id
                price          = 100,
                status         = "Released",
                payment_status = "paid",
                form_data      = form_data,
                requested_at   = requested_at,
                notes          = None,
            )
            db.add(req)
            db.flush()  # populate req.id

            # Generate and save the Barangay ID PDF.
            # The request keeps doctype_id=NULL for the dedicated ID flow, so
            # we use id_doc_type.file directly instead of req.doctype.
            if id_doc_type and id_doc_type.file and save_pdf_available:
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
                                template_bytes=id_doc_type.file,
                                form_data=form_data,
                            )
                    else:
                        pdf_bytes = _generate_pdf_from_template(
                            template_bytes=id_doc_type.file,
                            form_data=form_data,
                        )

                    rel_path              = _save_request_pdf(tx_no, pdf_bytes)
                    req.request_file_path = rel_path
                    id_pdf_ok += 1

                except Exception as e:
                    print(f"    ⚠  ID PDF failed for {tx_no}: {e}")
                    id_pdf_fail += 1
            else:
                id_pdf_skip += 1

            # BarangayID row — active, linked to resident's RFID
            active_rfid = next((r for r in resident.rfids if r.is_active), None)
            barangay_id_row = BarangayID(
                resident_id     = resident.id,
                rfid_id         = active_rfid.id if active_rfid else None,
                request_id      = req.id,
                brgy_id_number  = brgy_id_number,
                issued_date     = released_at.date(),
                expiration_date = active_rfid.expiration_date if active_rfid else None,
                is_active       = True,
            )
            db.add(barangay_id_row)
            id_ok += 1

        db.commit()
        print(f"    ↳ ID applications inserted: {id_ok}  |  skipped: {id_skip}")
        print(f"    ↳ ID PDFs generated: {id_pdf_ok}  |  skipped: {id_pdf_skip}  |  failed: {id_pdf_fail}")

    # ──────────────────────────────────────────────────────────────
    # BLOCK 2 — Seed regular document requests
    # ──────────────────────────────────────────────────────────────

    existing_docs = (
        db.query(DocumentRequest)
        .filter(DocumentRequest.doctype_id.isnot(None))
        .count()
    )

    if existing_docs >= 20:
        print(f"  ↳ Document requests skipped — {existing_docs} already exist.")
        return

    if not all_doc_types:
        print("  ↳ No document types available — skipping regular document requests.")
        return

    print(f"\n  [document requests] Seeding regular document requests …")

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

    valid_residents = [r for r in residents if r is not None]

    for _ in range(TARGET):
        resident     = random.choice(valid_residents)
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
        transaction_no = _generate_doc_transaction_no(db)

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
        db.flush()

        # ── Generate and save PDF ─────────────────────────────
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
    print(f"    ↳ Inserted {counter} document requests.")
    print(f"    ↳ PDFs generated: {pdf_ok}  |  skipped (no template / error): {pdf_skip}")