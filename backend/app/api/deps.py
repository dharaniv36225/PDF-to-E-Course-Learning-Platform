"""Shared FastAPI dependencies."""
from __future__ import annotations

import uuid

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AuthenticationError
from app.core.security import ACCESS_TOKEN, decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login", auto_error=False
)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Resolve the authenticated user from a bearer JWT."""
    if not token:
        raise AuthenticationError("Not authenticated")
    payload = decode_token(token)
    if not payload or payload.get("type") != ACCESS_TOKEN:
        raise AuthenticationError("Invalid or expired token")
    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Invalid token subject")
    try:
        user_id = uuid.UUID(subject)
    except ValueError as exc:
        raise AuthenticationError("Invalid token subject") from exc

    user = UserRepository(db).get(user_id)
    if not user or not user.is_active:
        raise AuthenticationError("User not found or inactive")
    return user
