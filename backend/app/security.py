import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from . import models
from .database import get_db

PBKDF2_ITERATIONS = 200_000
SECRET_KEY = os.getenv("HOSPITAL_SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = 8

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(PBKDF2_ITERATIONS, salt.hex(), digest.hex())


def verify_password(password: str, hashed: str) -> bool:
    # bcrypt is accepted too, so the hashes in data/staff.csv work.
    if hashed.startswith(("$2a$", "$2b$", "$2y$")):
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except ValueError:
            return False
    try:
        scheme, iterations, salt_hex, hash_hex = hashed.split("$")
        if scheme != "pbkdf2_sha256":
            return False
        expected = bytes.fromhex(hash_hex)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations), len(expected)
        )
    except (ValueError, TypeError, AttributeError):
        return False
    return hmac.compare_digest(digest, expected)


def create_access_token(staff: models.Staff) -> str:
    payload = {
        "sub": str(staff.id),
        "role": staff.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_staff(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.Staff:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        staff_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError, TypeError):
        raise unauthorized

    staff = db.get(models.Staff, staff_id)
    if staff is None or not staff.login_enabled:
        raise unauthorized
    return staff


def require_roles(*roles: str):
    def checker(staff: models.Staff = Depends(get_current_staff)) -> models.Staff:
        if staff.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{staff.role}' cannot do this",
            )
        return staff

    return checker


def get_current_doctor(
    staff: models.Staff = Depends(get_current_staff), db: Session = Depends(get_db)
) -> models.Doctor:
    doctor = db.query(models.Doctor).filter(models.Doctor.staff_id == staff.id).first()
    if doctor is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This staff member has no doctor profile",
        )
    return doctor
