"""
Admin Authentication & Account Settings Router
-----------------------------------------------
All routes are prefixed with /admin/auth via the main app router include.

Route map:
  POST   /login                  — get JWT
  POST   /register               — create admin account (superadmin only in prod)
  GET    /me                     — get own profile
  PATCH  /me                     — update username / position
  PATCH  /me/password            — change password
  PUT    /me/photo               — upload / replace profile photo
  GET    /me/photo               — serve profile photo as image
"""
from fastapi import APIRouter, Depends, UploadFile, File
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin
from app.schemas.admin.auth import (
    AdminLoginRequest,
    AdminCreateRequest,
    AdminTokenResponse,
    AdminProfileResponse,
    AdminUpdateProfileRequest,
    AdminUpdateProfileResponse,
    AdminChangePasswordRequest,
    AdminChangePasswordResponse,
)
from app.services.auth_service import (
    authenticate_admin,
    create_admin_account,
    get_admin_profile,
    update_admin_profile,
    change_admin_password,
    update_admin_photo,
    get_admin_photo,
)
from app.core.security import create_access_token
from app.models.admin import Admin

router = APIRouter(prefix="/auth")

# Max photo size: 5 MB
MAX_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}


# ================================================================
# AUTHENTICATION
# ================================================================

@router.post("/login", response_model=AdminTokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, username=payload.username, password=payload.password)

    token = create_access_token(
        data={
            "sub": str(admin.id),
            "role": admin.system_role,        # updated field name
        }
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=AdminProfileResponse, status_code=201)
def register_admin(payload: AdminCreateRequest, db: Session = Depends(get_db)):
    """
    Creates a new admin account.
    
    In production: protect this with `get_current_admin` and add a
    superadmin role guard so only superadmins can register new accounts.
    For initial seeding, the seed_admin.py script is used instead.
    """
    admin = create_admin_account(
        db=db,
        resident_id=payload.resident_id,
        username=payload.username,
        password=payload.password,
        position=payload.position,
        system_role=payload.system_role,
    )
    admin.has_photo = False
    return admin


# ================================================================
# ACCOUNT SETTINGS — the admin manages their own account
# ================================================================

@router.get("/me", response_model=AdminProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Returns the authenticated admin's full profile including linked resident name."""
    return get_admin_profile(db, admin_id=current_admin.id)


@router.patch("/me", response_model=AdminUpdateProfileResponse)
def update_my_profile(
    payload: AdminUpdateProfileRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Partially updates username and/or position.
    Send only the fields you want to change.
    """
    return update_admin_profile(
        db,
        admin_id=current_admin.id,
        username=payload.username,
        position=payload.position,
    )


@router.patch("/me/password", response_model=AdminChangePasswordResponse)
def change_my_password(
    payload: AdminChangePasswordRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Changes the admin's password after verifying the current one.
    Returns 401 if current_password is wrong.
    """
    change_admin_password(
        db,
        admin_id=current_admin.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return {"detail": "Password updated successfully"}


@router.put("/me/photo", status_code=204)
async def upload_my_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Uploads or replaces the admin's profile photo.
    Accepts JPEG, PNG, or WebP up to 5 MB.
    Returns 204 No Content on success.
    """
    if photo.content_type not in ALLOWED_PHOTO_TYPES:
        from fastapi import HTTPException
        raise HTTPException(status_code=415, detail="Photo must be JPEG, PNG, or WebP")

    photo_bytes = await photo.read()

    if len(photo_bytes) > MAX_PHOTO_BYTES:
        from fastapi import HTTPException
        raise HTTPException(status_code=413, detail="Photo must be under 5 MB")

    update_admin_photo(db, admin_id=current_admin.id, photo_bytes=photo_bytes)


@router.get("/me/photo")
def get_my_photo(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Streams the admin's profile photo as a raw image response.
    The frontend can use this URL directly in an <img> src tag with the
    Authorization header set (or embed as a blob URL after fetching).
    Returns 404 if no photo has been uploaded yet.
    """
    photo_bytes = get_admin_photo(db, admin_id=current_admin.id)
    return Response(content=photo_bytes, media_type="image/jpeg")


@router.delete("/me/photo", status_code=204)
def delete_my_photo(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    admin = db.query(Admin).filter(Admin.id == current_admin.id).first()
    if admin:
        admin.photo = None
        db.commit()