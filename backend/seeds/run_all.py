from seeds.seed_puroks import seed_puroks
from seeds.seed_residents import seed_residents
from seeds.seed_addresses import seed_addresses
from seeds.seed_rfid import seed_rfids
from seeds.seed_admin import seed_admin
from seeds.seed_barangay_ids import seed_barangay_ids

def seed_all():
    """
    Run all database seeding functions in the correct order.
    Order matters due to foreign key relationships.
    """
    print("🌱 Starting database seeding...")
    print("-" * 50)
    
    try:
        # 1. Seed puroks first (no dependencies)
        seed_puroks()
        
        # 2. Seed residents (no dependencies)
        seed_residents()
        
        # 3. Seed addresses (depends on residents and puroks)
        seed_addresses()
        
        # 4. Seed RFIDs (depends on residents)
        seed_rfids()
        
        # 5. Seed admin (depends on residents)
        seed_admin()

        seed_barangay_ids()
        
        print("-" * 50)
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print("-" * 50)
        print(f"❌ Database seeding encountered an error: {e}")
        raise

if __name__ == "__main__":
    seed_all()