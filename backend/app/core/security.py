"""Password hashing and JWT token utilities."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN = "access"
REFRESH_TOKEN = "refresh"


def hash_password(password: str) -> str:
    """Hash a plain-text password."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a stored hash."""
    return pwd_context.verify(plain_password, hashed_password)


def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a short-lived access token."""
    return _create_token(
        subject,
        ACCESS_TOKEN,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims,
    )


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        subject,
        REFRESH_TOKEN,
        timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> dict[str, Any] | None:
    """Decode and validate a JWT issued by this application. Returns ``None`` if invalid."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None


def decode_supabase_token(token: str) -> dict[str, Any] | None:
    """Decode a Supabase-issued JWT using the Supabase JWT secret."""
    if not settings.SUPABASE_JWT_SECRET:
        return None
    try:
        return jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError:
        return None
