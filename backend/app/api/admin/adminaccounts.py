"""
Admin Accounts Router  (superadmin only)
-----------------------------------------
All routes are prefixed with /admin/accounts via the main app router include.

Route map:
  GET    /                        — list all admin accounts
  GET    /{admin_id}/photo        — serve an admin's profile photo
  PATCH  /{admin_id}/status       — activate / deactivate
  PATCH  /{admin_id}/role         — change system_role
  DELETE /{admin_id}              — permanently delete

Account *creation* reuses POST /admin/auth/register (auth router).
"""

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_superadmin
from app.models.admin import Admin
from app.schemas.adminaccounts import (
    AdminAccountListItem,
    AdminSetStatusRequest,
    AdminSetStatusResponse,
    AdminSetRoleRequest,
    AdminSetRoleResponse,
    AdminDeleteResponse,
)
from app.services.adminaccounts_service import (
    list_all_admins,
    set_admin_active_status,
    update_admin_role,
    delete_admin_account,
)
from app.api.deps import get_db   # adjust import path to match your project

router = APIRouter(prefix="/accounts")


# ── GET /admin/accounts ───────────────────────────────────────────────────────

@router.get("", response_model=list[AdminAccountListItem])
def get_all_admins(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """Returns all admin accounts. Superadmin only."""
    return list_all_admins(db)


# ── GET /admin/accounts/{admin_id}/photo ──────────────────────────────────────

@router.get("/{admin_id}/photo")
def get_admin_photo(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """Streams the target admin's profile photo. Returns 404 if none uploaded."""
    from fastapi import HTTPException, status as http_status
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Admin not found")
    if not admin.photo:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="No photo uploaded")
    return Response(content=admin.photo, media_type="image/jpeg")


# ── PATCH /admin/accounts/{admin_id}/status ───────────────────────────────────

@router.patch("/{admin_id}/status", response_model=AdminSetStatusResponse)
def patch_admin_status(
    admin_id: int,
    payload: AdminSetStatusRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """Activates or deactivates an admin account. Superadmin only."""
    return set_admin_active_status(
        db,
        target_admin_id=admin_id,
        is_active=payload.is_active,
        requesting_admin_id=current_admin.id,
    )


# ── PATCH /admin/accounts/{admin_id}/role ─────────────────────────────────────

@router.patch("/{admin_id}/role", response_model=AdminSetRoleResponse)
def patch_admin_role(
    admin_id: int,
    payload: AdminSetRoleRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """Updates an admin's system role (admin ↔ superadmin). Superadmin only."""
    return update_admin_role(
        db,
        target_admin_id=admin_id,
        new_role=payload.system_role,
        requesting_admin_id=current_admin.id,
    )


# ── DELETE /admin/accounts/{admin_id} ─────────────────────────────────────────

@router.delete("/{admin_id}", response_model=AdminDeleteResponse)
def remove_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """Permanently deletes an admin account. Superadmin only."""
    return delete_admin_account(
        db,
        target_admin_id=admin_id,
        requesting_admin_id=current_admin.id,
    )