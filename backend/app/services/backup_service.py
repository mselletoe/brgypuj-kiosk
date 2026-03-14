"""
Backup Scheduler
----------------
Uses APScheduler to run pg_dump at the schedule stored in system_config.
Timezone is fixed to Asia/Manila (PH Time, UTC+8).
"""

import os
import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.db.session import SessionLocal
from app.services.systemconfig_service import get_config, set_last_backup
from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BACKUP_DIR = Path(settings.BACKUP_DIR)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

PH_TIMEZONE = "Asia/Manila"

_scheduler = BackgroundScheduler(timezone=PH_TIMEZONE)
_JOB_ID = "auto_backup"


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


def _do_backup() -> None:
    """Runs pg_dump and saves the result. Called by the scheduler."""
    print("✅ SCHEDULER FIRED", flush=True)
    logger.info("Scheduler triggered _do_backup()")
    db = SessionLocal()
    try:
        config = get_config(db)

        if config.backup_schedule == "manual":
            logger.info("Scheduled backup skipped — schedule is set to manual.")
            return

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename  = f"backup_auto_{timestamp}.sql"
        dest      = BACKUP_DIR / filename

        db_info = _parse_db_url(settings.DATABASE_URL)
        env = os.environ.copy()
        env["PGPASSWORD"] = db_info["password"]

        result = subprocess.run(
            [
                "pg_dump",
                "-h", db_info["host"],
                "-p", db_info["port"],
                "-U", db_info["user"],
                "-F", "p",
                "-f", str(dest),
                db_info["dbname"],
            ],
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error("Scheduled pg_dump failed: %s", result.stderr.strip())
            return

        logger.info("Scheduled backup saved: %s", dest)
        set_last_backup(db)

        # Prune old auto backups — keep last 30
        auto_files = sorted(BACKUP_DIR.glob("backup_auto_*.sql"), reverse=True)
        for old in auto_files[30:]:
            old.unlink(missing_ok=True)
            logger.info("Pruned old backup: %s", old.name)

    except Exception as exc:
        logger.exception("Unexpected error during scheduled backup: %s", exc)
    finally:
        db.close()


def _build_trigger(schedule: str, backup_time: str) -> CronTrigger:
    """
    Converts schedule + backup_time (HH:MM, PH time) into a CronTrigger.
    The scheduler itself runs in Asia/Manila so no offset conversion needed.
    """
    try:
        hour, minute = backup_time.split(":")
    except (ValueError, AttributeError):
        hour, minute = "2", "0"

    if schedule == "daily":
        return CronTrigger(hour=int(hour), minute=int(minute), timezone=PH_TIMEZONE)
    elif schedule == "weekly":
        return CronTrigger(day_of_week="mon", hour=int(hour), minute=int(minute), timezone=PH_TIMEZONE)
    else:
        # manual — job still exists but skips inside _do_backup
        return CronTrigger(hour=int(hour), minute=int(minute), timezone=PH_TIMEZONE)


def _reschedule() -> None:
    db = SessionLocal()
    try:
        config = get_config(db)
        schedule    = config.backup_schedule or "manual"
        backup_time = config.backup_time or "02:00"
    finally:
        db.close()

    trigger = _build_trigger(schedule, backup_time)

    if _scheduler.get_job(_JOB_ID):
        _scheduler.reschedule_job(_JOB_ID, trigger=trigger)
        logger.info("Backup job rescheduled: %s @ %s PHT", schedule, backup_time)
    else:
        _scheduler.add_job(
            _do_backup,
            trigger=trigger,
            id=_JOB_ID,
            replace_existing=True,
            misfire_grace_time=3600,
        )
        logger.info("Backup job added: %s @ %s PHT", schedule, backup_time)


def start_scheduler() -> None:
    """Call on FastAPI startup."""
    _reschedule()
    _scheduler.start()

    # Debug: show next run time
    job = _scheduler.get_job(_JOB_ID)
    if job:
        print(f"✅ Next backup scheduled at: {job.next_run_time}", flush=True)
    else:
        print("❌ No backup job found!", flush=True)

    logger.info("Backup scheduler started (timezone: %s).", PH_TIMEZONE)


def stop_scheduler() -> None:
    """Call on FastAPI shutdown."""
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("Backup scheduler stopped.")


def apply_new_schedule() -> None:
    """Call from settings PATCH endpoint after saving backup_schedule/backup_time."""
    if _scheduler.running:
        _reschedule()
        job = _scheduler.get_job(_JOB_ID)
        if job:
            print(f"✅ Backup rescheduled. Next run: {job.next_run_time}", flush=True)