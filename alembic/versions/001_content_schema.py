"""Content schema: occupations through exam sessions."""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "001_content_schema"
down_revision = None
branch_labels = None
depends_on = None

_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "app" / "db" / "content_schema.sql"
)

_DOWNGRADE_TABLES = (
    "exam_session_open_answers",
    "exam_session_answers",
    "exam_sessions",
    "unit_progress",
    "category_progress",
    "exam_open_questions",
    "exam_quiz_questions",
    "practice_exams",
    "content_source_links",
    "open_question_criteria",
    "open_questions",
    "quiz_questions",
    "learning_unit_categories",
    "glossary_entries",
    "theory_blocks",
    "learning_units",
    "question_categories",
    "content_reviews",
    "source_documents",
    "learning_modules",
    "curriculum_months",
    "specializations",
    "occupations",
    "schema_migrations",
)


_LEARNER_BOOTSTRAP_SQL = """
CREATE TABLE IF NOT EXISTS learners (
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


def upgrade() -> None:
    """Apply learner bootstrap (if needed) and the content DDL script."""
    op.execute(_LEARNER_BOOTSTRAP_SQL)
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in raw.split(";")
        if statement.strip() and not statement.strip().upper().startswith("PRAGMA ")
    ]
    for statement in statements:
        op.execute(statement)


def downgrade() -> None:
    """Drop content tables in reverse dependency order."""
    for table in _DOWNGRADE_TABLES:
        op.execute(f"DROP TABLE IF EXISTS {table}")
