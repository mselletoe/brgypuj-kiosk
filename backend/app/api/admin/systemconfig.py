"""
app/api/admin/systemconfig.py

Router for barangay system configuration management.
Handles reading and patching system settings, uploading, retrieving,
and deleting the barangay logo, and broadcasting config changes to the kiosk.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.websocket_manager import ws_manager
from app.api.deps import get_db, get_current_admin
from app.models.admin import Admin
from app.schemas.systemconfig import SystemConfigRead, SystemConfigUpdate
from app.services.systemconfig_service import get_config, update_config
from app.services.backup_service import apply_new_schedule

router = APIRouter(prefix="/settings")

ALLOWED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/svg+xml"}
MAX_LOGO_SIZE_MB = 2


# =================================================================================
# SYSTEM CONFIGURATION
# =================================================================================

@router.get("", response_model=SystemConfigRead)
def get_system_config(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    return get_config(db)


@router.patch("", response_model=SystemConfigRead)
async def patch_system_config(
    data: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    result = update_config(db, data)

    if data.backup_schedule is not None or data.backup_time is not None:
        apply_new_schedule()

    await ws_manager.broadcast_to_kiosk("config_updated", {
        "brgy_name":            result.brgy_name,
        "brgy_subname":         result.brgy_subname,
        "has_logo":             result.has_logo,
        "maintenance_mode":     result.maintenance_mode,
        "maintenance_message":  result.maintenance_message,
        "auto_logout_duration": result.auto_logout_duration,
    })
    return result


# =================================================================================
# BARANGAY LOGO
# =================================================================================

@router.put("/logo", status_code=204)
async def upload_brgy_logo(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type. Allowed: PNG, JPEG, WebP, SVG")

    contents = await file.read()
    if len(contents) / (1024 * 1024) > MAX_LOGO_SIZE_MB:
        raise HTTPException(status_code=413, detail=f"File too large. Max size is {MAX_LOGO_SIZE_MB} MB.")

    config = get_config(db)
    config.brgy_logo = contents
    config.brgy_logo_content_type = file.content_type
    db.commit()

    await ws_manager.broadcast_to_kiosk("config_updated", {"has_logo": True})


@router.get("/logo")
def get_brgy_logo(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    config = get_config(db)
    if not config.brgy_logo:
        raise HTTPException(status_code=404, detail="No logo uploaded.")
    content_type = getattr(config, "brgy_logo_content_type", None) or "image/png"
    return Response(content=config.brgy_logo, media_type=content_type)


@router.delete("/logo", status_code=204)
async def delete_brgy_logo(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    config = get_config(db)
    config.brgy_logo = None
    config.brgy_logo_content_type = None
    db.commit()

    await ws_manager.broadcast_to_kiosk("config_updated", {"has_logo": False})