"""
app/api/admin/routes.py

Admin Dashboard API Aggregator.
Centralizes all administrative sub-routers covering document requests,
resident management, system configuration, and supporting services.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.admin import (
    document, auth, residents, equipment, feedback, announcement,
    blotter, transaction, faqs, id, audit, search, systemlogs,
    contact, systemconfig, backup, adminaccounts, finance,
    notifications, sms,
)

router = APIRouter()


# =================================================================================
# SUB-ROUTER REGISTRATION
# =================================================================================

router.include_router(auth.router)
router.include_router(document.router)
router.include_router(residents.router)
router.include_router(equipment.router)
router.include_router(feedback.router)
router.include_router(announcement.router)
router.include_router(blotter.router)
router.include_router(transaction.router)
router.include_router(faqs.router)
router.include_router(id.router)
router.include_router(audit.router)
router.include_router(search.router)
router.include_router(systemlogs.router)
router.include_router(contact.router)
router.include_router(systemconfig.router)
router.include_router(backup.router)
router.include_router(adminaccounts.router)
router.include_router(finance.router)
router.include_router(notifications.router)
router.include_router(sms.router)


# =================================================================================
# HEALTH CHECK
# =================================================================================

@router.get("/health")
def admin_health(db: Session = Depends(get_db)):
    return {"status": "admin ok"}