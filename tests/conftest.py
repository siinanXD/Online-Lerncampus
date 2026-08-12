"""Pytest configuration for isolated database-backed tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.core.config import get_settings


@pytest.fixture(autouse=True)
def isolated_test_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Give each test its own SQLite database and DB-backed content store."""
    db_path = tmp_path / "pytest.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("CONTENT_SOURCE", "db")
    monkeypatch.setenv("CONTENT_SEED_ON_STARTUP", "true")
    get_settings.cache_clear()

    import app.api.routes as routes

    routes.database = None
    routes.auth_service = None
    routes.question_repository = None
    routes.progress_service = None
    routes.exam_session_service = None

    yield

    get_settings.cache_clear()


def pytest_configure(config: pytest.Config) -> None:
    """Default tests to DB mode unless overridden before collection."""
    os.environ.setdefault("CONTENT_SOURCE", "db")
    os.environ.setdefault("CONTENT_SEED_ON_STARTUP", "true")
