"""Database dialect helpers for SQLite and PostgreSQL."""

from __future__ import annotations

import re
from enum import StrEnum
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse


class DbDialect(StrEnum):
    """Supported database backends."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


def normalize_database_url(database_url: str) -> str:
    """Rewrite Railway-style Postgres URLs so psycopg can connect."""
    url = (database_url or "").strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if not (
        url.startswith("postgresql://") or url.startswith("postgresql+psycopg://")
    ):
        return url
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    if "sslmode" not in query and host and not (
        host in {"localhost", "127.0.0.1"} or host.endswith(".railway.internal")
    ):
        query["sslmode"] = "require"
    return urlunparse(parsed._replace(query=urlencode(query)))


def detect_dialect(database_url: str) -> DbDialect:
    """Return the dialect for one database URL."""
    url = normalize_database_url(database_url)
    if url.startswith("postgresql://") or url.startswith("postgres://"):
        return DbDialect.POSTGRESQL
    if url.startswith("sqlite:///"):
        return DbDialect.SQLITE
    raise ValueError("DATABASE_URL must use sqlite:/// or postgresql://")


def adapt_sql(sql: str, dialect: DbDialect) -> str:
    """Translate SQLite-style SQL to the target dialect when needed."""
    if dialect is DbDialect.SQLITE:
        return sql
    adapted = sql.replace("?", "%s")
    adapted = adapted.replace("INSERT OR IGNORE", "INSERT")
    return adapted


def adapt_schema_sql(sql: str, dialect: DbDialect) -> str:
    """Return DDL adapted for PostgreSQL while keeping SQLite syntax intact."""
    if dialect is DbDialect.SQLITE:
        return sql
    adapted = re.sub(
        r"\bINTEGER PRIMARY KEY AUTOINCREMENT\b",
        "SERIAL PRIMARY KEY",
        sql,
    )
    adapted = adapted.replace("datetime('now')", "CURRENT_TIMESTAMP")
    adapted = adapted.replace("INSERT OR IGNORE", "INSERT")
    return adapted


def insert_ignore_sql(
    table: str,
    columns: str,
    placeholders: str,
    conflict_target: str,
    dialect: DbDialect,
) -> str:
    """Return an idempotent INSERT statement for the target dialect."""
    if dialect is DbDialect.SQLITE:
        return (
            f"INSERT OR IGNORE INTO {table} ({columns}) VALUES ({placeholders})"
        )
    return (
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
        f"ON CONFLICT ({conflict_target}) DO NOTHING"
    )


def returning_id_clause(dialect: DbDialect) -> str:
    """Return SQL suffix for fetching inserted row ids on PostgreSQL."""
    if dialect is DbDialect.SQLITE:
        return ""
    return " RETURNING id"
