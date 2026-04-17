"""
seeds/seed_audit.py
"""

import random
from sqlalchemy.orm import Session

from seeds.utils import rand_dt
from app.models.audit import AdminAuditLog
from app.models.admin import Admin


AUDIT_TEMPLATES = [
    # (action, entity_type, details_template)
    ("Approved Request",    "doc",      "DOC-{ref} - Barangay Clearance"),
    ("Approved Request",    "doc",      "DOC-{ref} - Certificate of Indigency"),
    ("Released Document",   "doc",      "DOC-{ref} - Barangay Clearance released to resident"),
    ("Rejected Request",    "doc",      "DOC-{ref} - Incomplete requirements"),
    ("Approved Request",    "equip",    "EQ-{ref} - Sound System approved for borrowing"),
    ("Equipment Returned",  "equip",    "EQ-{ref} - Plastic Chairs returned in good condition"),
    ("Added Resident",      "resident", "New resident registered: {name}"),
    ("Updated Resident",    "resident", "Updated contact info for {name}"),
    ("Resolved Blotter",    "blotter",  "BL-2026-{num:03d} - Dispute settled"),
    ("Created Announcement","system",   "Posted: Barangay Assembly - Q1 2026"),
    ("Sent SMS Blast",      "system",   "Sent to {count} recipients via {mode}"),
    ("Exported Report",     "system",   "Monthly transaction report exported"),
    ("Admin Login",         "system",   "Admin logged in from {ip}"),
    ("Admin Logout",        "system",   "Admin session ended"),
    ("Updated Settings",    "system",   "System configuration updated"),
]

NAMES    = ["Santos, Juan", "Reyes, Maria", "Cruz, Pedro", "Flores, Ana"]
MODES    = ["groups", "puroks", "specific"]
IPS      = ["192.168.1.10", "192.168.1.15", "192.168.1.22", "10.0.0.5"]


def seed_audit(db: Session):
    print("\n[audit] Seeding admin audit logs …")

    existing = db.query(AdminAuditLog).count()
    if existing >= 10:
        print(f"  ↳ Skipped — {existing} audit logs already exist.")
        return

    # Try to get a real admin id, fall back to None
    admin = db.query(Admin).first()
    admin_id = admin.id if admin else None

    count = 0
    for _ in range(50):
        action_tpl, entity_type, details_tpl = random.choice(AUDIT_TEMPLATES)

        details = details_tpl.format(
            ref   = random.randint(1001, 1099),
            name  = random.choice(NAMES),
            num   = random.randint(1, 30),
            count = random.randint(20, 200),
            mode  = random.choice(MODES),
            ip    = random.choice(IPS),
        )

        log = AdminAuditLog(
            admin_id    = admin_id,
            action      = action_tpl,
            details     = details,
            entity_type = entity_type,
            created_at  = rand_dt(),
        )
        db.add(log)
        count += 1

    db.commit()
    print(f"  ↳ Inserted {count} audit log entries.")