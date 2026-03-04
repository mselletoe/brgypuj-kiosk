"""
Authentication & Account Settings Service Layer
------------------------------------------------
Core business logic for admin authentication and self-service account management.
All database mutations go through here; the router layer stays thin.
"""
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from passlib.context import CryptContext

from app.models.resident import Resident, ResidentRFID
from app.models.admin import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sentinel value for residents who have not yet configured a PIN.
RFID_PIN_DEFAULT = '0000'


# ================================================================
# HELPERS
# ================================================================

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _get_admin_or_404(db: Session, admin_id: int) -> Admin:
    """Shared lookup used by every settings endpoint."""
    admin = (
        db.query(Admin)
        .options(joinedload(Admin.resident))   # eager-load so resident name is always available
        .filter(Admin.id == admin_id)
        .first()
    )
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin


# ================================================================
# RESIDENT / RFID AUTH
# ================================================================

def rfid_login(db: Session, rfid_uid: str):
    """
    Validates an RFID UID and retrieves the associated Resident profile.
    Dynamically attaches `has_pin` to the Resident object for the frontend
    to decide whether to show the PIN setup or verify screen.
    """
    result = (
        db.query(Resident, ResidentRFID)
        .join(ResidentRFID, Resident.id == ResidentRFID.resident_id)
        .filter(
            ResidentRFID.rfid_uid == rfid_uid,
            ResidentRFID.is_active == True
        )
        .first()
    )

    if not result:
        return None

    resident, rfid = result
    resident.has_pin = resident.rfid_pin not in (None, RFID_PIN_DEFAULT)
    return resident


# ================================================================
# ADMIN AUTHENTICATION
# ================================================================

def authenticate_admin(db: Session, username: str, password: str) -> Admin:
    admin = (
        db.query(Admin)
        .options(joinedload(Admin.resident))
        .filter(Admin.username == username)
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    if not verify_password(password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    return admin


def create_admin_account(
    db: Session,
    resident_id: int,
    username: str,
    password: str,
    position: str | None,
    system_role: str,
) -> Admin:
    if db.query(Admin).filter(Admin.username == username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    admin = Admin(
        resident_id=resident_id,
        username=username,
        password=hash_password(password),
        position=position,
        system_role=system_role,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


# ================================================================
# ADMIN ACCOUNT SETTINGS
# ================================================================

def get_admin_profile(db: Session, admin_id: int) -> Admin:
    """
    Returns the admin's full profile including the linked resident's name.
    The `has_photo` flag is computed here so the response schema stays clean.
    """
    admin = _get_admin_or_404(db, admin_id)
    # Attach a convenience flag — avoids sending the raw binary to the profile endpoint
    admin.has_photo = admin.photo is not None
    return admin


def update_admin_profile(
    db: Session,
    admin_id: int,
    username: str | None,
    position: str | None,
) -> Admin:
    """
    Updates editable text fields on the admin's own account.
    Only the fields that are explicitly provided (not None) are written.
    """
    admin = _get_admin_or_404(db, admin_id)

    if username is not None:
        # Guard against another admin already owning that username
        conflict = (
            db.query(Admin)
            .filter(Admin.username == username, Admin.id != admin_id)
            .first()
        )
        if conflict:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username is already taken by another account"
            )
        admin.username = username

    if position is not None:
        admin.position = position

    db.commit()
    db.refresh(admin)
    return admin


def change_admin_password(
    db: Session,
    admin_id: int,
    current_password: str,
    new_password: str,
) -> None:
    """
    Verifies the current password before accepting the new one.
    Raises 401 if the current password is wrong so the frontend can show
    a specific 'incorrect current password' message.
    """
    admin = _get_admin_or_404(db, admin_id)

    if not verify_password(current_password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )

    admin.password = hash_password(new_password)
    db.commit()


def update_admin_photo(db: Session, admin_id: int, photo_bytes: bytes) -> None:
    """Stores the raw photo bytes directly on the admin row."""
    admin = _get_admin_or_404(db, admin_id)
    admin.photo = photo_bytes
    db.commit()


def get_admin_photo(db: Session, admin_id: int) -> bytes:
    """
    Returns the raw photo bytes for streaming back as an image response.
    Raises 404 if no photo has been uploaded yet.
    """
    admin = _get_admin_or_404(db, admin_id)
    if not admin.photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No photo uploaded for this account"
        )
    return admin.photo