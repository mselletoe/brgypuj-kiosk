from app.db.session import SessionLocal
from app.models.equipment import EquipmentInventory

EQUIPMENT = [
    {
        "name": "Tent",
        "total_quantity": 5,
        "available_quantity": 5,
        "rate_per_day": 500.00,
    },
    {
        "name": "Chair",
        "total_quantity": 100,
        "available_quantity": 100,
        "rate_per_day": 5.00,
    },
]

def seed_equipment_inventory():
    db = SessionLocal()
    try:
        if db.query(EquipmentInventory).count() > 0:
            print("✅ Equipment already seeded")
            return

        for item in EQUIPMENT:
            db.add(EquipmentInventory(**item))

        db.commit()
        print("🌱 Equipment seeded")

    except Exception as e:
        db.rollback()
        print("❌ Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed_equipment_inventory()
