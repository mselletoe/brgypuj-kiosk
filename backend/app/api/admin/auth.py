from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.admin.auth import (
    AdminLoginRequest,
    AdminCreateRequest,
    AdminTokenResponse,
    AdminProfileResponse
)
from app.services.auth_service import (
    authenticate_admin,
    create_admin_account
)
from app.core.security import create_access_token

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=AdminTokenResponse)
def admin_login(payload: AdminLoginRequest, db: Session = Depends(get_db)):
    admin = authenticate_admin(
        db,
        username=payload.username,
        password=payload.password
    )

    token = create_access_token(
        data={
            "sub": str(admin.id),
            "role": admin.role
        }
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.post("/register", response_model=AdminProfileResponse)
def register_admin(payload: AdminCreateRequest, db: Session = Depends(get_db)):
    admin = create_admin_account(
        db=db,
        resident_id=payload.resident_id,
        username=payload.username,
        password=payload.password,
        role=payload.role
    )

    return admin
