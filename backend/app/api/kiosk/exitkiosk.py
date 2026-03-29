import subprocess
from fastapi import APIRouter

router = APIRouter()

@router.post("/system/exit-kiosk")
async def exit_kiosk():
    """
    Exit Kiosk Mode.

    Kills the Chromium browser process running in kiosk mode on the
    Raspberry Pi, returning the display to the desktop.

    Returns:
        dict: A status message confirming the exit command was sent.
    """
    try:
        subprocess.run(["pkill", "-f", "chromium"], capture_output=True)
        return {"status": "ok", "message": "Kiosk exiting"}
    except Exception as e:
        return {"status": "error", "message": str(e)}