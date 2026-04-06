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
from app.api.deps import get_db 

router = APIRouter(prefix="/accounts")


@router.get("", response_model=list[AdminAccountListItem])
def get_all_admins(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    return list_all_admins(db)


@router.get("/{admin_id}/photo")
def get_admin_photo(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    from fastapi import HTTPException, status as http_status
    admin = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Admin not found")
    if not admin.photo:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="No photo uploaded")
    return Response(content=admin.photo, media_type="image/jpeg")



@router.patch("/{admin_id}/status", response_model=AdminSetStatusResponse)
def patch_admin_status(
    admin_id: int,
    payload: AdminSetStatusRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    return set_admin_active_status(
        db,
        target_admin_id=admin_id,
        is_active=payload.is_active,
        requesting_admin_id=current_admin.id,
    )


@router.patch("/{admin_id}/role", response_model=AdminSetRoleResponse)
def patch_admin_role(
    admin_id: int,
    payload: AdminSetRoleRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    return update_admin_role(
        db,
        target_admin_id=admin_id,
        new_role=payload.system_role,
        requesting_admin_id=current_admin.id,
    )


@router.delete("/{admin_id}", response_model=AdminDeleteResponse)
def remove_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    return delete_admin_account(
        db,
        target_admin_id=admin_id,
        requesting_admin_id=current_admin.id,
    )