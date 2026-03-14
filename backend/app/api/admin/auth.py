"""
app/api/admin/auth.py

Router for admin authentication and profile management.
Handles login, registration, profile updates, password changes,
resident re-linking, and photo upload/retrieval/deletion.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin, require_superadmin
from app.schemas.admin.auth import (
    AdminLoginRequest,
    AdminCreateRequest,
    AdminTokenResponse,
    AdminProfileResponse,
    AdminUpdateProfileRequest,
    AdminUpdateProfileResponse,
    AdminChangePasswordRequest,
    AdminChangePasswordResponse,
    AdminRelinkResidentRequest,
)
from app.services.auth_service import (
    authenticate_admin,
    create_admin_account,
    get_admin_profile,
    update_admin_profile,
    change_admin_password,
    update_admin_photo,
    get_admin_photo,
    relink_admin_resident,
)
from app.core.security import create_access_token
from app.models.admin import Admin

router = APIRouter(prefix="/auth")

# Maximum allowed photo upload size (5 MB)
MAX_PHOTO_BYTES = 5 * 1024 * 1024

# Accepted MIME types for admin profile photos
ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/png", "image/webp"}

@router.post("/login", response_model=AdminTokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = authenticate_admin(db, username=payload.username, password=payload.password)

    # Embed the admin's ID and system role into the token payload
    token = create_access_token(
        data={
            "sub": str(admin.id),
            "role": admin.system_role,
        }
    )

    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", response_model=AdminProfileResponse, status_code=201)
def register_admin(payload: AdminCreateRequest, db: Session = Depends(get_db)):
    """
    Register a new admin account linked to an existing resident record.
    Returns the created admin's profile. Photo is not set on creation.
    """
    admin = create_admin_account(
        db=db,
        resident_id=payload.resident_id,
        username=payload.username,
        password=payload.password,
        position=payload.position,
        system_role=payload.system_role,
    )

    # New accounts have no photo by default
    admin.has_photo = False
    return admin


@router.get("/me", response_model=AdminProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Retrieve the authenticated admin's full profile.
    """
    return get_admin_profile(db, admin_id=current_admin.id)


@router.patch("/me", response_model=AdminUpdateProfileResponse)
def update_my_profile(
    payload: AdminUpdateProfileRequest,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Update the authenticated admin's username and/or position.
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
    Change the authenticated admin's password.
    Requires the current password for verification before updating.
    """
    change_admin_password(
        db,
        admin_id=current_admin.id,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return {"detail": "Password updated successfully"}


@router.patch("/me/resident", response_model=AdminProfileResponse)
def relink_my_resident(
    payload: AdminRelinkResidentRequest,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(require_superadmin),
):
    """
    Re-link the authenticated superadmin's account to a different resident record.
    Restricted to superadmins only.
    """
    admin = relink_admin_resident(
        db,
        admin_id=current_admin.id,
        new_resident_id=payload.resident_id,
    )
    admin.has_photo = admin.photo is not None
    return admin


@router.put("/me/photo", status_code=204)
async def upload_my_photo(
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    if photo.content_type not in ALLOWED_PHOTO_TYPES:
        raise HTTPException(status_code=415, detail="Photo must be JPEG, PNG, or WebP")

    photo_bytes = await photo.read()

    if len(photo_bytes) > MAX_PHOTO_BYTES:
        raise HTTPException(status_code=413, detail="Photo must be under 5 MB")

    update_admin_photo(db, admin_id=current_admin.id, photo_bytes=photo_bytes)


@router.get("/me/photo")
def get_my_photo(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Retrieve the authenticated admin's profile photo as a raw JPEG response.
    """
    photo_bytes = get_admin_photo(db, admin_id=current_admin.id)
    return Response(content=photo_bytes, media_type="image/jpeg")


@router.delete("/me/photo", status_code=204)
def delete_my_photo(
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """
    Delete the authenticated admin's profile photo.
    Sets the photo field to null and commits the change.
    """
    admin = db.query(Admin).filter(Admin.id == current_admin.id).first()
    if admin:
        admin.photo = None
        db.commit()