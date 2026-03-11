"""
ID Services Router  (Admin)
---------------------------
Admin-only endpoints for the ID Services feature.

  GET    /id-services/applications                  — list all ID applications
  GET    /id-services/reports                       — list all RFID lost-card reports

  POST   /id-services/applications/{id}/approve
  POST   /id-services/applications/{id}/reject
  POST   /id-services/applications/{id}/release     — generates brgy_id_number,
                                                       fills docx template, creates
                                                       BarangayID row
  POST   /id-services/applications/{id}/mark-paid
  POST   /id-services/applications/{id}/mark-unpaid
  POST   /id-services/applications/{id}/undo
  GET    /id-services/applications/{id}/download    — download the filled ID docx
  DELETE /id-services/applications/{id}
  POST   /id-services/applications/bulk-delete
  POST   /id-services/applications/bulk-undo

  POST   /id-services/reports/{id}/undo
  DELETE /id-services/reports/{id}
  POST   /id-services/reports/bulk-undo
  POST   /id-services/reports/bulk-delete

ID Applications are stored in the DocumentRequest table with doctype_id = NULL.
Release is handled by id_service.release_id_application (NOT the shared
document_service.release_request) because it carries extra logic:
brgy_id_number generation, docx template filling, and BarangayID row creation.
All other actions (approve, reject, mark-paid, undo, delete) still delegate to
the shared document_service helpers.
"""

from pathlib import Path
from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db

BASE_DIR = Path(__file__).resolve().parents[3]
from app.schemas.id import (
    IDApplicationAdminOut,
    RFIDReportAdminOut,
)
from app.services.id_service import (
    get_all_id_applications,
    get_all_rfid_reports,
    release_id_application,
    undo_rfid_report,
    delete_rfid_report,
    bulk_delete_rfid_reports,
)
from app.services.document_service import (
    approve_request,
    reject_request,
    mark_request_paid,
    mark_request_unpaid,
    undo_request,
    delete_request,
    bulk_delete_requests,
    bulk_undo_requests,
)
from app.models.document import DocumentRequest

router = APIRouter(prefix="/id-services")


# =========================================================
# LIST
# =========================================================

@router.get(
    "/applications",
    response_model=list[IDApplicationAdminOut],
    summary="[Admin] List all ID applications",
)
def list_id_applications(db: Session = Depends(get_db)):
    return get_all_id_applications(db)


@router.get(
    "/reports",
    response_model=list[RFIDReportAdminOut],
    summary="[Admin] List all RFID lost-card reports",
)
def list_rfid_reports(db: Session = Depends(get_db)):
    return get_all_rfid_reports(db)


# =========================================================
# ID APPLICATION ACTIONS
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


@router.post(
    "/applications/{request_id}/release",
    summary="[Admin] Release ID application",
)
def release_id_application_endpoint(request_id: int, db: Session = Depends(get_db)):
    return release_id_application(db, request_id)


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


@router.get(
    "/applications/{request_id}/download",
    summary="[Admin] Download the filled ID card docx",
    description=(
        "Returns the filled .docx file generated at release time. "
        "Returns 404 if the application has not been released yet or "
        "no template was uploaded when it was released."
    ),
)
def download_filled_id(request_id: int, db: Session = Depends(get_db)):
    req = db.query(DocumentRequest).filter(DocumentRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Application not found")
    if not req.request_file_path:
        raise HTTPException(
            status_code=404,
            detail="No filled ID document available. The application may not have been released yet."
        )
    pdf_path = BASE_DIR / req.request_file_path
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found on disk.")

    tx_no = req.transaction_no or f"request-{request_id}"
    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=f"BarangayID-{tx_no}.pdf",
    )


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

@router.post("/reports/bulk-undo", summary="[Admin] Bulk undo RFID reports")
def bulk_undo_rfid_reports_endpoint(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    results = {"reverted": [], "failed": []}
    for report_id in ids:
        try:
            undo_rfid_report(db, report_id)
            results["reverted"].append(report_id)
        except HTTPException:
            results["failed"].append(report_id)
    return {"detail": f"{len(results['reverted'])} reports reverted", **results}


@router.post("/reports/bulk-delete", summary="[Admin] Bulk delete RFID reports")
def bulk_delete_rfid_reports_endpoint(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    deleted_count = bulk_delete_rfid_reports(db, ids)
    return {"detail": f"{deleted_count} reports deleted"}


@router.post(
    "/reports/{report_id}/undo",
    summary="[Admin] Undo RFID report — reactivates the resident's RFID card",
)
def undo_rfid_report_endpoint(report_id: int, db: Session = Depends(get_db)):
    return undo_rfid_report(db, report_id)


@router.delete("/reports/{report_id}", summary="[Admin] Delete RFID report")
def delete_rfid_report_endpoint(report_id: int, db: Session = Depends(get_db)):
    if not delete_rfid_report(db, report_id):
        raise HTTPException(status_code=404, detail="Report not found")
    return {"detail": "Report deleted"}