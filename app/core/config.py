"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.db.dialect import normalize_database_url

INSECURE_APP_SECRETS = frozenset(
    {
        "",
        "local-dev-change-me",
        "change-this-before-production",
        "bitte-aendern",
    }
)
MIN_PRODUCTION_SECRET_LENGTH = 16
SESSION_COOKIE_NAME = "ol_session"


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
    bootstrap_admin_identifier: str = Field(
        default="",
        alias="BOOTSTRAP_ADMIN_IDENTIFIER",
    )
    bootstrap_admin_password: str = Field(
        default="",
        alias="BOOTSTRAP_ADMIN_PASSWORD",
    )

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
    def is_production_like(self) -> bool:
        """Return True for any environment that is not local development."""
        return self.app_env.strip().lower() not in {"local", "test", "dev"}

    def assert_production_safety(self) -> None:
        """Refuse to start with insecure defaults outside local development."""
        if not self.is_production_like:
            return
        problems: list[str] = []
        secret = self.app_secret.strip()
        if secret in INSECURE_APP_SECRETS:
            problems.append("APP_SECRET ist noch der unsichere Standardwert.")
        elif len(secret) < MIN_PRODUCTION_SECRET_LENGTH:
            problems.append(
                "APP_SECRET muss in Produktion mindestens "
                f"{MIN_PRODUCTION_SECRET_LENGTH} Zeichen haben."
            )
        if self.app_debug:
            problems.append("APP_DEBUG muss in Produktion deaktiviert sein.")
        if problems:
            raise RuntimeError(
                "Unsichere Konfiguration fuer APP_ENV="
                f"{self.app_env!r}: " + " ".join(problems)
            )

    def require_production_secret(self) -> None:
        """Backward-compatible wrapper around assert_production_safety."""
        try:
            self.assert_production_safety()
        except RuntimeError as error:
            raise ValueError(str(error)) from error

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
