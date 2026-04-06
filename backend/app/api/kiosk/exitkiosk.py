import subprocess
from fastapi import APIRouter

router = APIRouter()

@router.post("/system/exit-kiosk")
async def exit_kiosk():
    try:
        subprocess.run(["pkill", "-f", "chromium"], capture_output=True)
        return {"status": "ok", "message": "Kiosk exiting"}
    except Exception as e:
        return {"status": "error", "message": str(e)}