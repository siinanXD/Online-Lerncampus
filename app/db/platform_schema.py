"""Platform database schema loader for preferences, tools, and staff extras."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

_SCHEMA_PATH = Path(__file__).with_name("platform_schema.sql")


def _load_schema_sql() -> str:
    """Return the platform DDL script without SQLite-only pragma lines."""
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    lines = [
        line
        for line in raw.splitlines()
        if not line.strip().upper().startswith("PRAGMA ")
    ]
    return "\n".join(lines)


PLATFORM_SCHEMA_SQL = _load_schema_sql()

PLATFORM_TABLES: tuple[str, ...] = (
    "learner_preferences",
    "notification_settings",
    "notifications",
    "daily_goal_progress",
    "formulas",
    "formula_progress",
    "diagnosis_cases",
    "diagnosis_progress",
    "video_lessons",
    "video_progress",
    "translations",
    "content_flags",
    "media_assets",
    "app_settings",
)


def initialize_platform_schema(connection: Any) -> None:
    """Create platform tables when they do not exist yet."""
    connection.executescript(PLATFORM_SCHEMA_SQL)
    _ensure_training_report_columns(connection)
    _ensure_learner_preference_columns(connection)


def _ensure_learner_preference_columns(connection: Any) -> None:
    """Add onboarding flag when upgrading an existing preferences table."""
    dialect = getattr(connection, "dialect", None)
    dialect_value = getattr(dialect, "value", str(dialect or "sqlite"))
    if dialect_value == "postgresql":
        connection.execute(
            """
            ALTER TABLE learner_preferences
            ADD COLUMN IF NOT EXISTS onboarding_completed INTEGER NOT NULL DEFAULT 0
            """
        )
        return
    rows = connection.execute("PRAGMA table_info(learner_preferences)").fetchall()
    columns = {
        row["name"] if not isinstance(row, tuple) else row[1]
        for row in rows
    }
    if "onboarding_completed" not in columns:
        connection.execute(
            """
            ALTER TABLE learner_preferences
            ADD COLUMN onboarding_completed INTEGER NOT NULL DEFAULT 0
            """
        )
        connection.execute(
            "UPDATE learner_preferences SET onboarding_completed = 1"
        )


def _ensure_training_report_columns(connection: Any) -> None:
    """Add signature columns when upgrading an existing Berichtsheft table."""
    dialect = getattr(connection, "dialect", None)
    dialect_value = getattr(dialect, "value", str(dialect or "sqlite"))
    if dialect_value == "postgresql":
        connection.execute(
            """
            ALTER TABLE training_reports
            ADD COLUMN IF NOT EXISTS signed_at TEXT
            """
        )
        connection.execute(
            """
            ALTER TABLE training_reports
            ADD COLUMN IF NOT EXISTS trainer_status TEXT
            """
        )
        return
    rows = connection.execute("PRAGMA table_info(training_reports)").fetchall()
    columns = {
        row["name"] if not isinstance(row, tuple) else row[1]
        for row in rows
    }
    if "signed_at" not in columns:
        connection.execute("ALTER TABLE training_reports ADD COLUMN signed_at TEXT")
    if "trainer_status" not in columns:
        connection.execute(
            "ALTER TABLE training_reports ADD COLUMN trainer_status TEXT"
        )


def list_platform_tables(connection: sqlite3.Connection) -> set[str]:
    """Return platform table names that exist in the database."""
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()
    names = {row[0] for row in rows}
    return names.intersection(PLATFORM_TABLES)
