"""
Authentication Service Layer
---------------------------
Contains the core business logic for resident authentication.
Separates database query complexity from the API routing layer.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.models.resident import Resident, ResidentRFID
from app.models.admin import Admin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def rfid_login(db: Session, rfid_uid: str):
    """
    Validates an RFID UID and retrieves the associated Resident profile.
    
    This function performs a relational join between the Residents and ResidentRFIDs 
    tables to ensure the card is both recognized and currently active.
    
    Args:
        db (Session): The active SQLAlchemy database session.
        rfid_uid (str): The unique hex or decimal string from the RFID hardware.
        
    Returns:
        Optional[Resident]: The Resident model instance with an injected 'has_pin' 
                           attribute if found and active; otherwise None.
                           
    Note:
        The 'has_pin' attribute is dynamically attached to the Resident object 
        to assist the frontend in determining the security challenge flow.
    """

    # Execute a joined query to fetch both Resident details and RFID status in one trip
    result = (
        db.query(Resident, ResidentRFID)
        .join(ResidentRFID, Resident.id == ResidentRFID.resident_id)
        .filter(
            ResidentRFID.rfid_uid == rfid_uid,
            ResidentRFID.is_active == True
        )
        .first()
    )

    # Return None if no active record matches the scanned UID
    if not result:
        return None

    # Unpack the tuple returned by the joined query
    resident, rfid = result

    # Business Logic: Determine if the resident has already configured a security PIN.
    # Checks the 'rfid_pin' column in the Resident table.
    # This boolean flag is used by the Pydantic schema for serialization.
    resident.has_pin = resident.rfid_pin is not None
    
    return resident

# ================================================================
# ADMIN
# ================================================================ 

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def authenticate_admin(db: Session, username: str, password: str) -> Admin:
    admin = db.query(Admin).filter(Admin.username == username).first()

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
    role: str
) -> Admin:
    existing = db.query(Admin).filter(Admin.username == username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    admin = Admin(
        resident_id=resident_id,
        username=username,
        password=hash_password(password),
        role=role
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin