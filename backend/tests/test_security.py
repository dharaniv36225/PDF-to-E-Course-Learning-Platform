from app.core.security import (
    ACCESS_TOKEN,
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("s3cret-password")
    assert hashed != "s3cret-password"
    assert verify_password("s3cret-password", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_roundtrip():
    token = create_access_token("user-123", {"email": "a@b.com"})
    payload = decode_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["type"] == ACCESS_TOKEN
    assert payload["email"] == "a@b.com"


def test_invalid_token_returns_none():
    assert decode_token("not-a-token") is None
