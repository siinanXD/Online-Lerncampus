"""Tests for JSON bundle export/load and PostgreSQL dialect helpers."""

from pathlib import Path

import pytest

from app.data.content_bundle import (
    bundle_to_json,
    load_json_bundle,
    load_python_bundle,
)
from app.db.dialect import (
    DbDialect,
    adapt_schema_sql,
    adapt_sql,
    detect_dialect,
    group_concat_sql,
    insert_ignore_sql,
)


def test_python_and_json_bundles_match_question_count(tmp_path: Path) -> None:
    """JSON export/load must preserve the full MAF question bank."""
    python_bundle = load_python_bundle()
    json_path = tmp_path / "bundle.json"
    json_path.write_text(
        __import__("json").dumps(bundle_to_json(python_bundle), ensure_ascii=False),
        encoding="utf-8",
    )
    json_bundle = load_json_bundle(json_path)
    assert len(json_bundle.questions) == len(python_bundle.questions) == 480
    assert len(json_bundle.units) == len(python_bundle.units) == 240
    assert len(json_bundle.open_questions) == len(python_bundle.open_questions) == 120


def test_detect_dialect_supports_sqlite_and_postgresql() -> None:
    """Database URL parsing must distinguish local SQLite and prod PostgreSQL."""
    assert detect_dialect("sqlite:///./local.db") is DbDialect.SQLITE
    assert (
        detect_dialect("postgresql://user:pass@localhost/lerncampus")
        is DbDialect.POSTGRESQL
    )
    assert (
        detect_dialect("postgres://user:pass@localhost/lerncampus")
        is DbDialect.POSTGRESQL
    )


def test_normalize_database_url_rewrites_railway_postgres() -> None:
    """Railway still emits postgres:// and public hosts need SSL."""
    from app.db.dialect import normalize_database_url

    local = normalize_database_url("postgres://user:pass@localhost:5432/db")
    assert local.startswith("postgresql://")
    assert "sslmode" not in local

    internal = normalize_database_url(
        "postgresql://user:pass@postgres.railway.internal:5432/railway"
    )
    assert "sslmode" not in internal

    public = normalize_database_url(
        "postgres://user:pass@shuttle.proxy.rlwy.net:1234/railway"
    )
    assert public.startswith("postgresql://")
    assert "sslmode=require" in public


def test_postgres_schema_adaptation_rewrites_autoincrement() -> None:
    """PostgreSQL DDL must replace SQLite-only syntax."""
    adapted = adapt_schema_sql(
        "CREATE TABLE demo (id INTEGER PRIMARY KEY AUTOINCREMENT);",
        DbDialect.POSTGRESQL,
    )
    assert "SERIAL PRIMARY KEY" in adapted
    assert "AUTOINCREMENT" not in adapted


def test_insert_ignore_sql_is_dialect_specific() -> None:
    """Idempotent inserts must work on SQLite and PostgreSQL."""
    sqlite_sql = insert_ignore_sql(
        "content_source_links",
        "source_id, entity_type, entity_id",
        "?, ?, ?",
        "source_id, entity_type, entity_id",
        DbDialect.SQLITE,
    )
    postgres_sql = insert_ignore_sql(
        "content_source_links",
        "source_id, entity_type, entity_id",
        "?, ?, ?",
        "source_id, entity_type, entity_id",
        DbDialect.POSTGRESQL,
    )
    assert "INSERT OR IGNORE" in sqlite_sql
    assert "ON CONFLICT" in postgres_sql


def test_postgres_sql_rewrites_group_concat() -> None:
    """PostgreSQL has no GROUP_CONCAT; learning queries must use STRING_AGG."""
    sqlite_sql = (
        "SELECT GROUP_CONCAT(DISTINCT sd.key) AS source_keys "
        "FROM source_documents sd"
    )
    postgres_sql = adapt_sql(sqlite_sql, DbDialect.POSTGRESQL)
    assert "GROUP_CONCAT" not in postgres_sql.upper()
    assert "STRING_AGG(DISTINCT sd.key, ',')" in postgres_sql
    assert group_concat_sql("qc.slug", DbDialect.SQLITE) == "GROUP_CONCAT(DISTINCT qc.slug)"
    assert (
        group_concat_sql("qc.slug", DbDialect.POSTGRESQL)
        == "STRING_AGG(DISTINCT qc.slug, ',')"
    )
