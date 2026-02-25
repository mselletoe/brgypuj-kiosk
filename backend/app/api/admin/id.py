"""
ID Services Router
------------------
Exposes the three ID Service workflows as REST endpoints consumed
by the Barangay Kiosk and Admin Dashboard.

Admin dashboard:
  GET  /id-services/admin/applications           — list all ID applications
  GET  /id-services/admin/reports                — list all RFID lost-card reports
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.id import (
    IDApplicationAdminOut,
    RFIDReportAdminOut,
)
from app.services.id_service import (
    get_all_id_applications,
    get_all_rfid_reports,
)

router = APIRouter(prefix="/id-services")


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@router.get(
    "/applications",
    response_model=list[IDApplicationAdminOut],
    summary="[Admin] List all ID applications",
    description=(
        "Returns all DocumentRequests of type 'ID Application' for the admin "
        "Document Requests dashboard. Includes resident name, RFID, and request status."
    ),
)
def list_id_applications(db: Session = Depends(get_db)):
    return get_all_id_applications(db)


@router.get(
    "/reports",
    response_model=list[RFIDReportAdminOut],
    summary="[Admin] List all RFID lost-card reports",
    description=(
        "Returns all RFIDReport records for the admin Reports dashboard. "
        "Includes resident name, the deactivated RFID UID, and report status."
    ),
)
def list_rfid_reports(db: Session = Depends(get_db)):
    return get_all_rfid_reports(db)