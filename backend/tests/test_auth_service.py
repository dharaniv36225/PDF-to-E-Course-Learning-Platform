"""Integration tests for AuthService (requires the configured database)."""
import uuid

import pytest

from app.core.errors import AuthenticationError, ConflictError
from app.core.security import decode_token
from app.schemas.auth import UserCreate
from app.services.auth_service import AuthService


def _payload() -> UserCreate:
    return UserCreate(
        email=f"auth-{uuid.uuid4()}@test.dev",
        full_name="Auth Tester",
        password="s3cret-password",
    )


def test_register_creates_hashed_user(db):
    service = AuthService(db)
    payload = _payload()
    created = service.register(payload)
    try:
        assert created.id is not None
        assert created.email == payload.email.lower()
        assert created.hashed_password and created.hashed_password != payload.password
        assert created.auth_provider == "email"
    finally:
        db.delete(created)
        db.commit()


def test_register_duplicate_email_raises(db):
    service = AuthService(db)
    payload = _payload()
    created = service.register(payload)
    try:
        with pytest.raises(ConflictError):
            service.register(payload)
    finally:
        db.delete(created)
        db.commit()


def test_authenticate_success(db):
    service = AuthService(db)
    payload = _payload()
    created = service.register(payload)
    try:
        user = service.authenticate(payload.email, payload.password)
        assert user.id == created.id
    finally:
        db.delete(created)
        db.commit()


def test_authenticate_wrong_password_raises(db):
    service = AuthService(db)
    payload = _payload()
    created = service.register(payload)
    try:
        with pytest.raises(AuthenticationError):
            service.authenticate(payload.email, "wrong-password")
    finally:
        db.delete(created)
        db.commit()


def test_authenticate_unknown_email_raises(db):
    service = AuthService(db)
    with pytest.raises(AuthenticationError):
        service.authenticate("nobody@test.dev", "whatever12")


def test_authenticate_inactive_user_raises(db):
    service = AuthService(db)
    payload = _payload()
    created = service.register(payload)
    created.is_active = False
    db.commit()
    try:
        with pytest.raises(AuthenticationError):
            service.authenticate(payload.email, payload.password)
    finally:
        db.delete(created)
        db.commit()


def test_issue_tokens_embeds_subject_and_email(db):
    service = AuthService(db)
    payload = _payload()
    created = service.register(payload)
    try:
        token = service.issue_tokens(created)
        access = decode_token(token.access_token)
        assert access is not None
        assert access["sub"] == str(created.id)
        assert access["email"] == created.email
        assert decode_token(token.refresh_token) is not None
    finally:
        db.delete(created)
        db.commit()
