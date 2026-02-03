"""
Document Administration API
---------------------------
Provides management endpoints for document type templates and resident 
request monitoring within the administrative dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Body
from fastapi.responses import StreamingResponse
from io import BytesIO
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.document import (
    DocumentTypeAdminOut,
    DocumentTypeCreate,
    DocumentTypeUpdate,
    DocumentRequestAdminOut,
    DocumentRequestAdminDetail,
    DocumentTypeProcessingOut
)
from app.services.document_service import (
    bulk_undo_requests,
    get_all_document_types,
    create_document_type,
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
    update_request_notes
)

router = APIRouter(prefix="/documents")


# =========================================================
# DOCUMENT TYPES 
# =========================================================

@router.get(
    "/types",
    response_model=list[DocumentTypeAdminOut],
)
def list_document_types(db: Session = Depends(get_db),):
    """
    Retrieves a comprehensive list of all document types, including 
    those currently marked as unavailable.
    """
    return get_all_document_types(db)


@router.post(
    "/types",
    response_model=DocumentTypeAdminOut,
    status_code=status.HTTP_201_CREATED,
)
def create_type(payload: DocumentTypeCreate, db: Session = Depends(get_db),):
    """
    Configures a new document type template with dynamic field definitions.
    """
    return create_document_type(db, payload)


@router.put(
    "/types/{doctype_id}",
    response_model=DocumentTypeAdminOut,
)
def update_type(
    doctype_id: int,
    payload: DocumentTypeUpdate,
    db: Session = Depends(get_db),
):
    """
    Updates configuration, pricing, or field requirements for an existing document type.
    """
    updated = update_document_type(db, doctype_id, payload)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found",
        )
    return updated


@router.delete(
    "/types/{doctype_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_type(doctype_id: int, db: Session = Depends(get_db)):
    deleted = delete_document_type(db, doctype_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document type not found",
        )


@router.get(
    "/types/{doctype_id}/file",
)
def download_document_type_file(
    doctype_id: int,
    db: Session = Depends(get_db),
):
    """
    Downloads the document template file for a specific document type.
    """
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


@router.post(
    "/types/{doctype_id}/file",
    status_code=status.HTTP_204_NO_CONTENT,
)
def upload_document_type_template(
    doctype_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Uploads or replaces the document template file for a document type.
    """
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


# =========================================================
# DOCUMENT REQUESTS 
# =========================================================

def _format_request_for_admin(request):
    """Helper to format request with resident data"""
    # Get the active RFID UID if resident exists
    rfid_display = "Guest Mode"
    phone_number = None

    if request.resident:
        # Get the active RFID from the relationship
        active_rfid = next(
            (rfid.rfid_uid for rfid in request.resident.rfids if rfid.is_active),
            None
        )
        rfid_display = active_rfid if active_rfid else "No RFID"
        phone_number = request.resident.phone_number

    return {
        "id": request.id,
        "transaction_no": request.transaction_no,
        "resident_id": request.resident_id,
        "resident_first_name": request.resident.first_name if request.resident else None,
        "resident_middle_name": request.resident.middle_name if request.resident else None,
        "resident_last_name": request.resident.last_name if request.resident else None,
        "resident_phone": phone_number,
        "resident_rfid": rfid_display,
        "doctype_id": request.doctype_id,
        "doctype_name": request.doctype.doctype_name,
        "price": request.price,
        "status": request.status,
        "payment_status": request.payment_status,
        "form_data": request.form_data,
        "notes": request.notes,
        "processed_by": request.processed_by,
        "requested_at": request.requested_at,
    }


@router.get(
    "/requests",
    response_model=list[DocumentRequestAdminOut],
)
def list_document_requests(db: Session = Depends(get_db),):
    """
    Lists all document requests submitted by residents for administrative review.
    Includes both regular document requests and RFID requests.
    """
    requests = get_all_document_requests(db)
    return [_format_request_for_admin(req) for req in requests]


@router.get(
    "/requests/{request_id}",
    response_model=DocumentRequestAdminDetail,
)
def get_document_request(request_id: int, db: Session = Depends(get_db),):
    """
    Fetches the complete details of a specific request, including submitted form data.
    """
    request = get_document_request_by_id(db, request_id)
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found",
        )
    
    data = _format_request_for_admin(request)
    data["request_file_path"] = request.request_file_path
    
    return data


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
    """
    Reverts a request to its previous status in the workflow:
    - Approved → Pending
    - Released → Approved  
    - Rejected → Pending
    """
    try:
        success = undo_request(db, request_id)
        if not success:
            raise HTTPException(status_code=404, detail="Request not found")
        return {"detail": "Request status reverted"}
    except HTTPException:
        raise


@router.post("/requests/bulk-undo")
def bulk_undo_document_requests(ids: list[int] = Body(...), db: Session = Depends(get_db)):
    """
    Bulk undo operation for multiple requests.
    Returns count of successfully reverted requests.
    """
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


@router.get("/requests/{request_id}/notes")
def get_notes(request_id: int, db: Session = Depends(get_db)):
    notes = get_request_notes(db, request_id)
    return {"notes": notes}


@router.put("/requests/{request_id}/notes")
def put_notes(request_id: int, payload: dict = Body(...), db: Session = Depends(get_db)):
    updated_notes = update_request_notes(db, request_id, payload.get("notes", ""))
    return {"notes": updated_notes}