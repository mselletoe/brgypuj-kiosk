from fastapi import APIRouter
from app.api.kiosk import auth

router = APIRouter()

router.include_router(auth.router)

@router.get("/health")
def kiosk_health():
    return {"status": "kiosk ok"}