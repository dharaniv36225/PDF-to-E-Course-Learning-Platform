"""Authentication service: registration, login, tokens, Supabase bridging."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.errors import AuthenticationError, ConflictError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_supabase_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import Token, UserCreate


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def register(self, payload: UserCreate) -> User:
        if self.users.get_by_email(payload.email):
            raise ConflictError("An account with this email already exists")
        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            auth_provider="email",
            is_verified=False,
        )
        self.users.add(user)
        self.users.commit()
        return user

    def authenticate(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if not user or not user.hashed_password:
            raise AuthenticationError("Invalid email or password")
        if not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")
        if not user.is_active:
            raise AuthenticationError("Account is disabled")
        return user

    def login_with_supabase(self, access_token: str) -> User:
        claims = decode_supabase_token(access_token)
        if not claims:
            raise AuthenticationError("Invalid Supabase token")
        supabase_id = claims.get("sub")
        email = claims.get("email")
        if not supabase_id or not email:
            raise AuthenticationError("Supabase token missing required claims")

        user = self.users.get_by_supabase_id(supabase_id) or self.users.get_by_email(email)
        metadata = claims.get("user_metadata") or {}
        if user is None:
            user = User(
                email=email.lower(),
                full_name=metadata.get("full_name") or metadata.get("name"),
                avatar_url=metadata.get("avatar_url") or metadata.get("picture"),
                supabase_user_id=supabase_id,
                auth_provider=claims.get("app_metadata", {}).get("provider", "supabase"),
                is_verified=True,
            )
            self.users.add(user)
        else:
            user.supabase_user_id = supabase_id
            user.is_verified = True
        self.users.commit()
        return user

    @staticmethod
    def issue_tokens(user: User) -> Token:
        subject = str(user.id)
        return Token(
            access_token=create_access_token(subject, {"email": user.email}),
            refresh_token=create_refresh_token(subject),
        )
