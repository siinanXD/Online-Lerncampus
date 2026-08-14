"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.db.dialect import normalize_database_url

_WEAK_SECRETS = {
    "",
    "local-dev-change-me",
    "change-this-before-production",
    "bitte-aendern",
}


class Settings(BaseSettings):
    """Runtime settings for the application."""

    app_name: str = "Online Lerncampus"
    app_env: str = "local"
    app_debug: bool = True
    allowed_origins_raw: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        alias="ALLOWED_ORIGINS",
    )
    content_review_required: bool = True
    content_source: str = Field(default="db", alias="CONTENT_SOURCE")
    content_seed_format: str = Field(default="python", alias="CONTENT_SEED_FORMAT")
    content_seed_on_startup: bool = Field(default=True, alias="CONTENT_SEED_ON_STARTUP")
    content_json_bundle_path: str = Field(
        default="app/content/maf/v1/bundle.json",
        alias="CONTENT_JSON_BUNDLE_PATH",
    )
    ai_provider: str = "disabled"
    database_url: str = "sqlite:///./local.db"
    app_secret: str = "local-dev-change-me"
    session_ttl_hours: int = 12
    privacy_notice_version: str = "2026-08-12-mvp"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("database_url")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        """Accept Railway postgres:// URLs and add SSL for public hosts."""
        return normalize_database_url(value)

    @property
    def allowed_origins(self) -> list[str]:
        """Return configured CORS origins as a clean list."""
        return [
            origin.strip()
            for origin in self.allowed_origins_raw.split(",")
            if origin.strip()
        ]

    def require_production_secret(self) -> None:
        """Refuse to boot in production with a placeholder APP_SECRET."""
        if self.app_env != "production":
            return
        secret = self.app_secret.strip()
        if secret in _WEAK_SECRETS or len(secret) < 16:
            raise ValueError(
                "APP_SECRET must be a random value with at least 16 characters in production."
            )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
