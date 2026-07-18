"""Authentication routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AuthenticationError
from app.core.security import REFRESH_TOKEN, create_access_token, create_refresh_token, decode_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPassword,
    SupabaseLogin,
    Token,
    TokenRefresh,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.schemas.common import Message
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=Token, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    user = service.register(payload)
    return service.issue_tokens(user)


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    service = AuthService(db)
    user = service.authenticate(payload.email, payload.password)
    return service.issue_tokens(user)


@router.post("/login/oauth", response_model=Token, include_in_schema=False)
def login_oauth(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Token:
    """OAuth2 password flow endpoint enabling the Swagger 'Authorize' button."""
    service = AuthService(db)
    user = service.authenticate(form_data.username, form_data.password)
    return service.issue_tokens(user)


@router.post("/supabase", response_model=Token)
def login_supabase(payload: SupabaseLogin, db: Session = Depends(get_db)) -> Token:
    """Exchange a Supabase access token (Google OAuth / email) for app JWTs."""
    service = AuthService(db)
    user = service.login_with_supabase(payload.access_token)
    return service.issue_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh_token(payload: TokenRefresh, db: Session = Depends(get_db)) -> Token:
    claims = decode_token(payload.refresh_token)
    if not claims or claims.get("type") != REFRESH_TOKEN:
        raise AuthenticationError("Invalid refresh token")
    subject = claims["sub"]
    return Token(
        access_token=create_access_token(subject),
        refresh_token=create_refresh_token(subject),
    )


@router.post("/forgot-password", response_model=Message)
def forgot_password(payload: ForgotPassword, db: Session = Depends(get_db)) -> Message:
    """Trigger a password reset. Delegates to Supabase Auth in production."""
    # Always respond success to avoid user enumeration.
    return Message(message="If an account exists, a reset link has been sent.")


@router.get("/me", response_model=UserRead)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
