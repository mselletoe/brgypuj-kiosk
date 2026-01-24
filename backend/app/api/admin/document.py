"""
Document Administration API
---------------------------
Provides management endpoints for document type templates and resident 
request monitoring within the administrative dashboard.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
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
    get_all_document_types,
    create_document_type,
    update_document_type,
    get_all_document_requests,
    get_document_request_by_id,
    delete_document_type,
    get_document_type_with_file,
    upload_document_type_file,
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

@router.get(
    "/requests",
    response_model=list[DocumentRequestAdminOut],
)
def list_document_requests( db: Session = Depends(get_db),):
    """
    Lists all document requests submitted by residents for administrative review.
    """
    return get_all_document_requests(db)


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
    return request