"""Tests for settings normalization."""
from app.core.config import Settings


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
