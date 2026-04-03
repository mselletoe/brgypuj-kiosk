"""
app/api/admin/documents.py

Router for admin document management.
Handles document type configuration, template uploads, request lifecycle
(approve, reject, release, payment, undo), PDF generation, and notes.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from fastapi.responses import StreamingResponse, FileResponse
from pathlib import Path
from io import BytesIO
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.websocket_manager import ws_manager
from app.schemas.document import (
    DocumentTypeAdminOut,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentRequestAdminOut,
    DocumentRequestAdminDetail,
    EligibilityCheckResult
)
from app.services.document_service import (
    bulk_undo_requests,
    get_all_document_types,
    create_document_type,
    get_resident_blotter_summary,
    release_request,
    update_document_type,
    get_all_document_requests,
    get_document_request_by_id,
    delete_document_type,
    get_document_type_with_file,
    upload_document_type_file,
    approve_request,
    reject_request,
    mark_request_paid,
    mark_request_unpaid,
    undo_request,
    delete_request,
    bulk_delete_requests,
    get_request_notes, 
    update_request_notes,
    regenerate_request_pdf,
    check_resident_eligibility
)
from app.services.document_service import PDF_STORAGE_DIR

router = APIRouter(prefix="/documents")


# =================================================================================
# INTERNAL HELPERS
# =================================================================================

def _format_request_for_admin(request):
    is_id_application = request.doctype_id is None

    if is_id_application:
        rfid_display = (request.form_data or {}).get("session_rfid", "Guest Mode")
        phone_number = request.resident.phone_number if request.resident else None
    else:
        rfid_display = "Guest Mode"
        phone_number = None
        if request.resident:
            active_rfid = next(
                (rfid.rfid_uid for rfid in request.resident.rfids if rfid.is_active),
                None
            )
            rfid_display = active_rfid if active_rfid else "No RFID"
            phone_number = request.resident.phone_number

    doctype_id   = request.doctype_id if not is_id_application else None
    doctype_name = "I.D Application" if is_id_application else (
        request.doctype.doctype_name if request.doctype else "Unknown"
    )

    return {
        "id": request.id,
        "transaction_no": request.transaction_no,
        "resident_id": request.resident_id,
        "resident_first_name": request.resident.first_name if request.resident else None,
        "resident_middle_name": request.resident.middle_name if request.resident else None,
        "resident_last_name": request.resident.last_name if request.resident else None,
        "resident_phone": phone_number,
        "resident_rfid": rfid_display,
        "doctype_id": doctype_id,
        "doctype_name": doctype_name,
        "price": request.price,
        "status": request.status,
        "payment_status": request.payment_status,
        "form_data": request.form_data,
        "notes": request.notes,
        "processed_by": request.processed_by,
        "requested_at": request.requested_at,
    }


# =================================================================================
# DOCUMENT TYPES
# =================================================================================
@router.get( "/types", response_model=list[DocumentTypeAdminOut], )
def list_document_types(db: Session = Depends(get_db),):
    return get_all_document_types(db)


@router.post(
    "/types",
    response_model=DocumentTypeAdminOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_type(payload: DocumentTypeCreate, db: Session = Depends(get_db)):
    result = create_document_type(db, payload)
    await ws_manager.broadcast_to_kiosk("document_types_updated", {
        "action": "created",
        "doctype_id": result.id,
        "doctype_name": result.doctype_name,
        "is_available": result.is_available,
        "price": float(result.price) if result.price is not None else None,
    })
    return result


@router.post("/types/bulk-delete", status_code=status.HTTP_200_OK)
async def bulk_delete_types(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    for id in ids:
        delete_document_type(db, id)
        await ws_manager.broadcast_to_kiosk("document_types_updated", {
            "action": "deleted",
            "doctype_id": id,
        })
    return {"detail": f"{len(ids)} document type(s) deleted"}


@router.put( "/types/{doctype_id}", response_model=DocumentTypeAdminOut, )
async def update_type(doctype_id: int, payload: DocumentTypeUpdate, db: Session = Depends(get_db)):
    updated = update_document_type(db, doctype_id, payload)
    if not updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document type not found")
    await ws_manager.broadcast_to_kiosk("document_types_updated", {
        "action": "updated",
        "doctype_id": updated.id,
        "doctype_name": updated.doctype_name,
        "is_available": updated.is_available,
        "price": float(updated.price) if updated.price is not None else None,
    })
    return updated


@router.delete( "/types/{doctype_id}", status_code=status.HTTP_204_NO_CONTENT, )
async def delete_type(doctype_id: int, db: Session = Depends(get_db)):
    deleted = delete_document_type(db, doctype_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document type not found")
    await ws_manager.broadcast_to_kiosk("document_types_updated", {
        "action": "deleted",
        "doctype_id": doctype_id,
    })


@router.get( "/types/{doctype_id}/file" )
def download_document_type_file(
    doctype_id: int,
    db: Session = Depends(get_db),
):
    doc = get_document_type_with_file(db, doctype_id)

    if not doc or not doc.file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found",
        )

    return StreamingResponse(
        BytesIO(doc.file),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{doc.doctype_name}.docx"'
        },
    )


@router.post( "/types/{doctype_id}/file", status_code=status.HTTP_204_NO_CONTENT, )
def upload_document_type_template(
    doctype_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith((".docx", ".pdf")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .docx or .pdf files are allowed",
        )

    success = upload_document_type_file(
        db=db,
        doctype_id=doctype_id,
        file_bytes=file.file.read(),
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found",
        )


# =================================================================================
# RESIDENT ELIGIBILITY
# =================================================================================
@router.get("/{resident_id}/blotter-summary")
def get_blotter_summary(resident_id: int, db: Session = Depends(get_db)):
    return get_resident_blotter_summary(db, resident_id)


@router.get( "/{resident_id}/eligibility/{doctype_id}", response_model=EligibilityCheckResult )
def admin_check_eligibility(resident_id: int, doctype_id: int, db: Session = Depends(get_db)):
    return check_resident_eligibility(db, resident_id=resident_id, doctype_id=doctype_id)


# =================================================================================
# DOCUMENT REQUESTS
# =================================================================================
@router.get( "/requests", response_model=list[DocumentRequestAdminOut], )
def list_document_requests(db: Session = Depends(get_db),):
    requests = get_all_document_requests(db)
    return [_format_request_for_admin(req) for req in requests]


@router.get( "/requests/{request_id}", response_model=DocumentRequestAdminDetail, )
def get_document_request(request_id: int, db: Session = Depends(get_db),):
    request = get_document_request_by_id(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    data = _format_request_for_admin(request)
    data["request_file_path"] = request.request_file_path
    
    return data


@router.get("/requests/{request_id}/pdf")
def view_request_pdf(request_id: int, db: Session = Depends(get_db)):
    request = get_document_request_by_id(db, request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    if not request.request_file_path:
        raise HTTPException(status_code=404, detail="No PDF generated yet")

    absolute_path = PDF_STORAGE_DIR / Path(request.request_file_path).relative_to("storage/documents")

    print("Absolute path being checked:", absolute_path)
    print("Exists?", absolute_path.exists())

    if not absolute_path.exists():
        raise HTTPException(status_code=404, detail="PDF file missing")

    return FileResponse(
        path=str(absolute_path),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=request_{request.transaction_no}.pdf"},
    )


@router.post("/requests/{request_id}/regenerate-pdf")
def regenerate_pdf(request_id: int, db: Session = Depends(get_db)):
    success = regenerate_request_pdf(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "PDF regenerated successfully"}


@router.post("/requests/{request_id}/approve")
def approve_document_request(request_id: int, db: Session = Depends(get_db)):
    success = approve_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "Request approved"}


@router.post("/requests/{request_id}/reject")
def reject_document_request(request_id: int, db: Session = Depends(get_db)):
    success = reject_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "Request rejected"}


@router.post("/requests/{request_id}/release")
def release_document_request(request_id: int, db: Session = Depends(get_db)):
    success = release_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "Request released"}


@router.post("/requests/{request_id}/mark-paid")
def mark_request_as_paid(request_id: int, db: Session = Depends(get_db)):
    success = mark_request_paid(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "Marked as paid"}


@router.post("/requests/{request_id}/mark-unpaid")
def mark_request_as_unpaid(request_id: int, db: Session = Depends(get_db)):
    success = mark_request_unpaid(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "Marked as unpaid"}


@router.post("/requests/{request_id}/undo")
def undo_document_request(request_id: int, db: Session = Depends(get_db)):
    try:
        success = undo_request(db, request_id)
        if not success:
            raise HTTPException(status_code=404, detail="Request not found")
        return {"detail": "Request status reverted"}
    except HTTPException:
        raise


@router.post("/requests/bulk-undo")
def bulk_undo_document_requests(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    updated_count = bulk_undo_requests(db, ids)
    return {"detail": f"{updated_count} requests reverted"}


@router.delete("/requests/{request_id}")
def delete_document_request(request_id: int, db: Session = Depends(get_db)):
    success = delete_request(db, request_id)
    if not success:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"detail": "Request deleted"}


@router.post("/requests/bulk-delete")
def bulk_delete_document_requests(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    deleted_count = bulk_delete_requests(db, ids)
    return {"detail": f"{deleted_count} requests deleted"}


# =================================================================================
# NOTES
# =================================================================================
@router.get("/requests/{request_id}/notes")
def get_notes(request_id: int, db: Session = Depends(get_db)):
    notes = get_request_notes(db, request_id)
    return {"notes": notes}


@router.put("/requests/{request_id}/notes")
def put_notes(request_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    updated_notes = update_request_notes(db, request_id, payload.get("notes", ""))
    return {"notes": updated_notes}