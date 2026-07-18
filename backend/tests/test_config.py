"""Tests for settings normalization."""
import os
from unittest import mock

import pytest

from app.core.config import INSECURE_SECRET_KEY, Settings


def test_database_url_normalizes_legacy_scheme() -> None:
    settings = Settings(DATABASE_URL="postgres://user:pass@host:5432/db")
    assert settings.DATABASE_URL == "postgresql+psycopg://user:pass@host:5432/db"


def test_database_url_normalizes_plain_postgresql_scheme() -> None:
    settings = Settings(DATABASE_URL="postgresql://user:pass@host:5432/db")
    assert settings.DATABASE_URL == "postgresql+psycopg://user:pass@host:5432/db"


def test_database_url_keeps_explicit_driver() -> None:
    url = "postgresql+psycopg://user:pass@host:5432/db"
    assert Settings(DATABASE_URL=url).DATABASE_URL == url


def test_cors_origins_accepts_comma_separated_string() -> None:
    settings = Settings(BACKEND_CORS_ORIGINS="http://a.com, http://b.com")
    assert settings.BACKEND_CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_from_env_comma_separated() -> None:
    """Env vars are the real-world path (docker-compose/Render) and must not crash."""
    with mock.patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": "http://a.com,http://b.com"}):
        assert Settings().BACKEND_CORS_ORIGINS == ["http://a.com", "http://b.com"]


def test_cors_origins_from_env_json_array() -> None:
    with mock.patch.dict(os.environ, {"BACKEND_CORS_ORIGINS": '["http://a.com"]'}):
        assert Settings().BACKEND_CORS_ORIGINS == ["http://a.com"]


def test_production_rejects_default_secret_key() -> None:
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(ENVIRONMENT="production", SECRET_KEY=INSECURE_SECRET_KEY)


def test_production_accepts_custom_secret_key() -> None:
    settings = Settings(ENVIRONMENT="production", SECRET_KEY="a-strong-unique-secret")
    assert settings.is_production is True


def test_development_allows_default_secret_key() -> None:
    settings = Settings(ENVIRONMENT="development", SECRET_KEY=INSECURE_SECRET_KEY)
    assert settings.SECRET_KEY == INSECURE_SECRET_KEY
