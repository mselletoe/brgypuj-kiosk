"""
Admin Accounts Management Service
----------------------------------
Superadmin-only operations for managing all admin accounts:
  - List all admins with profile info
  - Toggle active/inactive status
  - Update system role
  - Create new admin account (wraps auth_service)
  - Delete admin account
"""

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from app.models.admin import Admin
from app.models.resident import Resident


# ================================================================
# HELPERS
# ================================================================

def _build_full_name(resident) -> str:
    parts = [resident.first_name]
    if resident.middle_name:
        parts.append(resident.middle_name)
    parts.append(resident.last_name)
    if resident.suffix:
        parts.append(resident.suffix)
    return " ".join(parts)


# ================================================================
# LIST
# ================================================================

def list_all_admins(db: Session) -> list[dict]:
    """
    Returns all admin accounts with their linked resident's full name,
    photo flag, role, status, and last-login info.
    Ordered by created_at descending (newest first).
    """
    admins = (
        db.query(Admin)
        .options(joinedload(Admin.resident))
        .order_by(Admin.created_at.asc())
        .all()
    )

    result = []
    for admin in admins:
        resident = admin.resident
        result.append({
            "id": admin.id,
            "username": admin.username,
            "full_name": _build_full_name(resident) if resident else "—",
            "position": admin.position,
            "system_role": admin.system_role,
            "is_active": admin.is_active,
            "has_photo": admin.photo is not None,
            "created_at": admin.created_at.isoformat() if admin.created_at else None,
        })

    return result


# ================================================================
# TOGGLE STATUS
# ================================================================

def set_admin_active_status(
    db: Session,
    target_admin_id: int,
    is_active: bool,
    requesting_admin_id: int,
) -> dict:
    """
    Activates or deactivates an admin account.
    Guards:
      - Cannot deactivate your own account.
      - Cannot deactivate the last active superadmin.
    """
    admin = (
        db.query(Admin)
        .options(joinedload(Admin.resident))
        .filter(Admin.id == target_admin_id)
        .first()
    )
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    if target_admin_id == requesting_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    # Guard: don't deactivate the last active superadmin
    if not is_active and admin.system_role == "superadmin":
        active_superadmins = (
            db.query(Admin)
            .filter(Admin.system_role == "superadmin", Admin.is_active == True)
            .count()
        )
        if active_superadmins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate the last active superadmin account",
            )

    admin.is_active = is_active
    db.commit()
    db.refresh(admin)

    return {
        "id": admin.id,
        "is_active": admin.is_active,
        "detail": f"Account {'activated' if is_active else 'deactivated'} successfully",
    }


# ================================================================
# UPDATE ROLE
# ================================================================

VALID_ROLES = {"admin", "superadmin"}


def update_admin_role(
    db: Session,
    target_admin_id: int,
    new_role: str,
    requesting_admin_id: int,
) -> dict:
    """
    Changes an admin's system_role.
    Guards:
      - Role must be 'admin' or 'superadmin'.
      - Cannot demote the last active superadmin.
      - Cannot change your own role (prevents accidental self-demotion).
    """
    if new_role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    admin = (
        db.query(Admin)
        .filter(Admin.id == target_admin_id)
        .first()
    )
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    if target_admin_id == requesting_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot change your own role",
        )

    # Guard: don't demote last active superadmin
    if admin.system_role == "superadmin" and new_role != "superadmin":
        active_superadmins = (
            db.query(Admin)
            .filter(Admin.system_role == "superadmin", Admin.is_active == True)
            .count()
        )
        if active_superadmins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot demote the last active superadmin account",
            )

    admin.system_role = new_role
    db.commit()
    db.refresh(admin)

    return {
        "id": admin.id,
        "system_role": admin.system_role,
        "detail": f"Role updated to '{new_role}' successfully",
    }


# ================================================================
# DELETE
# ================================================================

def delete_admin_account(
    db: Session,
    target_admin_id: int,
    requesting_admin_id: int,
) -> dict:
    """
    Permanently deletes an admin account.
    Guards:
      - Cannot delete your own account.
      - Cannot delete the last active superadmin.
    """
    admin = db.query(Admin).filter(Admin.id == target_admin_id).first()
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

    if target_admin_id == requesting_admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    if admin.system_role == "superadmin":
        active_superadmins = (
            db.query(Admin)
            .filter(Admin.system_role == "superadmin", Admin.is_active == True)
            .count()
        )
        if active_superadmins <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last active superadmin account",
            )

    db.delete(admin)
    db.commit()

    return {"detail": "Admin account deleted successfully"}