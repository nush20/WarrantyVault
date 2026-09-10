from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.config import get_settings
from backend.models.user import User
from backend.schemas.auth import UserCreate
from backend.utils.exceptions import ConflictError, UnauthorizedError

password_hash = PasswordHash.recommended()


def create_user(db: Session, data: UserCreate) -> User:
    email = data.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise ConflictError("An account with this email already exists")
    user = User(email=email, hashed_password=password_hash.hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.scalar(select(User).where(User.email == email.lower()))
    if not user or not password_hash.verify(password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")
    return user


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": user_id, "exp": expires}, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_access_token(token: str) -> str:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid authentication token")
        return user_id
    except jwt.PyJWTError as exc:
        raise UnauthorizedError("Invalid or expired authentication token") from exc
