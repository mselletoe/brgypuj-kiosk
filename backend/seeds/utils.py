"""
seeds/utils.py

Shared helpers for generating fake timestamps within the
deployment window (2026-03-16 → 2026-04-13) and for
historic resident registration dates.
"""

import random
from datetime import datetime, date, timedelta, timezone

# ── Deployment window ────────────────────────────────────────────
DEPLOY_START = datetime(2026, 3, 16,  8,  0, 0, tzinfo=timezone.utc)
DEPLOY_END   = datetime(2026, 4, 13, 17, 30, 0, tzinfo=timezone.utc)

OFFICE_OPEN  = 8   # 08:00
OFFICE_CLOSE = 17  # 17:00  (last requests at 17:00)


def rand_dt(
    start: datetime = DEPLOY_START,
    end: datetime   = DEPLOY_END,
    office_hours_only: bool = True,
) -> datetime:
    """
    Random timezone-aware datetime between *start* and *end*.
    If office_hours_only=True, restricts hour to OFFICE_OPEN..OFFICE_CLOSE.
    Skips weekends (Sat/Sun) automatically when office_hours_only=True.
    """
    delta = int((end - start).total_seconds())
    for _ in range(500):          # up to 500 tries to land on a valid slot
        offset = random.randint(0, delta)
        candidate = start + timedelta(seconds=offset)
        if office_hours_only:
            if candidate.weekday() >= 5:          # skip Sat(5) / Sun(6)
                continue
            if not (OFFICE_OPEN <= candidate.hour < OFFICE_CLOSE):
                continue
        return candidate
    # fallback: return something safe
    return DEPLOY_START + timedelta(hours=2)


def rand_date(start: date = DEPLOY_START.date(), end: date = DEPLOY_END.date()) -> date:
    """Random date between start and end (inclusive)."""
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def rand_historic_date(years_ago_min: int = 0, years_ago_max: int = 10) -> date:
    """
    Random past date for historic resident registration.
    years_ago_min / years_ago_max relative to DEPLOY_START date.
    """
    base = DEPLOY_START.date()
    start = base - timedelta(days=years_ago_max * 365)
    end   = base - timedelta(days=years_ago_min * 365)
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 0)))


def progression(base: datetime, min_hours: int = 1, max_hours: int = 48) -> datetime:
    """
    Return a datetime that is *base* plus a random forward offset.
    Used to simulate status progressions (Pending → Approved → Released).
    """
    offset = timedelta(hours=random.randint(min_hours, max_hours))
    result = base + offset
    # keep within deployment window
    if result > DEPLOY_END:
        result = DEPLOY_END - timedelta(minutes=random.randint(10, 120))
    return result


# ── Fake Filipino names ───────────────────────────────────────────
FIRST_NAMES_M = [
    "Juan", "Jose", "Pedro", "Miguel", "Ramon", "Eduardo", "Roberto",
    "Antonio", "Fernando", "Carlo", "Dante", "Emmanuel", "Rene", "Gilbert",
    "Reynaldo", "Rodolfo", "Ernesto", "Alfredo", "Bernardo", "Crisanto",
]
FIRST_NAMES_F = [
    "Maria", "Ana", "Rosario", "Cristina", "Liza", "Marilou", "Elvira",
    "Shirley", "Cecilia", "Rowena", "Maricel", "Geraldine", "Tessie",
    "Nenita", "Ligaya", "Remedios", "Edna", "Fe", "Gloria", "Norma",
]
LAST_NAMES = [
    "Santos", "Reyes", "Cruz", "Bautista", "Ocampo", "Garcia", "Mendoza",
    "Torres", "Flores", "Castillo", "Villanueva", "Dela Cruz", "Diaz",
    "Ramos", "Hernandez", "Aquino", "Marquez", "Velasco", "Aguilar",
    "Domingo", "Pascual", "Navarro", "Miranda", "Lim", "Tan",
]
MIDDLE_NAMES = [
    "Santos", "Reyes", "Cruz", "Garcia", "Flores", "Ramos", "Torres",
    "Mendoza", "Hernandez", "Castillo", "Aquino", "Marquez", "Navarro",
]
PUROKS = ["Purok 1", "Purok 2", "Purok 3", "Purok 4", "Purok 5"]
STREETS = [
    "Rizal Street", "Mabini Street", "Quezon Avenue", "Bonifacio Street",
    "Luna Street", "Aguinaldo Street", "Del Pilar Street",
]


def fake_name(gender: str = "male") -> dict:
    """Return dict with first_name, middle_name, last_name, gender."""
    if gender == "female":
        first = random.choice(FIRST_NAMES_F)
    else:
        first = random.choice(FIRST_NAMES_M)
    return {
        "first_name":  first,
        "middle_name": random.choice(MIDDLE_NAMES),
        "last_name":   random.choice(LAST_NAMES),
        "gender":      gender,
    }


def fake_phone() -> str:
    return f"09{random.randint(100000000, 999999999)}"


def fake_email(first: str, last: str) -> str:
    tag = random.randint(10, 999)
    return f"{first.lower()}.{last.lower().replace(' ', '')}{tag}@gmail.com"