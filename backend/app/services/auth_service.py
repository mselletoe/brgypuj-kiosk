"""
app/services/auth_service.py

Service layer for admin authentication and profile management.
Handles password hashing, RFID-based resident login, admin credential
verification, account creation, profile updates, and photo storage.
"""

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from passlib.context import CryptContext
from datetime import date
from app.models.resident import Resident, ResidentRFID
from app.models.barangayid import BarangayID
from app.models.admin import Admin

# bcrypt context for hashing and verifying passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Default PIN assigned to residents before they set their own
RFID_PIN_DEFAULT = '0000'


# =================================================================================
# UTILITIES
# =================================================================================
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _get_admin_or_404(db: Session, admin_id: int) -> Admin:
    """
    Fetches an admin by ID with their linked resident eagerly loaded.
    Raises 404 if no matching admin is found.
    """
    admin = (
        db.query(Admin)
        .options(joinedload(Admin.resident))
        .filter(Admin.id == admin_id)
        .first()
    )
    if not admin:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")
    return admin


# =================================================================================
# KIOSK AUTH
# =================================================================================
def rfid_login(db: Session, rfid_uid: str):
    """
    Looks up a resident by their active RFID tag UID.

    If the RFID card is expired, deactivates it along with any linked
    Barangay ID and returns None. Also attaches a convenience `has_pin`
    flag to indicate whether the resident has set a custom PIN.
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

    # Deactivate expired RFID cards and their linked Barangay IDs
    if rfid.expiration_date and rfid.expiration_date < date.today():
        rfid.is_active = False

        linked_brgy_id = (
            db.query(BarangayID)
            .filter(
                BarangayID.rfid_id == rfid.id,
                BarangayID.is_active.is_(True),
            )
            .first()
        )
        if linked_brgy_id:
            linked_brgy_id.is_active = False

        db.commit()
        return None

    # True if the resident has set a PIN beyond the default
    resident.has_pin = resident.rfid_pin not in (None, RFID_PIN_DEFAULT)
    return resident


# =================================================================================
# ADMIN AUTH
# =================================================================================
def authenticate_admin(db: Session, username: str, password: str) -> Admin:
    """
    Validates admin credentials and returns the authenticated Admin.

    Raises 401 for an unrecognized username or wrong password, and
    403 if the account exists but has been deactivated.
    """
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
    """
    Creates and persists a new admin account linked to a resident record.
    Raises 400 if the username is already taken.
    """
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


# =================================================================================
# ADMIN PROFILE
# =================================================================================
def get_admin_profile(db: Session, admin_id: int) -> Admin:
    """
    Returns the admin's full profile including the linked resident's name.
    The `has_photo` flag is computed here so the response schema stays clean.
    """
    admin = _get_admin_or_404(db, admin_id)
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


def relink_admin_resident(db: Session, admin_id: int, new_resident_id: int) -> Admin:
    """
    Superadmin-only: re-links the admin account to a different resident record.

    Guards:
    - The target resident must exist.
    - The target resident must not already be linked to another admin account.
    """
    admin = _get_admin_or_404(db, admin_id)

    resident = db.query(Resident).filter(Resident.id == new_resident_id).first()
    if not resident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resident not found"
        )

    conflict = (
        db.query(Admin)
        .filter(Admin.resident_id == new_resident_id, Admin.id != admin_id)
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This resident is already linked to another admin account"
        )

    admin.resident_id = new_resident_id
    db.commit()
    return _get_admin_or_404(db, admin_id)


# =================================================================================
# ADMIN PHOTO
# =================================================================================
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