"""Database dialect helpers for SQLite and PostgreSQL."""

from __future__ import annotations

import re
from enum import StrEnum


class DbDialect(StrEnum):
    """Supported database backends."""

    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"


def detect_dialect(database_url: str) -> DbDialect:
    """Return the dialect for one database URL."""
    if database_url.startswith("postgresql://") or database_url.startswith(
        "postgres://"
    ):
        return DbDialect.POSTGRESQL
    if database_url.startswith("sqlite:///"):
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
