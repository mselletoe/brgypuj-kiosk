"""
System Config Routes
--------------------
GET   /admin/settings        → fetch full config (all tabs read from this)
PATCH /admin/settings        → partial update (each tab sends only its fields)
PUT   /admin/settings/logo   → upload brgy logo (multipart/form-data) — stored as bytes in DB
GET   /admin/settings/logo   → serve brgy logo as raw image response
DELETE /admin/settings/logo  → remove brgy logo

All routes require a valid admin JWT.
PATCH and logo mutation routes require superadmin.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.models.admin import Admin
from app.schemas.systemconfig import SystemConfigRead, SystemConfigUpdate
from app.services.systemconfig_service import get_config, update_config

router = APIRouter(prefix="/settings")

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}
MAX_LOGO_SIZE_MB = 2


# ── GET /admin/settings ───────────────────────────────────────────────────────

@router.get("", response_model=SystemConfigRead)
def get_system_config(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """Returns the full system config. Readable by any authenticated admin."""
    return get_config(db)


# ── PATCH /admin/settings ─────────────────────────────────────────────────────

@router.patch("", response_model=SystemConfigRead)
def patch_system_config(
    data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Partial update — only the fields you send are changed.
    Each settings tab sends only the fields it manages.
    Requires superadmin.
    """
    return update_config(db, data)


# ── PUT /admin/settings/logo ──────────────────────────────────────────────────

@router.put("/logo", status_code=204)
async def upload_brgy_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Upload or replace the barangay logo.
    Accepts PNG, JPEG, WebP, or SVG. Max 2 MB.
    Stores raw bytes directly in the DB — no folder created.
    Returns 204 No Content on success.
    """
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Allowed: PNG, JPEG, WebP, SVG",
        )

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_LOGO_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size is {MAX_LOGO_SIZE_MB} MB.",
        )

    config = get_config(db)
    config.brgy_logo = contents
    config.brgy_logo_content_type = file.content_type
    db.commit()


# ── GET /admin/settings/logo ──────────────────────────────────────────────────

@router.get("/logo")
def get_brgy_logo(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Streams the barangay logo as a raw image response.
    Returns 404 if no logo has been uploaded yet.
    """
    config = get_config(db)
    if not config.brgy_logo:
        raise HTTPException(status_code=404, detail="No logo uploaded.")
    content_type = getattr(config, "brgy_logo_content_type", None) or "image/png"
    return Response(content=config.brgy_logo, media_type=content_type)


# ── DELETE /admin/settings/logo ───────────────────────────────────────────────

@router.delete("/logo", status_code=204)
def delete_brgy_logo(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """Removes the barangay logo."""
    config = get_config(db)
    config.brgy_logo = None
    config.brgy_logo_content_type = None
    db.commit()