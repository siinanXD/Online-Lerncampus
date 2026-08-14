"""Tests for the content seed importer."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.services.content_seeder import ContentSeeder
from app.services.database import Database


def test_seed_import_populates_content_tables(tmp_path: Path) -> None:
    """Seed import must load the full MAF bundle into SQLite."""
    database = Database(f"sqlite:///{tmp_path / 'seed.db'}")
    seeder = ContentSeeder(database)

    assert seeder.is_empty() is True
    counts = seeder.seed_all()
    assert counts["quiz_questions"] == 480
    assert counts["learning_units"] == 240
    assert counts["open_questions"] == 120
    assert counts["question_categories"] == 240
    assert seeder.is_empty() is False

    # Idempotent second run
    again = seeder.seed_all()
    assert again["quiz_questions"] == 480


def test_seeded_content_is_live_with_review_gate_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fresh installs must show the curated bundle even with the review gate on."""
    monkeypatch.setenv("CONTENT_REVIEW_REQUIRED", "true")
    get_settings.cache_clear()

    from app.main import create_app

    client = TestClient(create_app())
    stats = client.get("/api/content/stats")
    assert stats.status_code == 200
    payload = stats.json()
    assert payload["learning_units"] == 240
    assert payload["quiz_questions"] == 480
    units = client.get("/api/learning/units?month=1")
    assert units.status_code == 200
    assert units.json()
    assert all(unit["review_status"] == "approved" for unit in units.json())


def test_seed_force_reimports_after_clear(tmp_path: Path) -> None:
    """Force mode must rebuild content from scratch."""
    database = Database(f"sqlite:///{tmp_path / 'force-seed.db'}")
    seeder = ContentSeeder(database)
    seeder.seed_all()
    seeder.seed_all(force=True)
    counts = seeder.counts()
    assert counts["quiz_questions"] == 480
