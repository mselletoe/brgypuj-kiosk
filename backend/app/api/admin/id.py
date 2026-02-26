"""
ID Services Router  (Admin)
---------------------------
Admin-only endpoints for the ID Services feature.

  GET    /id-services/applications                  — list all ID applications
  GET    /id-services/reports                       — list all RFID lost-card reports

  POST   /id-services/applications/{id}/approve
  POST   /id-services/applications/{id}/reject
  POST   /id-services/applications/{id}/release
  POST   /id-services/applications/{id}/mark-paid
  POST   /id-services/applications/{id}/mark-unpaid
  POST   /id-services/applications/{id}/undo
  DELETE /id-services/applications/{id}
  POST   /id-services/applications/bulk-delete
  POST   /id-services/applications/bulk-undo

  POST   /id-services/reports/{id}/undo            — reactivates the resident's RFID card
  DELETE /id-services/reports/{id}
  POST   /id-services/reports/bulk-undo
  POST   /id-services/reports/bulk-delete

ID Applications are stored in the DocumentRequest table with doctype_id = NULL.
The action endpoints are thin pass-throughs to the shared document_service helpers
so the admin frontend can use the same approve/reject/delete/bulk pattern as
regular document requests.
"""

from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.id import (
    IDApplicationAdminOut,
    RFIDReportAdminOut,
)
from app.services.id_service import (
    get_all_id_applications,
    get_all_rfid_reports,
    undo_rfid_report,
    delete_rfid_report,
    bulk_delete_rfid_reports,
)
from app.services.document_service import (
    approve_request,
    reject_request,
    release_request,
    mark_request_paid,
    mark_request_unpaid,
    undo_request,
    delete_request,
    bulk_delete_requests,
    bulk_undo_requests,
)
from app.models.misc import RFIDReport

router = APIRouter(prefix="/id-services")


# =========================================================
# LIST
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


# =========================================================
# ID APPLICATION ACTIONS
# (pass-throughs to the shared document_service helpers)
# =========================================================

@router.post("/applications/{request_id}/approve", summary="[Admin] Approve ID application")
def approve_id_application(request_id: int, db: Session = Depends(get_db)):
    if not approve_request(db, request_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Application approved"}


@router.post("/applications/{request_id}/reject", summary="[Admin] Reject ID application")
def reject_id_application(request_id: int, db: Session = Depends(get_db)):
    if not reject_request(db, request_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Application rejected"}


@router.post("/applications/{request_id}/release", summary="[Admin] Release ID application")
def release_id_application(request_id: int, db: Session = Depends(get_db)):
    if not release_request(db, request_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Application released"}


@router.post("/applications/{request_id}/mark-paid", summary="[Admin] Mark ID application as paid")
def mark_id_application_paid(request_id: int, db: Session = Depends(get_db)):
    if not mark_request_paid(db, request_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Marked as paid"}


@router.post("/applications/{request_id}/mark-unpaid", summary="[Admin] Mark ID application as unpaid")
def mark_id_application_unpaid(request_id: int, db: Session = Depends(get_db)):
    if not mark_request_unpaid(db, request_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Marked as unpaid"}


@router.post("/applications/{request_id}/undo", summary="[Admin] Undo last status change")
def undo_id_application(request_id: int, db: Session = Depends(get_db)):
    try:
        if not undo_request(db, request_id):
            raise HTTPException(status_code=404, detail="Application not found")
        return {"detail": "Application status reverted"}
    except HTTPException:
        raise


@router.delete("/applications/{request_id}", summary="[Admin] Delete ID application")
def delete_id_application(request_id: int, db: Session = Depends(get_db)):
    if not delete_request(db, request_id):
        raise HTTPException(status_code=404, detail="Application not found")
    return {"detail": "Application deleted"}


@router.post("/applications/bulk-delete", summary="[Admin] Bulk delete ID applications")
def bulk_delete_id_applications(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    deleted_count = bulk_delete_requests(db, ids)
    return {"detail": f"{deleted_count} applications deleted"}


@router.post("/applications/bulk-undo", summary="[Admin] Bulk undo ID application status changes")
def bulk_undo_id_applications(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    updated_count = bulk_undo_requests(db, ids)
    return {"detail": f"{updated_count} applications reverted"}


# =========================================================
# RFID REPORT ACTIONS
# =========================================================

@router.post(
    "/reports/bulk-undo",
    summary="[Admin] Bulk undo RFID reports — reactivates residents' RFID cards",
)
def bulk_undo_rfid_reports_endpoint(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    results = {"reverted": [], "failed": []}
    for report_id in ids:
        try:
            undo_rfid_report(db, report_id)
            results["reverted"].append(report_id)
        except HTTPException:
            results["failed"].append(report_id)
    return {"detail": f"{len(results['reverted'])} reports reverted", **results}


@router.post(
    "/reports/bulk-delete",
    summary="[Admin] Bulk delete RFID reports",
)
def bulk_delete_rfid_reports_endpoint(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    deleted_count = bulk_delete_rfid_reports(db, ids)
    return {"detail": f"{deleted_count} reports deleted"}


@router.post(
    "/reports/{report_id}/undo",
    summary="[Admin] Undo RFID report — reactivates the resident's RFID card",
    description=(
        "Finds the most recently deactivated RFID card for the resident, "
        "sets is_active = True, and marks the report as Resolved."
    ),
)
def undo_rfid_report_endpoint(report_id: int, db: Session = Depends(get_db)):
    return undo_rfid_report(db, report_id)


@router.delete(
    "/reports/{report_id}",
    summary="[Admin] Delete RFID report",
    description="Hard-deletes the report record. Does NOT reactivate the RFID card.",
)
def delete_rfid_report_endpoint(report_id: int, db: Session = Depends(get_db)):
    if not delete_rfid_report(db, report_id):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"detail": "Report deleted"}