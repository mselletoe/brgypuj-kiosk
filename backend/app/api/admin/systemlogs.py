"""
Admin Audit / System Logs Routes
---------------------------------
Endpoints for the admin dashboard to query and filter system logs.
All routes require a valid admin JWT token.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import Optional
from datetime import datetime

from app.api.deps import get_db, get_current_admin
from app.models.admin import Admin
from app.models.systemlogs import SystemLog, LogSource, LogLevel, LogCategory
from app.schemas.systemlogs import SystemLogRead, SystemLogListResponse

router = APIRouter(prefix="/system-logs")


@router.get("/logs", response_model=SystemLogListResponse)
def get_system_logs(
    # ── Filters ───────────────────────────────────────────────
    source: Optional[LogSource] = Query(None, description="Filter by source: admin | kiosk | system"),
    level: Optional[LogLevel] = Query(None, description="Filter by level: info | warning | error | critical"),
    category: Optional[LogCategory] = Query(None, description="Filter by category"),
    actor_id: Optional[int] = Query(None, description="Filter by admin/actor ID"),
    target_type: Optional[str] = Query(None, description="Filter by affected record type"),
    target_id: Optional[int] = Query(None, description="Filter by affected record ID"),
    search: Optional[str] = Query(None, description="Search within action text"),
    date_from: Optional[datetime] = Query(None, description="Start of date range (ISO 8601)"),
    date_to: Optional[datetime] = Query(None, description="End of date range (ISO 8601)"),

    # ── Pagination ────────────────────────────────────────────
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Results per page"),

    # ── Dependencies ──────────────────────────────────────────
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Retrieve paginated system logs with optional filters.
    Accessible only by authenticated admins.
    """
    filters = []

    if source:
        filters.append(SystemLog.source == source)
    if level:
        filters.append(SystemLog.level == level)
    if category:
        filters.append(SystemLog.category == category)
    if actor_id:
        filters.append(SystemLog.actor_id == actor_id)
    if target_type:
        filters.append(SystemLog.target_type == target_type)
    if target_id:
        filters.append(SystemLog.target_id == target_id)
    if search:
        filters.append(SystemLog.action.ilike(f"%{search}%"))
    if date_from:
        filters.append(SystemLog.created_at >= date_from)
    if date_to:
        filters.append(SystemLog.created_at <= date_to)

    query = db.query(SystemLog)
    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    logs = (
        query
        .order_by(desc(SystemLog.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return SystemLogListResponse(
        total=total,
        page=page,
        page_size=page_size,
        results=logs,
    )


@router.get("/logs/{log_id}", response_model=SystemLogRead)
def get_log_detail(
    log_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """Retrieve a single log entry by ID."""
    log = db.query(SystemLog).filter(SystemLog.id == log_id).first()
    if not log:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log entry not found")
    return log


@router.get("/logs/summary/counts")
def get_log_summary(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Quick summary counts grouped by level.
    Useful for the dashboard stats cards (e.g. X errors today).
    """
    from sqlalchemy import func, cast, Date
    from datetime import date

    today = date.today()

    results = (
        db.query(SystemLog.level, func.count(SystemLog.id).label("count"))
        .filter(func.cast(SystemLog.created_at, Date) == today)
        .group_by(SystemLog.level)
        .all()
    )

    summary = {level.value: 0 for level in LogLevel}
    for row in results:
        summary[row.level.value] = row.count

    return {
        "date": str(today),
        "counts": summary,
        "total_today": sum(summary.values()),
    }