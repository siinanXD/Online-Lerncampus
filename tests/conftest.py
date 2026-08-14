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
    monkeypatch.setenv("CONTENT_REVIEW_REQUIRED", "false")
    monkeypatch.setenv("CONTENT_SEED_FORMAT", "python")
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


STAFF_TEST_PASSWORD = "Staff-Pass1!"


def provision_staff(
    role: str = "trainer",
    *,
    cohort_code: str | None = None,
    tenant_id: str | None = None,
    platform_admin: bool = False,
    identifier: str | None = None,
    password: str = STAFF_TEST_PASSWORD,
) -> tuple[str, str]:
    """Create a staff account directly, as an admin would via the API."""
    from uuid import uuid4

    from app.api import routes

    routes.bootstrap_content_store()
    account = identifier or f"{role}-{uuid4()}"
    routes._auth().provision_user(
        identifier=account,
        password=password,
        role=role,
        cohort_code=cohort_code,
        tenant_id=tenant_id,
        is_platform_admin=platform_admin,
    )
    return account, password


def staff_login(
    client,
    role: str = "trainer",
    *,
    cohort_code: str | None = None,
    tenant_id: str | None = None,
    platform_admin: bool = False,
) -> tuple[dict[str, str], dict[str, object]]:
    """Provision a staff account and return auth headers plus login payload."""
    identifier, password = provision_staff(
        role,
        cohort_code=cohort_code,
        tenant_id=tenant_id,
        platform_admin=platform_admin,
    )
    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": password},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    headers = {"Authorization": f"Bearer {payload['access_token']}"}
    return headers, payload


def correct_option_index(question_id: str) -> int:
    """Return the correct option index from the app's content store."""
    from app.api import routes

    assert routes.question_repository is not None
    question = routes.question_repository.get_question(question_id)
    assert question is not None
    return question.correct_option_index


def pytest_configure(config: pytest.Config) -> None:
    """Default tests to DB mode unless overridden before collection."""
    os.environ.setdefault("CONTENT_SOURCE", "db")
    os.environ.setdefault("CONTENT_SEED_ON_STARTUP", "true")
