"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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
    content_seed_on_startup: bool = Field(default=True, alias="CONTENT_SEED_ON_STARTUP")
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

    @property
    def allowed_origins(self) -> list[str]:
        """Return configured CORS origins as a clean list."""
        return [
            origin.strip()
            for origin in self.allowed_origins_raw.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
