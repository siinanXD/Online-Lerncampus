"""Alembic migration for learner tools, preferences, and staff extras."""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "003_platform_features"
down_revision = "002_training_reports"
branch_labels = None
depends_on = None

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "app" / "db" / "platform_schema.sql"
)

_DOWNGRADE_TABLES = (
    "app_settings",
    "media_assets",
    "content_flags",
    "translations",
    "video_progress",
    "video_lessons",
    "diagnosis_progress",
    "diagnosis_cases",
    "formula_progress",
    "formulas",
    "daily_goal_progress",
    "notifications",
    "notification_settings",
    "learner_preferences",
)


def upgrade() -> None:
    """Apply platform feature tables and Berichtsheft signature columns."""
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in raw.split(";")
        if statement.strip() and not statement.strip().upper().startswith("PRAGMA ")
    ]
    for statement in statements:
        op.execute(statement)


def downgrade() -> None:
    """Drop platform tables. Signature columns stay on training_reports."""
    for table in _DOWNGRADE_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table}")
