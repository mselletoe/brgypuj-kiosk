import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.models.admin import Admin
from app.services.systemconfig_service import set_last_backup
from app.core.config import settings

router = APIRouter(prefix="/backup")

BACKUP_DIR = Path(settings.BACKUP_DIR)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

def _parse_db_url(url: str) -> dict:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return {
        "user":     parsed.username or "postgres",
        "password": parsed.password or "",
        "host":     parsed.hostname or "localhost",
        "port":     str(parsed.port or 5432),
        "dbname":   parsed.path.lstrip("/"),
    }


def _run_pg_dump(dest_path: Path) -> None:
    db = _parse_db_url(settings.DATABASE_URL)
    env = os.environ.copy()
    env["PGPASSWORD"] = db["password"]

    result = subprocess.run(
        [
            "pg_dump",
            "-h", db["host"],
            "-p", db["port"],
            "-U", db["user"],
            "-F", "p",          # plain SQL
            "-f", str(dest_path),
            db["dbname"],
        ],
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"pg_dump failed: {result.stderr.strip()}")


@router.post("", status_code=200)
def trigger_manual_backup(
    db: Session = Depends(get_db),
    _admin: Admin = Depends(get_current_admin),
):
    timestamp   = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename    = f"backup_manual_{timestamp}.sql"
    saved_path  = BACKUP_DIR / filename

    try:
        _run_pg_dump(saved_path)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        )

    set_last_backup(db)

    def iterfile():
        with open(saved_path, "rb") as f:
            yield from f

    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Backup-Filename": filename,
        },
    )


@router.get("/history")
def list_backup_history(
    _admin: Admin = Depends(get_current_admin),
):
    files = sorted(BACKUP_DIR.glob("backup_*.sql"), reverse=True)
    history = []
    for f in files:
        stat = f.stat()
        size_bytes = stat.st_size
        if size_bytes >= 1_048_576:
            size_str = f"{size_bytes / 1_048_576:.1f} MB"
        elif size_bytes >= 1024:
            size_str = f"{size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{size_bytes} B"

        btype = "auto" if "_auto_" in f.name else "manual"

        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        history.append({
            "filename": f.name,
            "type":     btype,
            "size":     size_str,
            "size_bytes": size_bytes,
            "created_at": mtime.isoformat(),
            "status":   "success", 
        })

    return history


@router.get("/download/{filename}")
def download_backup(
    filename: str,
    _admin: Admin = Depends(get_current_admin),
):
    safe = BACKUP_DIR / Path(filename).name
    if not safe.exists() or not safe.is_file():
        raise HTTPException(status_code=404, detail="Backup file not found.")

    return FileResponse(
        path=str(safe),
        media_type="application/octet-stream",
        filename=filename,
    )


@router.post("/restore", status_code=200)
async def restore_backup(
    file: UploadFile = File(...),
    _admin: Admin = Depends(get_current_admin),
):
    if not file.filename.endswith(".sql"):
        raise HTTPException(status_code=400, detail="Only .sql files are accepted.")

    db_info = _parse_db_url(settings.DATABASE_URL)
    env = os.environ.copy()
    env["PGPASSWORD"] = db_info["password"]

    with tempfile.NamedTemporaryFile(suffix=".sql", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = subprocess.run(
            [
                "psql",
                "-h", db_info["host"],
                "-p", db_info["port"],
                "-U", db_info["user"],
                "-d", db_info["dbname"],
                "-f", tmp_path,
            ],
            env=env,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail=f"Restore failed: {result.stderr.strip()}"
            )
    finally:
        os.unlink(tmp_path)

    return {"detail": "Database restored successfully."}