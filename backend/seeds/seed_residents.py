from datetime import date
from dateutil.relativedelta import relativedelta
from faker import Faker
from app.db.session import SessionLocal
from app.models.resident import Resident

fake = Faker("fil_PH")  # Filipino locale

# Target count per age group — adjust as needed
AGE_GROUPS = [
    {"label": "Child (0–12)",        "min_age": 0,  "max_age": 12, "count": 8},
    {"label": "Teen (13–19)",        "min_age": 13, "max_age": 19, "count": 8},
    {"label": "Young Adult (20–39)", "min_age": 20, "max_age": 39, "count": 16},
    {"label": "Middle-aged (40–59)", "min_age": 40, "max_age": 59, "count": 12},
    {"label": "Senior (60+)",        "min_age": 60, "max_age": 90, "count": 8},
]

SUFFIXES = [None, None, None, None, "Jr.", "Sr.", "III"]  # weighted toward None


def random_birthdate(min_age: int, max_age: int) -> date:
    today = date.today()
    start = today - relativedelta(years=max_age)
    end   = today - relativedelta(years=min_age)
    return fake.date_between(start_date=start, end_date=end)


def generate_residents() -> list[dict]:
    residents = []
    seen_emails = set()

    for group in AGE_GROUPS:
        for _ in range(group["count"]):
            gender = fake.random_element(["male", "female"])
            first  = fake.first_name_male()   if gender == "male" else fake.first_name_female()
            middle = fake.last_name()
            last   = fake.last_name()
            suffix = fake.random_element(SUFFIXES) if gender == "male" else None
            is_child = group["max_age"] < 13

            # Unique email
            base = f"{first.lower().replace(' ', '')}.{last.lower().replace(' ', '')}@test.com"
            email, counter = base, 1
            while email in seen_emails:
                email = f"{first.lower().replace(' ', '')}.{last.lower().replace(' ', '')}{counter}@test.com"
                counter += 1
            seen_emails.add(email)

            residents.append({
                "first_name":   first,
                "middle_name":  middle,
                "last_name":    last,
                "suffix":       suffix,
                "gender":       gender,
                "birthdate":    random_birthdate(group["min_age"], group["max_age"]),
                "email":        None if is_child else email,
                "phone_number": None if is_child else fake.numerify("09#########"),
                "rfid_pin":     "0000",  # sentinel — triggers PIN setup on first kiosk use
            })

    return residents


def seed_residents():
    db = SessionLocal()
    try:
        if db.query(Resident).count() > 0:
            print("✅ Residents already seeded")
            return

        residents = generate_residents()

        for r in residents:
            db.add(Resident(**r))

        db.commit()
        print(f"🌱 {len(residents)} residents seeded (PIN not set — residents must set on first use)")
        for group in AGE_GROUPS:
            print(f"   • {group['label']}: {group['count']}")

    except Exception as e:
        db.rollback()
        print("❌ Error seeding residents:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_residents()