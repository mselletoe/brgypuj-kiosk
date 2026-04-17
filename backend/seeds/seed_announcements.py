"""
seeds/seed_announcements.py

Seeds barangay announcements spread across the deployment window.
"""

import random
from datetime import timedelta
from sqlalchemy.orm import Session

from seeds.utils import rand_dt, rand_date, DEPLOY_START, DEPLOY_END
from app.models.announcement import Announcement


ANNOUNCEMENT_TEMPLATES = [
    {
        "title": "Barangay Assembly – First Quarter 2026",
        "description": (
            "All residents of Barangay Poblacion Uno are hereby invited to attend the "
            "First Quarter Barangay Assembly. Discuss community concerns, updates on "
            "barangay projects, and upcoming events. Attendance is encouraged."
        ),
        "location": "Barangay Hall, Poblacion Uno",
        "event_time": "09:00 AM",
    },
    {
        "title": "Free Medical Mission",
        "description": (
            "The barangay, in partnership with the Municipal Health Office, will conduct "
            "a free medical mission. Services include blood pressure monitoring, blood "
            "sugar testing, and free medicines. All residents may avail of these services."
        ),
        "location": "Barangay Multi-Purpose Hall",
        "event_time": "08:00 AM",
    },
    {
        "title": "Community Clean-Up Drive",
        "description": (
            "Join your neighbors in keeping our barangay clean and green. Residents are "
            "encouraged to participate in the clean-up drive. Bring gloves and brooms. "
            "Garbage bags will be provided by the barangay."
        ),
        "location": "All Puroks, Poblacion Uno",
        "event_time": "07:00 AM",
    },
    {
        "title": "Livelihood Training: Handicraft Making",
        "description": (
            "The barangay will hold a free livelihood training on handicraft making "
            "for interested residents. Materials will be provided. Priority will be "
            "given to unemployed residents and solo parents."
        ),
        "location": "Barangay Skills Training Center",
        "event_time": "01:00 PM",
    },
    {
        "title": "DSWD Ayuda Distribution Schedule",
        "description": (
            "The distribution of DSWD financial assistance will be conducted per purok "
            "schedule. Beneficiaries must bring their valid ID and the official notice "
            "they received. Please follow the schedule to avoid crowding."
        ),
        "location": "Barangay Hall, Poblacion Uno",
        "event_time": "08:00 AM",
    },
    {
        "title": "Barangay Basketball Tournament 2026",
        "description": (
            "The annual Barangay Basketball Tournament is now open for registration. "
            "Teams of 10–15 players from each purok may join. Registration forms are "
            "available at the barangay hall. Tournament starts March 22."
        ),
        "location": "Barangay Basketball Court",
        "event_time": "03:00 PM",
    },
    {
        "title": "Senior Citizens' Monthly Pension Release",
        "description": (
            "Senior citizens are reminded that the monthly pension release will be "
            "conducted this week. Please bring your Senior Citizen ID and a valid "
            "government-issued ID. Proxy claimants must present an authorization letter."
        ),
        "location": "Barangay Hall, Poblacion Uno",
        "event_time": "08:30 AM",
    },
    {
        "title": "Water Interruption Advisory",
        "description": (
            "Please be advised that there will be a scheduled water service interruption "
            "affecting Puroks 2, 3, and 4 for maintenance work on the main pipeline. "
            "Residents are advised to store enough water in advance."
        ),
        "location": "Puroks 2, 3, and 4",
        "event_time": "08:00 AM",
    },
    {
        "title": "Rabies Vaccination for Dogs and Cats",
        "description": (
            "The Municipal Veterinary Office will conduct a free anti-rabies vaccination "
            "for dogs and cats. Pet owners are encouraged to bring their pets. "
            "This is part of the National Rabies Prevention and Control Program."
        ),
        "location": "Purok 1 Covered Court",
        "event_time": "09:00 AM",
    },
    {
        "title": "Street Lighting Maintenance Notice",
        "description": (
            "The barangay will be conducting maintenance on streetlights along Rizal "
            "Street and Mabini Street. Residents along these areas are advised to "
            "prepare alternative lighting during the maintenance period."
        ),
        "location": "Rizal Street / Mabini Street",
        "event_time": "06:00 PM",
    },
]


def seed_announcements(db: Session):
    print("\n[announcements] Seeding announcements …")

    existing = db.query(Announcement).count()
    if existing >= 5:
        print(f"  ↳ Skipped — {existing} announcements already exist.")
        return

    count = 0
    deploy_start_date = DEPLOY_START.date()
    deploy_end_date   = DEPLOY_END.date()

    for i, tpl in enumerate(ANNOUNCEMENT_TEMPLATES):
        # Spread event_dates across the window
        event_date = deploy_start_date + timedelta(days=i * 3)
        if event_date > deploy_end_date:
            event_date = deploy_end_date

        created_at = rand_dt()

        ann = Announcement(
            title       = tpl["title"],
            description = tpl["description"],
            event_date  = event_date,
            event_time  = tpl["event_time"],
            location    = tpl["location"],
            is_active   = True,
            created_at  = created_at,
        )
        db.add(ann)
        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} announcements.")