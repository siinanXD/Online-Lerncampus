"""Content database schema loader for SQLite initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path

_SCHEMA_PATH = Path(__file__).with_name("content_schema.sql")


def _load_schema_sql() -> str:
    """Return the content DDL script without SQLite-only pragma lines."""
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    lines = [
        line
        for line in raw.splitlines()
        if not line.strip().upper().startswith("PRAGMA ")
    ]
    return "\n".join(lines)


CONTENT_SCHEMA_SQL = _load_schema_sql()

CONTENT_TABLES: tuple[str, ...] = (
    "occupations",
    "specializations",
    "curriculum_months",
    "learning_modules",
    "source_documents",
    "content_reviews",
    "question_categories",
    "learning_units",
    "theory_blocks",
    "glossary_entries",
    "learning_unit_categories",
    "quiz_questions",
    "open_questions",
    "open_question_criteria",
    "content_source_links",
    "practice_exams",
    "exam_quiz_questions",
    "exam_open_questions",
    "category_progress",
    "unit_progress",
    "exam_sessions",
    "exam_session_answers",
    "exam_session_open_answers",
    "schema_migrations",
)


def initialize_content_schema(connection: Any) -> None:
    """Create content tables when they do not exist yet."""
    connection.executescript(CONTENT_SCHEMA_SQL)


def list_content_tables(connection: sqlite3.Connection) -> set[str]:
    """Return content table names that exist in the database."""
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        """
    ).fetchall()
    names = {row[0] for row in rows}
    return names.intersection(CONTENT_TABLES)
