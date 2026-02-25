from datetime import date
from passlib.context import CryptContext
from app.db.session import SessionLocal
from app.models.resident import Resident

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

RESIDENTS = [
    {
        "first_name": "Maxpein Zin",
        "middle_name": "Park",
        "last_name": "del Valle",
        "gender": "female",
        "birthdate": date(1989, 3, 16),
        "email": "maxpeinzin@test.com",
        "phone_number": "09123456789",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Maxwell Laurent",
        "last_name": "del Valle",
        "gender": "male",
        "birthdate": date(1986, 9, 22),
        "email": "maxwelllaurent@test.com",
        "phone_number": "09327564789",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Maxrill Won",
        "last_name": "del Valle",
        "gender": "male",
        "birthdate": date(1992, 4, 30),
        "email": "maxrillwon@test.com",
        "phone_number": "09731285937",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Maze",
        "last_name": "del Valle",
        "gender": "female",
        "birthdate": date(1960, 2, 3),
        "email": "maze@test.com",
        "phone_number": "09437859094",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Maximor",
        "last_name": "del Valle",
        "gender": "male",
        "birthdate": date(1960, 7, 24),
        "email": "maximor@test.com",
        "phone_number": "09432567894",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Deib Lohr",
        "last_name": "Enrile",
        "gender": "male",
        "birthdate": date(1989, 8, 4),
        "email": "deiblohr@test.com",
        "phone_number": "09997435672",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Maxspaun Thaddeaus",
        "middle_name": "del Valle",
        "last_name": "Enrile",
        "gender": "male",
        "birthdate": date(2006, 8, 1),
        "email": "maxspaunthaddeaus@test.com",
        "phone_number": "09123456789",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Zarnaih",
        "last_name": "Marchessa",
        "gender": "female",
        "birthdate": date(1988, 3, 12),
        "email": "zarnaih@test.com",
        "phone_number": "09456734563",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Lee Roi",
        "last_name": "Gozon",
        "gender": "male",
        "birthdate": date(1989, 9, 13),
        "email": "leeroi@test.com",
        "phone_number": "09223412567",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Zelestaire Donatelli",
        "middle_name": "Marchessa",
        "last_name": "Gozon",
        "gender": "female",
        "birthdate": date(2007, 9, 19),
        "email": "zelestairedonatelli@test.com",
        "phone_number": "09234533789",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Randall",
        "last_name": "Echavez",
        "gender": "male",
        "birthdate": date(1986, 10, 10),
        "email": "randall@test.com",
        "phone_number": "09223412567",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Tokyo Athena",
        "middle_name": "Cortez",
        "last_name": "Velasquez",
        "gender": "female",
        "birthdate": date(2002, 4, 9),
        "email": "tokyoathena@test.com",
        "phone_number": "09223234567",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Zeus Emmanuel",
        "middle_name": "Cortez",
        "last_name": "Velasquez",
        "gender": "male",
        "birthdate": date(2000, 5, 21),
        "email": "zeusemmanuel@test.com",
        "phone_number": "09324566734",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Briane Leigh",
        "middle_name": "Regillo",
        "last_name": "Imperial",
        "gender": "female",
        "birthdate": date(2004, 7, 2),
        "email": "brianeleigh@test.com",
        "phone_number": "09234512345",
        "rfid_pin": "1234",
    },
    {
        "first_name": "Jandryll Pierce",
        "last_name": "Peña",
        "gender": "male",
        "birthdate": date(2004, 9, 17),
        "email": "jandryllpierce@test.com",
        "phone_number": "09125564567",
        "rfid_pin": "1234",
    }, 
]

def seed_residents():
    db = SessionLocal()
    try:
        if db.query(Resident).count() > 0:
            print("✅ Residents already seeded")
            return

        for r in RESIDENTS:
            # HASH THE PIN HERE before saving to DB
            r_copy = r.copy()
            r_copy["rfid_pin"] = pwd_context.hash(r["rfid_pin"])

            db.add(Resident(**r_copy))

        db.commit()
        print("🌱 Residents seeded (with hashed PINs)")
    except Exception as e:
        db.rollback()
        print("❌ Error seeding residents:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_residents()
