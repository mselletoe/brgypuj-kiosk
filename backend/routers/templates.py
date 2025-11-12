"""
================================================================================
File: templates.py
Description:
    This module manages the uploading, updating, retrieval, downloading, and
    deletion of document templates within the system.

    Templates represent pre-designed files (such as official document forms)
    that are linked to specific request types. Each template record may store:
      • Template name and description
      • File binary content and filename
      • Related request type (if applicable)
      • Metadata such as creation and update timestamps

    The routes provided here support:
      • Uploading and updating template files
      • Listing all templates with request type names
      • Downloading stored template files
      • Deleting templates from the database
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database import get_db
from models import Template, RequestType
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.responses import StreamingResponse
from io import BytesIO
import mimetypes

# ==================================
# Initialize Router
# ==================================
router = APIRouter(prefix="/templates", tags=["Templates"])

# ==================================
# Pydantic model for output
# ==================================
class TemplateOut(BaseModel):
    id: int
    template_name: str
    description: Optional[str] = None
    request_type_id: Optional[int] = None
    request_type_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Equivalent to orm_mode=True in Pydantic v1


# ==================================
# Get all templates
# ==================================
@router.get("/", response_model=List[TemplateOut])
def get_templates(db: Session = Depends(get_db)):
    templates = (
        db.query(Template, RequestType.request_type_name)
        .outerjoin(RequestType, Template.request_type_id == RequestType.id)
        .all()
    )

    # Format query results into JSON-serializable objects
    return [
        {
            "id": t.Template.id,
            "template_name": t.Template.template_name,
            "description": t.Template.description,
            "request_type_id": t.Template.request_type_id,
            "request_type_name": t.request_type_name,
            "created_at": t.Template.created_at,
            "updated_at": t.Template.updated_at,
        }
        for t in templates
    ]

# ==================================
# Upload a new template
# ==================================
@router.post("/", response_model=TemplateOut)
async def upload_template(
    template_name: str = Form(...),
    description: Optional[str] = Form(None),
    request_type_id: Optional[int] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()

    # Create a new template record
    new_template = Template(
        template_name=template_name,
        description=description,
        file=content,
        file_name=file.filename,
        request_type_id=request_type_id if request_type_id else None,
    )
    db.add(new_template)
    db.commit()
    db.refresh(new_template)

    # Retrieve related request type name for display
    request_type_name = None
    if request_type_id:
        req_type = db.query(RequestType).filter(RequestType.id == request_type_id).first()
        if req_type:
            request_type_name = req_type.request_type_name

    return {
        "id": new_template.id,
        "template_name": new_template.template_name,
        "description": new_template.description,
        "request_type_id": new_template.request_type_id,
        "request_type_name": request_type_name,
        "created_at": new_template.created_at,
        "updated_at": new_template.updated_at
    }

# ==================================
# Update existing template
# ==================================
@router.put("/{template_id}", response_model=TemplateOut)
async def update_template(
    template_id: int,
    template_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    request_type_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Update metadata fields if provided
    if template_name:
        template.template_name = template_name
    if description:
        template.description = description
    if request_type_id is not None:
        template.request_type_id = request_type_id
    if file:
        contents = await file.read()
        template.file = contents

    db.commit()
    db.refresh(template)

    # Fetch request type name for output
    request_type_name = None
    if template.request_type_id:
        req_type = db.query(RequestType).filter(RequestType.id == template.request_type_id).first()
        if req_type:
            request_type_name = req_type.request_type_name

    return {
        "id": template.id,
        "template_name": template.template_name,
        "description": template.description,
        "request_type_id": template.request_type_id,
        "request_type_name": request_type_name,
        "created_at": template.created_at,
        "updated_at": template.updated_at
    }

# ==================================
# Download template file
# ==================================
@router.get("/{template_id}/download")
def download_template(template_id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == template_id).first()
    if not template or not template.file:
        raise HTTPException(status_code=404, detail="File not found")

    file_stream = BytesIO(template.file)
    file_name = template.file_name or f"{template.template_name}.bin"

    import mimetypes
    mime_type, _ = mimetypes.guess_type(file_name)
    response = StreamingResponse(file_stream, media_type=mime_type or "application/octet-stream")
    response.headers["Content-Disposition"] = f"inline; filename={file_name}"
    return response

# ==================================
# Delete template
# ==================================
@router.delete("/{id}")
def delete_template(id: int, db: Session = Depends(get_db)):
    template = db.query(Template).filter(Template.id == id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"message": "Template deleted successfully"}