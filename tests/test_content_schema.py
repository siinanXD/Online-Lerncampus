"""Tests for the content database schema (Phase 1)."""

import sqlite3
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

from app.db.content_schema import CONTENT_TABLES, initialize_content_schema, list_content_tables
from app.db.platform_schema import list_platform_tables
from app.main import create_app
from app.services.database import Database


def test_content_schema_creates_all_tables(tmp_path: Path) -> None:
    """Fresh databases must contain every planned content table."""
    db_path = tmp_path / "schema-test.db"
    connection = sqlite3.connect(db_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(
        """
        CREATE TABLE learners (
            learner_id TEXT PRIMARY KEY,
            identifier_hash TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            role TEXT NOT NULL,
            cohort_code TEXT,
            password_hash TEXT,
            created_at TEXT NOT NULL,
            deleted_at TEXT
        );
        """
    )
    initialize_content_schema(connection)
    connection.commit()

    present = list_content_tables(connection)
    assert present == set(CONTENT_TABLES)
    connection.close()


def test_database_class_applies_content_schema(tmp_path: Path) -> None:
    """Database startup must initialize learner and content tables together."""
    db_path = tmp_path / "app-test.db"
    database = Database(f"sqlite:///{db_path.as_posix()}")
    with database._transaction() as connection:
        present = list_content_tables(connection)
        platform = list_platform_tables(connection)
    assert "quiz_questions" in present
    assert "learning_units" in present
    assert "exam_sessions" in present
    assert "formulas" in platform
    assert "diagnosis_cases" in platform
    assert "learner_preferences" in platform


def test_existing_app_still_boots_with_content_schema() -> None:
    """API smoke test after schema extension."""
    client = TestClient(create_app())
    login_id = f"schema-smoke-{uuid4()}"
    login = client.post(
        "/api/auth/login",
        json={
            "identifier": login_id,
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert login.status_code == 200
    assert client.get("/api/health").json()["status"] == "ok"
    assert len(client.get("/api/questions?month=1").json()) == 20
