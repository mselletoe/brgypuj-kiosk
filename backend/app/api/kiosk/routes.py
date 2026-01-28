"""
Kiosk API Module Aggregator
---------------------------
This module serves as the primary router for all Kiosk-related operations.
It centralizes sub-modules like authentication, resident services, and health checks
to provide a unified entry point for the frontend Kiosk application.
"""

from fastapi import APIRouter
from app.api.kiosk import auth, document, residents

# Initialize the master Kiosk router
# Developers can add 'dependencies' or 'responses' here that apply to all kiosk routes
router = APIRouter()

# Sub-Router Registration
# -----------------------
# Authentication routes are isolated in 'auth.py' for maintainability.
# Registered here to be accessible under the parent path.
router.include_router(auth.router)
router.include_router(document.router)
router.include_router(residents.router)

@router.get("/health")
def kiosk_health():
    """
    Kiosk Service Health Check.
    
    Used by load balancers, container orchestrators (like Docker/Kubernetes), 
    or the frontend to verify that the Kiosk backend module is responsive.
    
    Returns:
        dict: A status message confirming the module is operational.
    """
    return {"status": "kiosk ok"}