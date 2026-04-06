"""
app/api/kiosk/routes.py

Kiosk API module aggregator.
Registers all kiosk sub-routers under a single parent router,
providing a unified entry point for the frontend kiosk application.
"""

from fastapi import APIRouter
from app.api.kiosk import (
    auth, document, residents, equipment, feedback,
    announcement, transaction, faqs, id, registration,
    contact, systemconfig, exitkiosk,
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
router.include_router(transaction.router)
router.include_router(faqs.router)
router.include_router(id.router)
router.include_router(registration.router)
router.include_router(contact.router)
router.include_router(systemconfig.router)
router.include_router(exitkiosk.router)


# =================================================================================
# HEALTH CHECK
# =================================================================================

@router.get("/health")
def kiosk_health():
    return {"status": "kiosk ok"}