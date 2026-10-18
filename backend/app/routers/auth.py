from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models
from ..database import get_db
from ..security import create_access_token, get_current_staff, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    staff = db.scalar(select(models.Staff).where(models.Staff.username == form.username))
    if (
        staff is None
        or not staff.login_enabled
        or not staff.password_hash
        or not verify_password(form.password, staff.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(staff),
        "token_type": "bearer",
        "role": staff.role,
        "staff_id": staff.id,
    }


@router.get("/me")
def me(staff: models.Staff = Depends(get_current_staff)):
    return {
        "id": staff.id,
        "first_name": staff.first_name,
        "last_name": staff.last_name,
        "role": staff.role,
        "department_id": staff.department_id,
        "username": staff.username,
    }
