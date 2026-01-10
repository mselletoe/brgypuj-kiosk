"""
Admin Dashboard API Aggregator
---------------------------
Centralizes administrative functions such as document request processing, 
resident management, and system configuration.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.api.admin import document, auth

# Initialize the master Admin router
# Developers can add 'dependencies' or 'responses' here that apply to all admin routes
router = APIRouter()

# Sub-Router Registration
# -----------------------
router.include_router(auth.router)
router.include_router(document.router)

@router.get("/health")
def admin_health(db: Session = Depends(get_db)):
    """
    Admin Service Health Check.
    
    Unlike the kiosk health check, this verifies active database 
    connectivity, which is critical for administrative operations.
    
    Returns:
        dict: A status message confirming the admin module and DB are operational.
    """
    return {"status": "admin ok"}
