from datetime import date
from dateutil.relativedelta import relativedelta
from app.db.session import SessionLocal
from app.models.resident import ResidentRFID
from app.models.barangayid import BarangayID

VALIDITY_YEARS = 3  # Barangay ID expires after this many years


def generate_brgy_id_number(index: int) -> str:
    """Zero-padded 5-digit Barangay ID number, e.g. 00001."""
    return str(index + 1).zfill(5)


def seed_barangay_ids():
    db = SessionLocal()
    try:
        if db.query(BarangayID).count() > 0:
            print("✅ Barangay IDs already seeded")
            return

        # Only residents who have an RFID get a Barangay ID
        rfids = db.query(ResidentRFID).all()
        if not rfids:
            print("❌ No RFIDs found. Seed RFIDs first.")
            return

        today = date.today()
        for idx, rfid in enumerate(rfids):
            db.add(BarangayID(
                brgy_id_number=generate_brgy_id_number(idx),
                resident_id=rfid.resident_id,
                rfid_id=rfid.id,
                issued_date=today,
                expiration_date=today + relativedelta(years=VALIDITY_YEARS),
                is_active=True,
            ))
            print(f"   🪪 Brgy. ID {generate_brgy_id_number(idx)} → resident_id {rfid.resident_id}")

        db.commit()
        print(f"🌱 {len(rfids)} Barangay ID(s) seeded successfully")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding Barangay IDs: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_barangay_ids()