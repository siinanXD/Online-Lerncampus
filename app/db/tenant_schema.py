"""Tenant and cohort schema plus default seed data."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from app.db.dialect import DbDialect, insert_ignore_sql

_SCHEMA_PATH = Path(__file__).with_name("tenant_schema.sql")

DEFAULT_TENANT_ID = "bze-euskirchen"
DEFAULT_COHORT_CODE = "BZE-2026-F"


def _utc_now_iso() -> str:
    """Return the current UTC timestamp as ISO string."""
    return datetime.now(tz=UTC).isoformat()

DEFAULT_TENANTS: tuple[dict[str, str], ...] = (
    {
        "tenant_id": "bze-euskirchen",
        "name": "BZE Euskirchen",
        "slug": "bze-euskirchen",
    },
    {
        "tenant_id": "campus-demo",
        "name": "Campus Demo",
        "slug": "campus-demo",
    },
)

DEFAULT_COHORTS: tuple[dict[str, str], ...] = (
    {
        "cohort_id": "bze-2026-f",
        "tenant_id": "bze-euskirchen",
        "code": "BZE-2026-F",
        "name": "Fachklasse Metall 2026",
    },
    {
        "cohort_id": "bze-2026-k",
        "tenant_id": "bze-euskirchen",
        "code": "BZE-2026-K",
        "name": "Fachklasse Kunststoff 2026",
    },
    {
        "cohort_id": "demo-2026-a",
        "tenant_id": "campus-demo",
        "code": "DEMO-2026-A",
        "name": "Demo-Kohorte 2026",
    },
)


def _load_schema_sql() -> str:
    """Return tenant DDL without SQLite-only pragma lines."""
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    return "\n".join(
        line
        for line in raw.splitlines()
        if not line.strip().upper().startswith("PRAGMA ")
    )


TENANT_SCHEMA_SQL = _load_schema_sql()


def initialize_tenant_schema(connection: Any) -> None:
    """Create tenant tables, learner columns, and seed default organisations."""
    connection.executescript(TENANT_SCHEMA_SQL)
    _ensure_learner_tenant_columns(connection)
    _ensure_learner_tenant_indexes(connection)
    _seed_default_tenants(connection)
    _backfill_learner_tenants(connection)


def _column_names(connection: Any, table: str) -> set[str]:
    """Return column names for one table."""
    dialect = getattr(connection, "dialect", None)
    dialect_value = getattr(dialect, "value", str(dialect or "sqlite"))
    if dialect_value == "postgresql":
        rows = connection.execute(
            """
            SELECT column_name AS name
            FROM information_schema.columns
            WHERE table_name = ?
            """,
            (table,),
        ).fetchall()
        return {
            row["name"] if not isinstance(row, tuple) else row[0]
            for row in rows
        }
    rows = connection.execute(f"PRAGMA table_info({table})").fetchall()
    return {
        row["name"] if not isinstance(row, tuple) else row[1]
        for row in rows
    }


def _ensure_learner_tenant_columns(connection: Any) -> None:
    """Add tenant isolation columns on existing learner tables."""
    dialect = getattr(connection, "dialect", None)
    dialect_value = getattr(dialect, "value", str(dialect or "sqlite"))
    if dialect_value == "postgresql":
        connection.execute(
            """
            ALTER TABLE learners
            ADD COLUMN IF NOT EXISTS tenant_id TEXT
            """
        )
        connection.execute(
            """
            ALTER TABLE learners
            ADD COLUMN IF NOT EXISTS is_platform_admin INTEGER NOT NULL DEFAULT 0
            """
        )
        return
    columns = _column_names(connection, "learners")
    if "tenant_id" not in columns:
        connection.execute("ALTER TABLE learners ADD COLUMN tenant_id TEXT")
    if "is_platform_admin" not in columns:
        connection.execute(
            """
            ALTER TABLE learners
            ADD COLUMN is_platform_admin INTEGER NOT NULL DEFAULT 0
            """
        )


def _ensure_learner_tenant_indexes(connection: Any) -> None:
    """Index tenant and cohort lookups after the columns exist."""
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_learners_tenant ON learners (tenant_id)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_learners_cohort ON learners (cohort_code)"
    )


def _seed_default_tenants(connection: Any) -> None:
    """Insert the built-in BZE and demo organisations."""
    timestamp = _utc_now_iso()
    dialect = getattr(connection, "dialect", DbDialect.SQLITE)
    tenant_sql = insert_ignore_sql(
        "tenants",
        "tenant_id, name, slug, status, created_at",
        "?, ?, ?, 'active', ?",
        "tenant_id",
        dialect,
    )
    cohort_sql = insert_ignore_sql(
        "cohorts",
        "cohort_id, tenant_id, code, name, created_at",
        "?, ?, ?, ?, ?",
        "cohort_id",
        dialect,
    )
    for tenant in DEFAULT_TENANTS:
        connection.execute(
            tenant_sql,
            (tenant["tenant_id"], tenant["name"], tenant["slug"], timestamp),
        )
    for cohort in DEFAULT_COHORTS:
        connection.execute(
            cohort_sql,
            (
                cohort["cohort_id"],
                cohort["tenant_id"],
                cohort["code"],
                cohort["name"],
                timestamp,
            ),
        )


def _backfill_learner_tenants(connection: Any) -> None:
    """Attach existing non-platform accounts to the default BZE tenant."""
    connection.execute(
        """
        UPDATE learners
        SET tenant_id = ?
        WHERE tenant_id IS NULL
            AND COALESCE(is_platform_admin, 0) = 0
            AND deleted_at IS NULL
        """,
        (DEFAULT_TENANT_ID,),
    )
    connection.execute(
        """
        UPDATE learners
        SET cohort_code = ?
        WHERE (cohort_code IS NULL OR cohort_code = '')
            AND COALESCE(is_platform_admin, 0) = 0
            AND role = 'learner'
            AND deleted_at IS NULL
        """,
        (DEFAULT_COHORT_CODE,),
    )
