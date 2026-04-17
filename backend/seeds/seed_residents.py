"""
seeds/seed_residents.py

Residents seeded from real Poblacion Uno data.

Rules:
- 50 residents total, real names/birthdates/addresses from source list
- Residents 1–40  → assigned an RFID + Barangay ID
- Residents 41–50 → no RFID, no Barangay ID
- Barangay ID format: YEAR-XXXX  (randomised, non-consecutive)
"""

import random
import hashlib
from datetime import date, datetime, timezone
from sqlalchemy.orm import Session

from seeds.utils import rand_historic_date, DEPLOY_START, DEPLOY_END

from app.models.resident import Resident, Address, Purok, ResidentRFID
from app.models.barangayid import BarangayID


# ─────────────────────────────────────────────────────────────
# Source data (50 real residents from Poblacion 1 list)
# ─────────────────────────────────────────────────────────────

RESIDENTS_DATA = [
    # (full_name,                         birthdate,     street_address)
    ("JOEL A. ANGCAYA",                   "1972-08-21",  "084 A. Mabini St."),
    ("JOANA G. ANGCAYA",                  "1978-06-13",  "084 A. Mabini St."),
    ("MICAH ANGELIE G. ANGCAYA",          "2002-05-17",  "084 A. Mabini St."),
    ("MA. MONICA YINLEY G. ANGCAYA",      "2004-11-16",  "084 A. Mabini St."),
    ("MARY TIFFANY G. ANGCAYA",           "2009-05-08",  "084 A. Mabini St."),
    ("MICHAEL N. RAMOS",                  "1975-08-29",  "045 A. Mabini St."),
    ("NELSA C. RAMOS",                    "1977-11-17",  "045 A. Mabini St."),
    ("NAOMI ROSE C. RAMOS",               "1996-07-29",  "045 A. Mabini St."),
    ("WINONA KYLIE C. RAMOS",             "2002-09-15",  "045 A. Mabini St."),
    ("RANE NICOLO MANUEL C. RAMOS",       "2014-06-16",  "045 A. Mabini St."),
    ("ARVIN P. PANGANIBAN",               "1987-08-09",  "038B A. Mabini St."),
    ("GHIA LARIZE R. DIMAYUGA",           "1985-10-30",  "038B A. Mabini St."),
    ("ARHIA VICTORIA D. PANGANIBAN",      "2012-09-01",  "038B A. Mabini St."),
    ("CYNTHIA A. SAN MARTIN",             "1957-10-27",  "013 Bulboc Road"),
    ("BOBBY A. SAN MARTIN",               "1979-07-07",  "013 Bulboc Road"),
    ("FRANCO A. SAN MARTIN",              "1980-09-21",  "013 Bulboc Road"),
    ("JAN ALISON B. BAYOT",               "1988-07-12",  "120 A. Mabini St."),
    ("ROCHELLE ANN T. BAYOT",             "2000-07-18",  "120 A. Mabini St."),
    ("ROWN ALIZER T. BAYOT",              "2023-03-13",  "120 A. Mabini St."),
    ("JOMAR M. BARRERA",                  "1974-03-19",  "093 A. Mabini St."),
    ("MARIAN G. BARRERA",                 "1976-05-07",  "093 A. Mabini St."),
    ("LOURELLA G. BARRERA",               "2001-03-27",  "093 A. Mabini St."),
    ("LUCIANA L. BARRERA",                "1950-01-07",  "093 A. Mabini St."),
    ("GINA M. DELA REA",                  "1969-03-25",  "123 A. Mabini St."),
    ("KRISTAL JOY M. DELA REA",           "1989-02-04",  "123 A. Mabini St."),
    ("CARISSA MAE M. DELA REA",           "1996-09-29",  "123 A. Mabini St."),
    ("EMIL I. SUMAGUI",                   "1993-09-25",  "026 A. Mabini St."),
    ("NIEL I. SUMAGUI",                   "1995-10-09",  "026 A. Mabini St."),
    ("EMMANUEL I. SUMAGUI",               "1991-04-19",  "026 A. Mabini St."),
    ("JELYN MAE D. VIBANDOR",             "2001-08-19",  "002 Bypass Road"),
    ("MYLENE D. VIBANDOR",                "1979-11-09",  "002 Bypass Road"),
    ("CHARIEL ALTHEA A. DELARMINO",       "2002-06-04",  "115 A. Mabini St."),
    ("JENNA ROSE A. BATACLAN",            "2001-09-21",  "065 A. Mabini St."),
    ("JUSTINE CARL M. DELA REA",          "2001-10-18",  "123 A. Mabini St."),
    ("ALLIAH MAE B. JAMON",               "2004-08-20",  "054 A. Mabini St."),
    ("JOHANNE ALECS B. AMBION",           "2003-11-29",  "008 Bulboc Road"),
    ("KENJIE RYLE QUIRRO L. CRUZ",        "2003-09-06",  "128 A. Mabini St."),
    ("MARIFE A. SIPAT",                   "1985-05-25",  "005 By Pass Road"),
    ("VERONICA ANNE S. FRESCO",           "1995-04-10",  "005 By Pass Road"),
    ("MARY JOY B. MORA",                  "1982-11-06",  "008 By Pass Road"),
    # ── No RFID (residents 41–50) ──────────────────────────
    ("AUBREY ROSE M. MADERA",             "1986-12-01",  "009 By Pass Road"),
    ("JULITA A. OPEÑA",                   "1962-06-16",  "024 Bulboc Road"),
    ("MARY GRACE A. PANGANIBAN",          "1983-05-17",  "050 Bulboc Road"),
    ("MARIA JOSEFINA P. ABORDO",          "1970-11-22",  "025 Bulboc Road"),
    ("MERCY C. DELA REA",                 "1969-12-17",  "124B A. Mabini St."),
    ("CHRISTINA G. OPEÑA",                "1987-06-08",  "023 Bulboc Road"),
    ("JOI-ANN A. LIMBO",                  "1982-11-20",  "005 A. Mabini St."),
    ("LEA A. OPEÑA",                      "1990-03-05",  "037 Bulboc Road"),
    ("MIALYN D. CABALLERO",               "1974-02-22",  "053 Bulboc Road"),
    ("MARLYN L. CADAG",                   "1976-09-23",  "002 Bulboc Road"),
]

# 41 RFID numbers for residents 1–40 (index 0–39)
RFID_NUMBERS = [
    "1226449623", "0229509657", "229509657",  "1226497191", "1225987975",
    "0230705209", "0239376761", "0238558057", "0230632009", "0228850297",
    "0229175033", "0238980073", "0238873865", "0233336521", "0239417241",
    "0229235145", "0229576025", "1225961687", "0239104185", "0239784137",
    "0622493687", "0608404439", "0608357223", "1226499911", "0609630199",
    "1226283287", "1226783399", "1226651367", "1226715175", "1226568295",
    "0609606583", "0629191799", "1224966199", "0629866151", "0863533495",
    "0629471351", "0629932215", "0863367655", "0863698791", "0629412871",
]  # 40 entries — one per RFID resident

# Fixed PINs for RFID residents (index matches RFID_NUMBERS).
# These are deterministic so the PIN reference table always stays valid.
# Residents 41–50 (no RFID) get a random PIN since it's never used for auth.
RFID_PINS = [
    2824, 1409, 5506, 5012, 4657, 3286, 2679, 9935, 2424, 7912,
    1520, 1488, 2535, 4582, 4811, 9279, 1434, 4257, 9928, 7873,
    4611, 8359, 5557, 1106, 3615, 7924, 6574, 5552, 3547, 4527,
    6514, 2674, 2519, 7224, 2584, 6881, 6635, 5333, 1711, 8527,
]


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _parse_name(full_name: str) -> dict:
    """
    Splits 'FIRST [MIDDLE_INITIAL.] LAST' into components.
    Handles suffixes and compound last names (e.g. 'DELA REA').
    """
    parts = full_name.strip().split()
    last_name = parts[-1]

    # compound last names: DELA REA, SAN MARTIN, etc.
    compound_prefixes = {"DELA", "DE", "SAN", "DEL", "LOS", "LAS"}
    if len(parts) >= 2 and parts[-2].rstrip(".").upper() in compound_prefixes:
        last_name = f"{parts[-2]} {parts[-1]}"
        parts = parts[:-2]
    else:
        parts = parts[:-1]

    first_name = parts[0] if parts else ""
    # remaining parts between first and last are middle name(s)
    middle_parts = parts[1:] if len(parts) > 1 else []
    middle_name = " ".join(middle_parts) if middle_parts else None

    return {
        "first_name":  first_name.title(),
        "middle_name": middle_name.title() if middle_name else None,
        "last_name":   last_name.title(),
    }


def _infer_gender(first_name: str) -> str:
    female_indicators = {
        "JOANA", "MICAH", "MA.", "MARY", "NELSA", "NAOMI", "WINONA",
        "GHIA", "ARHIA", "CYNTHIA", "ROCHELLE", "ROWN", "MARIAN",
        "LOURELLA", "LUCIANA", "GINA", "KRISTAL", "CARISSA", "JELYN",
        "MYLENE", "CHARIEL", "JENNA", "ALLIAH", "MARIFE", "VERONICA",
        "AUBREY", "JULITA", "GRACE", "MARIA", "MERCY", "CHRISTINA",
        "JOI-ANN", "LEA", "MIALYN", "MARLYN",
    }
    fn_upper = first_name.upper().strip()
    return "female" if fn_upper in female_indicators else "male"


def _hash_pin(pin: str) -> str:
    import hashlib
    return hashlib.sha256(pin.encode()).hexdigest()


def _rand_brgy_id_number(year: int, used: set) -> str:
    """Generate a unique non-consecutive YEAR-XXXX style ID."""
    while True:
        seq = random.randint(1000, 9999)
        candidate = f"{year}-{seq}"
        if candidate not in used:
            used.add(candidate)
            return candidate


def _reg_date(birthdate: date) -> date:
    """
    Derive a plausible registration date:
    - For adults (18+): random historic date 1–10 years ago
    - For minors: shortly after birth or within deployment window
    """
    today = DEPLOY_START.date()
    age_days = (today - birthdate).days

    if age_days >= 18 * 365:
        return rand_historic_date(years_ago_min=1, years_ago_max=10)
    else:
        # register during deployment window
        from seeds.utils import rand_date
        return rand_date(DEPLOY_START.date(), DEPLOY_END.date())


def _get_puroks(db: Session) -> list:
    puroks = db.query(Purok).all()
    if not puroks:
        raise RuntimeError("Run seed_puroks first — no Purok records found.")
    return puroks


# ─────────────────────────────────────────────────────────────
# Seeder
# ─────────────────────────────────────────────────────────────

def seed_residents(db: Session):
    print("\n[residents] Seeding residents …")

    existing = db.query(Resident).count()
    if existing >= 50:
        print(f"  ↳ Skipped — {existing} residents already exist.")
        return

    puroks = _get_puroks(db)
    used_brgy_ids: set = set()
    issue_year = DEPLOY_START.year   # 2026

    residents_created = []

    for idx, (full_name, bdate_str, street) in enumerate(RESIDENTS_DATA):
        has_rfid = idx < 40   # first 40 get RFID + Barangay ID

        name = _parse_name(full_name)
        gender = _infer_gender(full_name.split()[0])
        birthdate = date.fromisoformat(bdate_str)
        reg_date = _reg_date(birthdate)

        # Convert reg_date to datetime for models that expect datetime
        if isinstance(reg_date, date) and not isinstance(reg_date, datetime):
            reg_dt = datetime(reg_date.year, reg_date.month, reg_date.day,
                              random.randint(8, 16), random.randint(0, 59), 0,
                              tzinfo=timezone.utc)
        else:
            reg_dt = reg_date

        # ── 1. Resident ──────────────────────────────────────
        resident = Resident(
            last_name=name["last_name"],
            first_name=name["first_name"],
            middle_name=name["middle_name"],
            suffix=None,
            gender=gender,
            birthdate=birthdate,
            residency_start_date=reg_date if isinstance(reg_date, date) else reg_date.date(),
            email=f"{name['first_name'].lower()}.{name['last_name'].lower().replace(' ', '')}"
                  f"{random.randint(10, 999)}@gmail.com",
            phone_number=f"09{random.randint(100000000, 999999999)}",
            rfid_pin=_hash_pin(str(RFID_PINS[idx] if idx < 40 else random.randint(1000, 9999))),
            registered_at=reg_dt,
        )
        db.add(resident)
        db.flush()

        # ── 2. Address ───────────────────────────────────────
        purok = random.choice(puroks)
        address = Address(
            resident_id=resident.id,
            house_no_street=street,
            purok_id=purok.id,
            barangay="Poblacion Uno",
            municipality="Amadeo",
            province="Cavite",
            region="Region IV-A",
            is_current=True,
            created_at=reg_dt,
        )
        db.add(address)

        if has_rfid:
            # ── 3. RFID ──────────────────────────────────────
            rfid = ResidentRFID(
                resident_id=resident.id,
                rfid_uid=RFID_NUMBERS[idx],
                is_active=True,
                created_at=reg_dt,
            )
            db.add(rfid)
            db.flush()

            # ── 4. Barangay ID ───────────────────────────────
            brgy_id_number = _rand_brgy_id_number(issue_year, used_brgy_ids)
            brgy_id = BarangayID(
                brgy_id_number=brgy_id_number,
                resident_id=resident.id,
                rfid_id=rfid.id,
                issued_date=reg_dt.date() if isinstance(reg_dt, datetime) else reg_dt,
                expiration_date=None,
                is_active=True,
                created_at=reg_dt,
            )
            db.add(brgy_id)

        residents_created.append(resident)

    db.commit()

    rfid_count = sum(1 for i in range(len(RESIDENTS_DATA)) if i < 40)
    no_rfid_count = len(RESIDENTS_DATA) - rfid_count

    print(f"  ↳ Inserted {len(residents_created)} residents:")
    print(f"      • {rfid_count} with RFID + Barangay ID")
    print(f"      • {no_rfid_count} without RFID")

    return residents_created