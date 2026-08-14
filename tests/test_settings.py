"""Production settings and Railway database URL handling."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_production_rejects_weak_app_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("APP_SECRET", "bitte-aendern")
    get_settings.cache_clear()
    settings = Settings()
    with pytest.raises(ValueError, match="APP_SECRET"):
        settings.require_production_secret()


def test_local_env_allows_default_secret() -> None:
    Settings().require_production_secret()


def test_postgres_scheme_is_normalized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgres://user:pass@shuttle.proxy.rlwy.net:5432/railway",
    )
    get_settings.cache_clear()
    settings = Settings()
    assert settings.database_url.startswith("postgresql://")
    assert "sslmode=require" in settings.database_url
    get_settings.cache_clear()
