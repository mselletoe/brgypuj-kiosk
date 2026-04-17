"""
seeds/seed_sms.py
"""

import random
from sqlalchemy.orm import Session

from seeds.utils import rand_dt
from app.models.sms import SMSLog


SMS_MESSAGES = [
    "BRGY POBLACION UNO: Reminder - Barangay Assembly on March 20, 9AM at the Barangay Hall. Please attend. -Brgy Captain",
    "BRGY POBLACION UNO: Free Medical Mission on March 22. 8AM-12PM, Multi-Purpose Hall. Bring your health card.",
    "BRGY POBLACION UNO: Your document request has been approved. Please proceed to the barangay hall to claim it.",
    "BRGY POBLACION UNO: Community Clean-Up Drive on March 28, 7AM. All purok leaders, please mobilize your residents.",
    "BRGY POBLACION UNO: DSWD Ayuda distribution starts March 30. Beneficiaries please check your schedule.",
    "BRGY POBLACION UNO: The barangay basketball tournament registration is now open until April 5.",
    "BRGY POBLACION UNO: Reminder to all equipment borrowers - please return borrowed items on or before the agreed date.",
    "BRGY POBLACION UNO: Senior citizen pension release on April 8, 8:30AM. Bring your SC ID.",
    "BRGY POBLACION UNO: Water interruption on April 10 for maintenance. Please store water in advance.",
    "BRGY POBLACION UNO: Anti-rabies vaccination for pets on April 11, 9AM, Purok 1 Covered Court.",
    "BRGY POBLACION UNO: Reminder - all residents must update their barangay records. Visit the kiosk or hall.",
    "BRGY POBLACION UNO: New barangay ID applications are now accepted via the kiosk system.",
]

MODES = ["groups", "puroks", "specific"]


def seed_sms(db: Session):
    print("\n[sms] Seeding SMS logs …")

    existing = db.query(SMSLog).count()
    if existing >= 5:
        print(f"  ↳ Skipped — {existing} SMS logs already exist.")
        return

    count = 0
    for msg in SMS_MESSAGES:
        mode       = random.choice(MODES)
        recipients = random.randint(15, 180)
        sms = SMSLog(
            message    = msg,
            mode       = mode,
            recipients = recipients,
            sent_at    = rand_dt(),
        )
        db.add(sms)
        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} SMS log entries.")