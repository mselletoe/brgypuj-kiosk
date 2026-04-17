"""
seeds/seed_notifications.py
"""

import random
from sqlalchemy.orm import Session

from seeds.utils import rand_dt
from app.models.notification import Notification


NOTIFICATION_TEMPLATES = [
    # (type, event, msg_template)
    ("Document", "doc_pending",   "New document request submitted — {ref}"),
    ("Document", "doc_approved",  "Document request {ref} has been approved."),
    ("Document", "doc_released",  "Document request {ref} is ready for release."),
    ("Document", "doc_rejected",  "Document request {ref} was rejected."),
    ("Equipment","equip_pending", "New equipment borrowing request from {name}."),
    ("Equipment","equip_approved","Equipment request {ref} approved."),
    ("Equipment","equip_returned","Equipment from request {ref} has been returned."),
    ("Feedback", "feedback_new",  "A resident submitted new feedback (Rating: {rating}/5)."),
    ("Feedback", "feedback_new",  "Feedback received — General Experience (⭐{rating}/5)."),
    ("System",   "system_info",   "System maintenance completed successfully."),
    ("System",   "system_info",   "Database backup completed."),
    ("Resident", "resident_new",  "New resident registered: {name}."),
]

NAMES  = ["Santos, Juan", "Reyes, Maria", "Cruz, Pedro", "Bautista, Ana"]
REFS   = [f"DR-{n}" for n in range(1001, 1041)] + [f"ER-{n}" for n in range(2001, 2015)]


def seed_notifications(db: Session):
    print("\n[notifications] Seeding notifications …")

    existing = db.query(Notification).count()
    if existing >= 10:
        print(f"  ↳ Skipped — {existing} notifications already exist.")
        return

    count = 0
    for _ in range(40):
        tpl_type, event, msg_tpl = random.choice(NOTIFICATION_TEMPLATES)

        msg = msg_tpl.format(
            ref    = random.choice(REFS),
            name   = random.choice(NAMES),
            rating = random.randint(3, 5),
        )

        n = Notification(
            type       = tpl_type,
            msg        = msg,
            is_read    = random.choices([True, False], weights=[60, 40])[0],
            event      = event,
            created_at = rand_dt(),
        )
        db.add(n)
        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} notifications.")