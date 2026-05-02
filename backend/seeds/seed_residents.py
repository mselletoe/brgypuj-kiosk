"""
seeds/seed_residents.py

Residents seeded from real Poblacion Uno data.

Rules:
- 54 residents total (original 50 + 4 new from Excel rows 52-55)
- Birthdates sourced directly from the Excel file (converted from Excel serial dates)
- Only Residents + Address records are created
- First 41 original residents are assigned real RFID card UIDs
- The 4 new residents (Plaganas, Gutierrez, Bayas, Villamor) also get RFID cards
- Residents WITHOUT an RFID card will appear in the approved applications list
  for future linking — they are intentionally left card-less

Transaction-eligible residents (those who appear in document/equipment requests):
    Vibandor Mylene, Angcaya Joana, Delarmino Chariel, Bataclan Jenna Rose,
    Angcaya Ma. Monica, Dela Rea Justine Carl, Jamon Alliah Mae,
    Plaganas Maria Aleth, Gutierrez Gillian Lou, Bayas Allister Marvin,
    Angcaya Micah Angelie, Cruz Kenjie Ryle, Sipat Marife,
    Ramos Naomi Rose, Ramos Winona Kylie, Barrera Lourella,
    Dela Rea Kristal Joy, Panganiban Arvin, Dela Rea Carissa Mae,
    Dimayuga Ghia Larize, Sumagui Emil, Sumagui Niel, Sumagui Emmanuel,
    San Martin Bobby, Fresco Veronica Anne, San Martin Franco,
    Mora Mary Joy, Madera Aubrey Rose, Bayot Rochelle Ann,
    Villamor Keith Beau Allen, Ambion Johanne Alecs
"""

import random
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from seeds.utils import rand_historic_date, DEPLOY_START, DEPLOY_END

from app.models.resident import Resident, Address, Purok, ResidentRFID
from app.services.systemconfig_service import get_config

# Must match the pwd_context in auth.py and resident_service.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─────────────────────────────────────────────────────────────
# Source data (54 residents — 50 original + 4 new from Excel)
# Birthdates verified from the Excel file serial date column.
# Mercy C. Dela Rea (row 45) had a #VALUE! error in Excel;
# original seed date 1969-12-17 is retained for her.
# ─────────────────────────────────────────────────────────────

RESIDENTS_DATA = [
    # (full_name, birthdate_iso, street)
    ("JOEL A. ANGCAYA",                "1972-08-21", "084 A. Mabini St."),
    ("JOANA G. ANGCAYA",               "1978-06-13", "084 A. Mabini St."),
    ("MICAH ANGELIE G. ANGCAYA",       "2002-05-17", "084 A. Mabini St."),
    ("MA. MONICA YINLEY G. ANGCAYA",   "2004-11-16", "084 A. Mabini St."),
    ("MARY TIFFANY G. ANGCAYA",        "2009-05-08", "084 A. Mabini St."),
    ("MICHAEL N. RAMOS",               "1975-08-29", "045 A. Mabini St."),
    ("NELSA C. RAMOS",                 "1977-11-17", "045 A. Mabini St."),
    ("NAOMI ROSE C. RAMOS",            "1996-07-29", "045 A. Mabini St."),
    ("WINONA KYLIE C. RAMOS",          "2002-09-15", "045 A. Mabini St."),
    ("RANE NICOLO MANUEL C. RAMOS",    "2014-06-16", "045 A. Mabini St."),
    ("ARVIN P. PANGANIBAN",            "1987-08-09", "038B A. Mabini St."),
    ("GHIA LARIZE R. DIMAYUGA",        "1985-10-30", "038B A. Mabini St."),
    ("ARHIA VICTORIA D. PANGANIBAN",   "2012-09-01", "038B A. Mabini St."),
    ("CYNTHIA A. SAN MARTIN",          "1957-10-27", "013 Bulboc Road"),
    ("BOBBY A. SAN MARTIN",            "1979-07-07", "013 Bulboc Road"),
    ("FRANCO A. SAN MARTIN",           "1980-09-21", "013 Bulboc Road"),
    ("JAN ALISON B. BAYOT",            "1988-07-12", "120 A. Mabini St."),
    ("ROCHELLE ANN T. BAYOT",          "2000-07-18", "120 A. Mabini St."),
    ("ROWN ALIZER T. BAYOT",           "2023-03-13", "120 A. Mabini St."),
    ("JOMAR M. BARRERA",               "1974-03-19", "093 A. Mabini St."),
    ("MARIAN G. BARRERA",              "1976-05-07", "093 A. Mabini St."),
    ("LOURELLA G. BARRERA",            "2001-03-27", "093 A. Mabini St."),
    ("LUCIANA L. BARRERA",             "1950-01-07", "093 A. Mabini St."),
    ("GINA M. DELA REA",               "1969-03-25", "123 A. Mabini St."),
    ("KRISTAL JOY M. DELA REA",        "1989-02-04", "123 A. Mabini St."),
    ("CARISSA MAE M. DELA REA",        "1996-09-29", "123 A. Mabini St."),
    ("EMIL I. SUMAGUI",                "1993-09-25", "026 A. Mabini St."),
    ("NIEL I. SUMAGUI",                "1995-10-09", "026 A. Mabini St."),
    ("EMMANUEL I. SUMAGUI",            "1991-04-19", "026 A. Mabini St."),
    ("JELYN MAE D. VIBANDOR",          "2001-08-19", "002 Bypass Road"),
    ("MYLENE D. VIBANDOR",             "1979-11-09", "002 Bypass Road"),
    ("CHARIEL ALTHEA A. DELARMINO",    "2002-06-04", "115 A. Mabini St."),
    ("JENNA ROSE A. BATACLAN",         "2001-09-21", "065 A. Mabini St."),
    ("JUSTINE CARL M. DELA REA",       "2001-10-18", "123 A. Mabini St."),
    ("ALLIAH MAE B. JAMON",            "2004-08-20", "054 A. Mabini St."),
    ("JOHANNE ALECS B. AMBION",        "2003-11-29", "008 Bulboc Road"),
    ("KENJIE RYLE QUIRRO L. CRUZ",     "2003-09-06", "128 A. Mabini St."),
    ("MARIFE A. SIPAT",                "1985-05-25", "005 By Pass Road"),
    ("VERONICA ANNE S. FRESCO",        "1995-04-10", "005 By Pass Road"),
    ("MARY JOY B. MORA",               "1982-11-06", "008 By Pass Road"),
    ("AUBREY ROSE M. MADERA",          "1986-12-01", "009 By Pass Road"),
    ("JULITA A. OPEÑA",                "1962-06-16", "024 Bulboc Road"),
    ("MARY GRACE A. PANGANIBAN",       "1983-05-17", "050 Bulboc Road"),
    ("MARIA JOSEFINA P. ABORDO",       "1970-11-22", "025 Bulboc Road"),
    ("MERCY C. DELA REA",              "1969-12-17", "124B A. Mabini St."),  # #VALUE! in Excel; original date kept
    ("CHRISTINA G. OPEÑA",             "1987-06-08", "023 Bulboc Road"),
    ("JOI-ANN A. LIMBO",               "1982-11-20", "005 A. Mabini St."),
    ("LEA A. OPEÑA",                   "1990-03-05", "037 Bulboc Road"),
    ("MIALYN D. CABALLERO",            "1974-02-22", "053 Bulboc Road"),
    ("MARLYN L. CADAG",                "1976-09-23", "002 Bulboc Road"),
    # ── 4 new residents from Excel rows 52-55 ──────────────────
    ("MARIA ALETH G. PLAGANAS",        "1989-08-14", "139 A. Mabini St."),
    ("GILLIAN LOU R. GUTIERREZ",       "1997-03-21", "152 A. Mabini St."),
    ("ALLISTER MARVIN G. BAYAS",       "2008-01-25", "139 A. Mabini St."),
    ("KEITH BEAU ALLEN Q. VILLAMOR",   "2004-01-12", "139 A. Mabini St."),
]


# ─────────────────────────────────────────────────────────────
# RFID UIDs
#
# Indices 0-40  → original 41 residents (unchanged)
# Indices 41-44 → 4 new residents (Plaganas, Gutierrez, Bayas, Villamor)
# Residents 42-49 (the original 9 without cards) remain card-less —
# they appear in the approved applications list for future linking.
# ─────────────────────────────────────────────────────────────

RFID_UIDS = [
    # ── original 41 ──────────────────────────────────────────
    "1226449623",   # 0  JOEL A. ANGCAYA
    "0229509657",   # 1  JOANA G. ANGCAYA
    "229509657",    # 2  MICAH ANGELIE G. ANGCAYA
    "1226497191",   # 3  MA. MONICA YINLEY G. ANGCAYA
    "1225987975",   # 4  MARY TIFFANY G. ANGCAYA
    "0230705209",   # 5  MICHAEL N. RAMOS
    "0239376761",   # 6  NELSA C. RAMOS
    "0238558057",   # 7  NAOMI ROSE C. RAMOS
    "0230632009",   # 8  WINONA KYLIE C. RAMOS
    "0228850297",   # 9  RANE NICOLO MANUEL C. RAMOS
    "0229175033",   # 10 ARVIN P. PANGANIBAN
    "0238980073",   # 11 GHIA LARIZE R. DIMAYUGA
    "0238873865",   # 12 ARHIA VICTORIA D. PANGANIBAN
    "0233336521",   # 13 CYNTHIA A. SAN MARTIN
    "0239417241",   # 14 BOBBY A. SAN MARTIN
    "0229235145",   # 15 FRANCO A. SAN MARTIN
    "0229576025",   # 16 JAN ALISON B. BAYOT
    "1225961687",   # 17 ROCHELLE ANN T. BAYOT
    "0239104185",   # 18 ROWN ALIZER T. BAYOT
    "0239784137",   # 19 JOMAR M. BARRERA
    "0622493687",   # 20 MARIAN G. BARRERA
    "0608404439",   # 21 LOURELLA G. BARRERA
    "0608357223",   # 22 LUCIANA L. BARRERA
    "1226499911",   # 23 GINA M. DELA REA
    "0609630199",   # 24 KRISTAL JOY M. DELA REA
    "1226283287",   # 25 CARISSA MAE M. DELA REA
    "1226783399",   # 26 EMIL I. SUMAGUI
    "1226651367",   # 27 NIEL I. SUMAGUI
    "1226715175",   # 28 EMMANUEL I. SUMAGUI
    "1226568295",   # 29 JELYN MAE D. VIBANDOR
    "0609606583",   # 30 MYLENE D. VIBANDOR
    "0629191799",   # 31 CHARIEL ALTHEA A. DELARMINO
    "1224966199",   # 32 JENNA ROSE A. BATACLAN
    "0629866151",   # 33 JUSTINE CARL M. DELA REA
    "0863533495",   # 34 ALLIAH MAE B. JAMON
    "0629471351",   # 35 JOHANNE ALECS B. AMBION
    "0629932215",   # 36 KENJIE RYLE QUIRRO L. CRUZ
    "0863367655",   # 37 MARIFE A. SIPAT
    "0863698791",   # 38 VERONICA ANNE S. FRESCO
    "0629412871",   # 39 MARY JOY B. MORA
    "0621004439",   # 40 AUBREY ROSE M. MADERA
    # ── 4 new residents ──────────────────────────────────────
    "0863412783",   # 50 MARIA ALETH G. PLAGANAS
    "0863500921",   # 51 GILLIAN LOU R. GUTIERREZ
    "0863619047",   # 52 ALLISTER MARVIN G. BAYAS
    "0863724566",   # 53 KEITH BEAU ALLEN Q. VILLAMOR
]

# Map: resident list index → RFID_UIDS index
# Indices 0-40 map straight (1:1). Indices 41-49 have no card.
# Indices 50-53 (the 4 new residents) map to RFID_UIDS[41-44].
_RFID_INDEX_MAP: dict[int, int] = {
    **{i: i for i in range(41)},   # original 41
    50: 41,                         # Plaganas
    51: 42,                         # Gutierrez
    52: 43,                         # Bayas
    53: 44,                         # Villamor
}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _parse_name(full_name: str) -> dict:
    parts = full_name.strip().split()
    last_name = parts[-1]

    compound_prefixes = {"DELA", "DE", "SAN", "DEL", "LOS", "LAS"}
    if len(parts) >= 2 and parts[-2].rstrip(".").upper() in compound_prefixes:
        last_name = f"{parts[-2]} {parts[-1]}"
        parts = parts[:-2]
    else:
        parts = parts[:-1]

    first_name = parts[0] if parts else ""
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
        "JOI-ANN", "LEA", "MIALYN", "MARLYN", "GILLIAN",
    }
    return "female" if first_name.upper().strip() in female_indicators else "male"


def _reg_date(birthdate: date) -> date:
    today = DEPLOY_START.date()
    age_days = (today - birthdate).days

    if age_days >= 18 * 365:
        return rand_historic_date(years_ago_min=1, years_ago_max=10)
    else:
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
    if existing >= 54:
        print(f"  ↳ Skipped — {existing} residents already exist.")
        return

    puroks = _get_puroks(db)

    try:
        config = get_config(db)
        expiry_days = config.rfid_expiry_days
    except Exception:
        expiry_days = 3 * 365

    expiration_date = date.today() + timedelta(days=expiry_days)

    residents_created = []

    for index, (full_name, bdate_str, street) in enumerate(RESIDENTS_DATA):
        name      = _parse_name(full_name)
        gender    = _infer_gender(full_name.split()[0])
        birthdate = date.fromisoformat(bdate_str)
        reg_date  = _reg_date(birthdate)

        if isinstance(reg_date, date) and not isinstance(reg_date, datetime):
            reg_dt = datetime(
                reg_date.year, reg_date.month, reg_date.day,
                random.randint(8, 16), random.randint(0, 59), 0,
                tzinfo=timezone.utc,
            )
        else:
            reg_dt = reg_date

        resident = Resident(
            last_name            = name["last_name"],
            first_name           = name["first_name"],
            middle_name          = name["middle_name"],
            suffix               = None,
            gender               = gender,
            birthdate            = birthdate,
            residency_start_date = reg_date if isinstance(reg_date, date) else reg_date.date(),
            email                = (
                f"{name['first_name'].lower()}"
                f".{name['last_name'].lower().replace(' ', '')}"
                f"{random.randint(10, 999)}@gmail.com"
            ),
            phone_number  = f"09{random.randint(100000000, 999999999)}",
            rfid_pin      = pwd_context.hash("0000"),
            registered_at = reg_dt,
        )

        db.add(resident)
        db.flush()

        purok = random.choice(puroks)

        address = Address(
            resident_id     = resident.id,
            house_no_street = street,
            purok_id        = purok.id,
            barangay        = "Poblacion Uno",
            municipality    = "Amadeo",
            province        = "Cavite",
            region          = "Region IV-A",
            is_current      = True,
            created_at      = reg_dt,
        )
        db.add(address)

        # Assign RFID card only to residents in the index map
        if index in _RFID_INDEX_MAP:
            rfid_idx = _RFID_INDEX_MAP[index]
            rfid = ResidentRFID(
                resident_id     = resident.id,
                rfid_uid        = RFID_UIDS[rfid_idx],
                is_active       = True,
                expiration_date = expiration_date,
                created_at      = datetime.now(),
            )
            db.add(rfid)

        residents_created.append(resident)

    db.commit()

    rfid_count   = len(_RFID_INDEX_MAP)
    no_card      = len(residents_created) - rfid_count
    print(
        f"  ↳ Inserted {len(residents_created)} residents "
        f"({rfid_count} with RFID cards, {no_card} without)"
    )

    return residents_created