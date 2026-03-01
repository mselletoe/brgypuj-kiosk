from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.models.audit import AdminAuditLog
from app.schemas.audit import AuditLogOut, AuditLogCreate

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])

@router.get("", response_model=list[AuditLogOut])
def get_audit_logs(db: Session = Depends(get_db)):
    # Gets the 100 most recent logs
    return db.query(AdminAuditLog).order_by(AdminAuditLog.created_at.desc()).limit(100).all()

@router.post("", response_model=AuditLogOut)
def create_audit_log(log_in: AuditLogCreate, db: Session = Depends(get_db)):
    new_log = AdminAuditLog(
        action=log_in.action,
        details=log_in.details,
        entity_type=log_in.entity_type,
        admin_id=log_in.admin_id
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log