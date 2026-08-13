"""Import platform seed content (formulas, diagnosis, videos, glossary)."""

from __future__ import annotations

import json

from app.data.platform_content import (
    DEFAULT_APP_SETTINGS,
    DIAGNOSIS_CASES,
    FORMULAS,
    MEDIA_ASSETS,
    TRANSLATIONS,
    VIDEO_LESSONS,
)
from app.db.dialect import insert_ignore_sql
from app.services.database import Database, utc_now_iso
from app.services.platform_repository import PlatformRepository


class PlatformSeeder:
    """Idempotent importer for learning-tool seed rows."""

    def __init__(self, database: Database) -> None:
        """Attach to an initialized application database."""
        self.database = database
        self.repository = PlatformRepository(database)

    def is_empty(self) -> bool:
        """Return True when Formeltrainer content is missing."""
        return self.repository.is_empty()

    def seed_all(self, *, force: bool = False) -> dict[str, int]:
        """Import formulas, diagnosis cases, videos, translations, and settings."""
        if force:
            self._clear()
        elif not self.is_empty():
            return self.repository.counts()

        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            for formula in FORMULAS:
                connection.execute(
                    insert_ignore_sql(
                        "formulas",
                        "slug, topic, title, expression, legend_json, example, "
                        "difficulty, source_keys_json, created_at",
                        "?, ?, ?, ?, ?, ?, ?, ?, ?",
                        "slug",
                        connection.dialect,
                    ),
                    (
                        formula["slug"],
                        formula["topic"],
                        formula["title"],
                        formula["expression"],
                        json.dumps(formula["legend"], ensure_ascii=False),
                        formula["example"],
                        formula["difficulty"],
                        json.dumps(formula["source_keys"], ensure_ascii=False),
                        timestamp,
                    ),
                )
            for case in DIAGNOSIS_CASES:
                connection.execute(
                    insert_ignore_sql(
                        "diagnosis_cases",
                        "slug, topic, title, symptom, options_json, "
                        "correct_option_index, explanation, difficulty, "
                        "estimated_minutes, created_at",
                        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
                        "slug",
                        connection.dialect,
                    ),
                    (
                        case["slug"],
                        case["topic"],
                        case["title"],
                        case["symptom"],
                        json.dumps(case["options"], ensure_ascii=False),
                        case["correct_option_index"],
                        case["explanation"],
                        case["difficulty"],
                        case["estimated_minutes"],
                        timestamp,
                    ),
                )
            for video in VIDEO_LESSONS:
                connection.execute(
                    insert_ignore_sql(
                        "video_lessons",
                        "slug, title, description, instructor, duration_seconds, "
                        "topic, thumbnail_url, video_url, chapters_json, "
                        "next_slug, created_at",
                        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
                        "slug",
                        connection.dialect,
                    ),
                    (
                        video["slug"],
                        video["title"],
                        video["description"],
                        video["instructor"],
                        video["duration_seconds"],
                        video["topic"],
                        video["thumbnail_url"],
                        video["video_url"],
                        json.dumps(video["chapters"], ensure_ascii=False),
                        video["next_slug"],
                        timestamp,
                    ),
                )
            for item in TRANSLATIONS:
                connection.execute(
                    insert_ignore_sql(
                        "translations",
                        "term, language, translation, definition",
                        "?, ?, ?, ?",
                        "term, language",
                        connection.dialect,
                    ),
                    (
                        item["term"],
                        item["language"],
                        item["translation"],
                        item["definition"],
                    ),
                )
            for asset in MEDIA_ASSETS:
                connection.execute(
                    insert_ignore_sql(
                        "media_assets",
                        "slug, title, media_type, url, created_at",
                        "?, ?, ?, ?, ?",
                        "slug",
                        connection.dialect,
                    ),
                    (
                        asset["slug"],
                        asset["title"],
                        asset["media_type"],
                        asset["url"],
                        timestamp,
                    ),
                )
            for key, value in DEFAULT_APP_SETTINGS.items():
                connection.execute(
                    insert_ignore_sql(
                        "app_settings",
                        "key, value_json, updated_at",
                        "?, ?, ?",
                        "key",
                        connection.dialect,
                    ),
                    (key, json.dumps(value), timestamp),
                )
        return self.repository.counts()

    def _clear(self) -> None:
        """Remove seeded tool content while keeping learner rows."""
        tables = (
            "formula_progress",
            "diagnosis_progress",
            "video_progress",
            "formulas",
            "diagnosis_cases",
            "video_lessons",
            "translations",
            "media_assets",
            "app_settings",
        )
        with self.database._transaction() as connection:
            for table in tables:
                connection.execute(f"DELETE FROM {table}")
