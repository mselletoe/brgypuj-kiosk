from seeds.seed_puroks import seed_puroks
from seeds.seed_residents import seed_residents
from seeds.seed_addresses import seed_addresses
from seeds.seed_rfid import seed_rfids
from seeds.seed_admin import seed_admin
from seeds.seed_document_types import seed_document_types
from seeds.seed_equipment_inventory import seed_equipment_inventory

if __name__ == "__main__":
    print("🌱 Starting database seeding...")
    print("-" * 50)
    
    seed_puroks()
    seed_residents()
    seed_addresses()
    seed_rfids()
    seed_admin()
    seed_document_types()
    seed_equipment_inventory()
    
    print("-" * 50)
    print("✅ Database seeding completed!")