"""
System Config Routes
--------------------
GET  /admin/settings        → fetch full config (all tabs read from this)
PATCH /admin/settings       → partial update (each tab sends only its fields)
POST /admin/settings/logo   → upload brgy logo (multipart/form-data)

All routes require a valid admin JWT.
PATCH and logo upload require superadmin.
"""

import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin, require_superadmin
from app.models.admin import Admin
from app.schemas.systemconfig import SystemConfigRead, SystemConfigUpdate
from app.services.systemconfig_service import get_config, update_config, set_logo_path

router = APIRouter(prefix="/settings")

# Where uploaded logos are saved — adjust to your static files directory
LOGO_UPLOAD_DIR = "uploads/logos"
os.makedirs(LOGO_UPLOAD_DIR, exist_ok=True)

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}
MAX_LOGO_SIZE_MB = 2


# ── GET /admin/settings ───────────────────────────────────────────────────────

@router.get("", response_model=SystemConfigRead)
def get_system_config(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Returns the full system config.
    Readable by any authenticated admin.
    """
    return get_config(db)


# ── PATCH /admin/settings ─────────────────────────────────────────────────────

@router.patch("", response_model=SystemConfigRead)
def patch_system_config(
    data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """
    Partial update — only the fields you send are changed.
    Each settings tab sends only the fields it manages.
    Requires superadmin.
    """
    return update_config(db, data)


# ── POST /admin/settings/logo ─────────────────────────────────────────────────

@router.post("/logo", response_model=SystemConfigRead)
async def upload_brgy_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """
    Upload a new barangay logo.
    Accepts PNG, JPEG, WebP, or SVG. Max 2 MB.
    Returns the updated config with the new logo path.
    """
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type. Allowed: PNG, JPEG, WebP, SVG",
        )

    # Read and validate size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_LOGO_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {MAX_LOGO_SIZE_MB} MB.",
        )

    # Save with a unique filename to avoid cache issues
    ext = os.path.splitext(file.filename or "logo.png")[1] or ".png"
    filename = f"brgy_logo_{uuid.uuid4().hex[:8]}{ext}"
    save_path = os.path.join(LOGO_UPLOAD_DIR, filename)

    with open(save_path, "wb") as f:
        f.write(contents)

    # Store the relative path (serve via your static files mount)
    logo_url_path = f"/uploads/logos/{filename}"
    return set_logo_path(db, logo_url_path)