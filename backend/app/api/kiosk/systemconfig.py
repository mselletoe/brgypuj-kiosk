# app/api/routes/kiosk/systemconfig.py

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.systemconfig_service import get_config, get_logo_bytes
from app.schemas.systemconfig import KioskSystemConfigRead

router = APIRouter(prefix="/settings")


@router.get("", response_model=KioskSystemConfigRead)
def get_kiosk_system_config(db: Session = Depends(get_db)):
    """
    Public endpoint — no auth required.
    Used by the kiosk to check maintenance mode, branding, and security settings.
    """
    return get_config(db)


@router.get("/logo")
def get_kiosk_brgy_logo(db: Session = Depends(get_db)):
    """
    Streams the barangay logo as a raw image. No auth required (public kiosk route).
    Returns 404 if no logo has been uploaded.
    """
    logo_bytes, content_type = get_logo_bytes(db)
    return Response(content=logo_bytes, media_type=content_type)