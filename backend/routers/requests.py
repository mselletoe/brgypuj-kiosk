"""
================================================================================
File: requests.py
Description:
    This router manages document requests (e.g., Barangay Clearance, Indigency).
    It handles the full lifecycle from creation to document generation and completion.

    Key Features:
    1. Automated Document Generation:
       - Uses 'docxtpl' to fill MS Word templates with user submitted form data.
       - Uses 'LibreOffice' (headless mode) to convert the filled DOCX to PDF.
       - Stores the generated PDF binary directly in the database.

    2. Request Lifecycle Management:
       - Tracks status (Pending, Processing, Released, etc.).
       - Manages Payment Status (Paid/Unpaid).
       - Enforces rules (e.g., cannot approve if unpaid).

    3. File Delivery:
       - Provides an endpoint to download the generated PDF directly.
================================================================================
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from database import get_db
from models import Request, RequestStatus, RequestType, Template
from pydantic import BaseModel
from typing import Optional, Dict, Any
from sqlalchemy import func
from fastapi.responses import StreamingResponse
import io
import subprocess
import tempfile
import os
import platform
from auth_utils import get_current_user, get_optional_user

router = APIRouter(prefix="/requests", tags=["Requests"])

# ----------------------------
# Pydantic Schemas
# ----------------------------
class RequestCreate(BaseModel):
    request_type_id: int
    form_data: Optional[Dict[str, Any]] = {}

    class Config:
        extra = "allow"

class RequestOut(BaseModel):
    id: int
    resident_id: Optional[int]
    request_type_id: Optional[int] = None
    document_type: str
    price: int
    form_data: Optional[Dict[str, Any]] = {}
    status: str
    created_at: str
    payment_status: Optional[str] = "Unpaid"
    requested_via: str  # "RFID" or "Guest"
    requester_name: Optional[str] = None
    rfid_uid: Optional[str] = None

# Pydantic model for updating status
class StatusUpdateSchema(BaseModel):
    status_name: str

# ----------------------------
# Helper to get or create status
# ----------------------------
def get_status(db: Session, name: str):
    status = db.query(RequestStatus).filter_by(name=name).first()
    if not status:
        status = RequestStatus(name=name)
        db.add(status)
        db.commit()
        db.refresh(status)
    return status

# ----------------------------
# Helper to convert DOCX to PDF using LibreOffice
# ----------------------------
def convert_docx_to_pdf(docx_bytes: bytes) -> bytes:
    """
    Convert DOCX bytes to PDF bytes using LibreOffice.
    Works on both Windows and Linux (Raspberry Pi).
    """
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save DOCX to temp file
        docx_path = os.path.join(temp_dir, "document.docx")
        with open(docx_path, "wb") as f:
            f.write(docx_bytes)
        
        # Determine LibreOffice command based on platform
        system = platform.system()
        if system == "Windows":
            # Common LibreOffice paths on Windows
            libreoffice_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
            soffice_cmd = None
            for path in libreoffice_paths:
                if os.path.exists(path):
                    soffice_cmd = path
                    break
            if not soffice_cmd:
                raise Exception("LibreOffice not found on Windows. Please install it.")
        else:  # Linux (Raspberry Pi)
            soffice_cmd = "soffice"
        
        # Convert DOCX to PDF using LibreOffice
        try:
            subprocess.run(
                [
                    soffice_cmd,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", temp_dir,
                    docx_path
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )
        except subprocess.CalledProcessError as e:
            raise Exception(f"LibreOffice conversion failed: {e.stderr.decode()}")
        except FileNotFoundError:
            raise Exception("LibreOffice not found. Install with: sudo apt-get install libreoffice")
        
        # Read the generated PDF
        pdf_path = os.path.join(temp_dir, "document.pdf")
        if not os.path.exists(pdf_path):
            raise Exception("PDF file was not generated")
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
        
        return pdf_bytes

# ----------------------------
# Create a new request and auto-fill document
# ----------------------------
@router.post("/", response_model=RequestOut)
def create_request(req: RequestCreate, user = Depends(get_optional_user), db: Session = Depends(get_db)):
    pending_status = get_status(db, "pending") 

    # Verify request type exists
    request_type = db.query(RequestType).filter_by(id=req.request_type_id).first()
    if not request_type:
        raise HTTPException(status_code=404, detail="Request type not found")

    # Extract authentication info from token
    resident_id = user.get("resident_id") if user else None
    login_method = user.get("login_method") if user else "guest"
    requester_name = user.get("name") if user else "Guest User"
    rfid_uid = user.get("rfid_uid") if user else None

    requested_via = "RFID" if login_method == "rfid" and resident_id else "Guest"

    # 1Create the new request
    new_request = Request(
        resident_id=resident_id,
        request_type_id=req.request_type_id,
        status_id=pending_status.id,
        form_data=req.form_data,
        payment_status="Unpaid",
    )
    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    # Auto-fill document template and convert to PDF
    try:
        # Find template linked to request_type
        template = db.query(Template).filter(Template.request_type_id == req.request_type_id).first()
        if template and template.file:
            from docxtpl import DocxTemplate

            # Merge authentication info into form_data for template
            template_data = req.form_data.copy() if req.form_data else {}
            template_data.update({
                "requester_name": requester_name,
                "requested_via": requested_via,
                "rfid_uid": rfid_uid or "N/A",
            })

            # Render the DOCX template with form data
            tpl = DocxTemplate(io.BytesIO(template.file))
            tpl.render(req.form_data or {})

            # Save rendered DOCX to bytes
            docx_stream = io.BytesIO()
            tpl.save(docx_stream)
            docx_bytes = docx_stream.getvalue()

            # Convert DOCX to PDF
            pdf_bytes = convert_docx_to_pdf(docx_bytes)
            
            # Save PDF to database
            new_request.request_file = pdf_bytes

            # Make sure SQLAlchemy tracks the change
            db.add(new_request)
            db.commit()
            db.refresh(new_request)
            print(f"✅ Auto-filled PDF saved for request {new_request.id}")

        else:
            print(f"❌ No template found for request_type_id {req.request_type_id}")

    except Exception as e:
        print(f"❌ Auto-fill failed for request {new_request.id}: {e}")
        # Don't raise exception - allow request to be created even if PDF generation fails
        # You can choose to raise HTTPException here if PDF generation is critical

    # Return the request info
    return {
        "id": new_request.id,
        "resident_id": new_request.resident_id,
        "request_type_id": new_request.request_type_id,
        "document_type": request_type.request_type_name,
        "price": request_type.price,
        "form_data": new_request.form_data,
        "status": pending_status.name,
        "created_at": new_request.created_at.isoformat(),
        "payment_status": new_request.payment_status,
        "requested_via": requested_via,
        "requester_name": requester_name,
        "rfid_uid": rfid_uid,
    }

# ----------------------------
# Download generated PDF
# ----------------------------
@router.get("/{request_id}/download-pdf")
def download_pdf(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if not req.request_file:
        raise HTTPException(status_code=404, detail="No document file found for this request")
    
    # Return PDF as downloadable file
    return StreamingResponse(
        io.BytesIO(req.request_file),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=request_{request_id}.pdf"}
    )

# ----------------------------
# Get all requests
# ----------------------------
@router.get("/", response_model=list[RequestOut])
def get_requests(db: Session = Depends(get_db)):
    results = db.query(Request).options(
        joinedload(Request.request_type),
        joinedload(Request.resident),
    ).all()
    
    output = []
    for r in results:
        # Determine authentication method
        if r.resident_id:
            # RFID user - fetch their info
            resident = r.resident
            requester_name = f"{resident.first_name} {resident.last_name}" if resident else "Unknown User"
            requested_via = "RFID"
            
            # Get RFID UID if available
            rfid_uid = None
            if resident and resident.rfid:
                rfid_uid = resident.rfid.rfid_uid
        else:
            # Guest user
            requester_name = "Guest User"
            requested_via = "Guest"
            rfid_uid = None
        
        output.append({
            "id": r.id,
            "resident_id": r.resident_id,
            "request_type_id": r.request_type_id,
            "document_type": r.request_type.request_type_name if r.request_type else "Unknown",
            "price": r.request_type.price if r.request_type else 0,
            "form_data": r.form_data,
            "status": r.status_obj.name if r.status_obj else None,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "payment_status": r.payment_status,
            "requested_via": requested_via,
            "requester_name": requester_name,
            "rfid_uid": rfid_uid,
        })
    
    return output

# ----------------------------
# Toggle Payment Status (Paid / Unpaid)
# ----------------------------
@router.put("/{request_id}/payment")
def toggle_payment_status(request_id: int, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    req.payment_status = "Paid" if req.payment_status != "Paid" else "Unpaid"
    req.updated_at = func.now()

    db.commit()
    db.refresh(req)

    return {"message": "Payment status updated", "payment_status": req.payment_status}

# ----------------------------
# Update Request Status (Generic)
# ----------------------------
@router.put("/{request_id}/status")  
def update_request_status(request_id: int, payload: StatusUpdateSchema, db: Session = Depends(get_db)):
    req = db.query(Request).filter(Request.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")

    status = get_status(db, payload.status_name)
    req.status_id = status.id
    req.updated_at = func.now()

    db.commit()
    db.refresh(req)

    return {"message": f"Request status updated to '{payload.status_name}'", "status": payload.status_name}