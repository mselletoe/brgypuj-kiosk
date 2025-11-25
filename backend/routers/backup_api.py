from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from services.backup_service import create_backup
from pathlib import Path

router = APIRouter(prefix="/backup", tags=["Backup"])

@router.post("/run")
async def run_backup():
    """
    Trigger a PostgreSQL backup and stream the file to the frontend.
    """
    try:
        backup_path: Path = create_backup()
        return FileResponse(
            backup_path,
            media_type="application/octet-stream",
            filename=backup_path.name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {e}")
