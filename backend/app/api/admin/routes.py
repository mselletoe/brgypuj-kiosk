"""
Admin Dashboard API Aggregator
---------------------------
Centralizes administrative functions such as document request processing, 
resident management, and system configuration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.admin import document, auth, residents, equipment, feedback, announcement, blotter, transaction, faqs, id, audit, search


# Initialize the master Admin router
router = APIRouter()

# Sub-Router Registration
# -----------------------
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


@router.get("/health")
def admin_health(db: Session = Depends(get_db)):
    """
    Admin Service Health Check.
    """
    return {"status": "admin ok"}