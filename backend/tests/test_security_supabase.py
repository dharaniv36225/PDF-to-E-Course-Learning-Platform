from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.core.security import (
    REFRESH_TOKEN,
    create_refresh_token,
    decode_supabase_token,
    decode_token,
)


def test_refresh_token_has_refresh_type():
    payload = decode_token(create_refresh_token("user-9"))
    assert payload is not None
    assert payload["type"] == REFRESH_TOKEN
    assert payload["sub"] == "user-9"


def test_decode_supabase_token_returns_none_without_secret(monkeypatch):
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", "", raising=False)
    assert decode_supabase_token("anything") is None


def test_decode_supabase_token_valid(monkeypatch):
    secret = "supabase-secret"
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret, raising=False)
    token = jwt.encode(
        {
            "sub": "sb-user",
            "email": "a@b.com",
            "aud": "authenticated",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )
    claims = decode_supabase_token(token)
    assert claims is not None
    assert claims["sub"] == "sb-user"


def test_decode_supabase_token_wrong_audience_returns_none(monkeypatch):
    secret = "supabase-secret"
    monkeypatch.setattr(settings, "SUPABASE_JWT_SECRET", secret, raising=False)
    token = jwt.encode(
        {"sub": "sb-user", "aud": "someone-else"},
        secret,
        algorithm="HS256",
    )
    assert decode_supabase_token(token) is None
