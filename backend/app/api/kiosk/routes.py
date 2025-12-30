from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def kiosk_health():
    return {"status": "kiosk ok"}
