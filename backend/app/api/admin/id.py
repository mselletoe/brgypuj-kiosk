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

  POST   /id-services/reports/{id}/resolve
  DELETE /id-services/reports/{id}

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
# ADMIN DASHBOARD — ID APPLICATION ACTIONS
# (pass-throughs to the shared document_service helpers;
#  ID Applications are stored in DocumentRequest with doctype_id = NULL)
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
# ADMIN DASHBOARD — RFID REPORT ACTIONS
# =========================================================

@router.post(
    "/reports/{report_id}/resolve",
    summary="[Admin] Mark RFID report as resolved",
)
def resolve_rfid_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(RFIDReport).filter(RFIDReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = "Resolved"
    db.commit()
    return {"detail": "Report resolved"}


@router.delete(
    "/reports/{report_id}",
    summary="[Admin] Delete RFID report",
)
def delete_rfid_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(RFIDReport).filter(RFIDReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return {"detail": "Report deleted"}