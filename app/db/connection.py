"""Unified database connection wrapper for SQLite and PostgreSQL."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any

from app.db.dialect import DbDialect, adapt_schema_sql, adapt_sql, detect_dialect


class DbConnection:
    """Expose one DB-API connection with SQLite-style placeholders."""

    def __init__(self, database_url: str) -> None:
        """Open a SQLite or PostgreSQL connection."""
        self.database_url = database_url
        self.dialect = detect_dialect(database_url)
        self._lock = RLock()
        if self.dialect is DbDialect.SQLITE:
            database_path = Path(database_url.removeprefix("sqlite:///")).resolve()
            database_path.parent.mkdir(parents=True, exist_ok=True)
            self._connection = sqlite3.connect(
                database_path,
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON")
        else:
            import psycopg
            from psycopg.rows import dict_row

            self._connection = psycopg.connect(database_url, row_factory=dict_row)

    @contextmanager
    def transaction(self) -> Iterator["DbConnection"]:
        """Run one commit/rollback cycle under a thread lock."""
        with self._lock:
            try:
                yield self
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def execute(self, sql: str, params: tuple[Any, ...] | list[Any] = ()) -> Any:
        """Execute one statement using ``?`` placeholders."""
        return self._connection.execute(adapt_sql(sql, self.dialect), params)

    def executescript(self, sql: str) -> None:
        """Execute a DDL script statement by statement."""
        if self.dialect is DbDialect.SQLITE:
            self._connection.executescript(sql)
            return
        adapted = adapt_schema_sql(sql, self.dialect)
        statements = [
            statement.strip()
            for statement in adapted.split(";")
            if statement.strip() and not statement.strip().upper().startswith("PRAGMA ")
        ]
        for statement in statements:
            if (
                statement.upper().startswith("INSERT INTO SCHEMA_MIGRATIONS")
                and "ON CONFLICT" not in statement.upper()
            ):
                statement = f"{statement} ON CONFLICT (version) DO NOTHING"
            self._connection.execute(statement)

    def fetch_scalar(self, sql: str, params: tuple[Any, ...] = ()) -> Any:
        """Return the first column of the first row."""
        row = self.execute(sql, params).fetchone()
        if row is None:
            return None
        if isinstance(row, sqlite3.Row):
            return row[0]
        if isinstance(row, dict):
            return next(iter(row.values()))
        return row[0]

    def insert_returning_id(
        self,
        sql: str,
        params: tuple[Any, ...],
    ) -> int:
        """Insert one row and return its primary key."""
        if self.dialect is DbDialect.SQLITE:
            cursor = self.execute(sql, params)
            return int(cursor.lastrowid)
        cursor = self.execute(f"{sql} RETURNING id", params)
        row = cursor.fetchone()
        assert row is not None
        if isinstance(row, dict):
            return int(row["id"])
        return int(row[0])
