"""SQLite persistence for learner sessions, progress, and privacy actions."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any

from app.db.content_schema import initialize_content_schema
from app.models.progress import QuestionProgress


def utc_now_iso() -> str:
    """Return the current UTC timestamp as ISO string."""
    return datetime.now(tz=UTC).isoformat()


class Database:
    """Small SQLite repository used by the local MVP backend."""

    def __init__(self, database_url: str) -> None:
        """Open the configured SQLite database and initialize its schema."""
        self.database_path = self._parse_sqlite_path(database_url)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()
        self._connection = sqlite3.connect(
            self.database_path,
            check_same_thread=False,
        )
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize_schema()

    @staticmethod
    def _parse_sqlite_path(database_url: str) -> Path:
        """Return a filesystem path from a sqlite URL."""
        prefix = "sqlite:///"
        if not database_url.startswith(prefix):
            raise ValueError("Only sqlite:/// DATABASE_URL values are supported.")
        raw_path = database_url.removeprefix(prefix)
        if not raw_path:
            raise ValueError("DATABASE_URL must include a sqlite file path.")
        return Path(raw_path).resolve()

    @contextmanager
    def _transaction(self) -> Iterator[sqlite3.Connection]:
        """Run database work under a thread lock and transaction."""
        with self._lock:
            try:
                yield self._connection
                self._connection.commit()
            except Exception:
                self._connection.rollback()
                raise

    def _initialize_schema(self) -> None:
        """Create all tables required by the MVP if they do not exist."""
        with self._transaction() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS learners (
                    learner_id TEXT PRIMARY KEY,
                    identifier_hash TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    cohort_code TEXT,
                    created_at TEXT NOT NULL,
                    deleted_at TEXT
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    token_hash TEXT PRIMARY KEY,
                    learner_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT,
                    FOREIGN KEY (learner_id) REFERENCES learners (learner_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS question_progress (
                    learner_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    answered_count INTEGER NOT NULL,
                    wrong_count INTEGER NOT NULL,
                    correct_streak INTEGER NOT NULL,
                    mastered INTEGER NOT NULL,
                    last_selected_option_index INTEGER,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (learner_id, question_id),
                    FOREIGN KEY (learner_id) REFERENCES learners (learner_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS consent_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    learner_id TEXT NOT NULL,
                    consent_version TEXT NOT NULL,
                    accepted INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (learner_id) REFERENCES learners (learner_id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    learner_id TEXT,
                    event_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                """
            )
            self._ensure_password_hash_column(connection)
            initialize_content_schema(connection)

    def _ensure_password_hash_column(self, connection: sqlite3.Connection) -> None:
        """Add password_hash when upgrading an existing local database."""
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(learners)").fetchall()
        }
        if "password_hash" not in columns:
            connection.execute("ALTER TABLE learners ADD COLUMN password_hash TEXT")

    def get_learner(self, learner_id: str) -> dict[str, Any] | None:
        """Return one active learner row by id."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT learner_id, identifier_hash, display_name, role,
                       cohort_code, password_hash
                FROM learners
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (learner_id,),
            ).fetchone()
        return dict(row) if row else None

    def get_learner_by_identifier_hash(
        self, identifier_hash: str
    ) -> dict[str, Any] | None:
        """Return one active learner row by pseudonymous login hash."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT learner_id, identifier_hash, display_name, role,
                       cohort_code, password_hash
                FROM learners
                WHERE identifier_hash = ? AND deleted_at IS NULL
                """,
                (identifier_hash,),
            ).fetchone()
        return dict(row) if row else None

    def upsert_learner(
        self,
        learner_id: str,
        identifier_hash: str,
        display_name: str,
        role: str,
        cohort_code: str | None,
        password_hash: str | None = None,
    ) -> None:
        """Create or update a learner profile without storing clear text login data."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO learners (
                    learner_id,
                    identifier_hash,
                    display_name,
                    role,
                    cohort_code,
                    password_hash,
                    created_at,
                    deleted_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                ON CONFLICT(learner_id) DO UPDATE SET
                    cohort_code = excluded.cohort_code,
                    password_hash = COALESCE(excluded.password_hash, learners.password_hash),
                    deleted_at = NULL
                """,
                (
                    learner_id,
                    identifier_hash,
                    display_name,
                    role,
                    cohort_code,
                    password_hash,
                    utc_now_iso(),
                ),
            )

    def update_password_hash(self, learner_id: str, password_hash: str) -> None:
        """Persist a new password hash for one learner."""
        with self._transaction() as connection:
            connection.execute(
                """
                UPDATE learners
                SET password_hash = ?
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (password_hash, learner_id),
            )

    def create_session(
        self,
        token_hash: str,
        learner_id: str,
        expires_at: datetime,
    ) -> None:
        """Persist a hashed bearer token for one learner."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO sessions (token_hash, learner_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (token_hash, learner_id, utc_now_iso(), expires_at.isoformat()),
            )

    def get_active_session(self, token_hash: str) -> dict[str, Any] | None:
        """Return an active session with learner data or None."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT
                    sessions.token_hash,
                    sessions.learner_id,
                    sessions.expires_at,
                    learners.display_name,
                    learners.role,
                    learners.cohort_code
                FROM sessions
                JOIN learners ON learners.learner_id = sessions.learner_id
                WHERE sessions.token_hash = ?
                    AND sessions.revoked_at IS NULL
                    AND learners.deleted_at IS NULL
                """,
                (token_hash,),
            ).fetchone()
        if row is None:
            return None
        if datetime.fromisoformat(row["expires_at"]) <= datetime.now(tz=UTC):
            self.revoke_session(token_hash)
            return None
        return dict(row)

    def revoke_session(self, token_hash: str) -> None:
        """Mark one session as revoked."""
        with self._transaction() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET revoked_at = ?
                WHERE token_hash = ?
                """,
                (utc_now_iso(), token_hash),
            )

    def save_question_progress(
        self,
        learner_id: str,
        progress: QuestionProgress,
    ) -> None:
        """Persist the latest progress for one learner question."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO question_progress (
                    learner_id,
                    question_id,
                    answered_count,
                    wrong_count,
                    correct_streak,
                    mastered,
                    last_selected_option_index,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, question_id) DO UPDATE SET
                    answered_count = excluded.answered_count,
                    wrong_count = excluded.wrong_count,
                    correct_streak = excluded.correct_streak,
                    mastered = excluded.mastered,
                    last_selected_option_index = excluded.last_selected_option_index,
                    updated_at = excluded.updated_at
                """,
                (
                    learner_id,
                    progress.question_id,
                    progress.answered_count,
                    progress.wrong_count,
                    progress.correct_streak,
                    int(progress.mastered),
                    progress.last_selected_option_index,
                    utc_now_iso(),
                ),
            )

    def get_question_progress(
        self,
        learner_id: str,
        question_id: str,
    ) -> QuestionProgress | None:
        """Return stored progress for one question or None."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM question_progress
                WHERE learner_id = ? AND question_id = ?
                """,
                (learner_id, question_id),
            ).fetchone()
        return self._row_to_progress(row) if row else None

    def list_question_progress(self, learner_id: str) -> dict[str, QuestionProgress]:
        """Return all stored progress entries for one learner."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM question_progress
                WHERE learner_id = ?
                ORDER BY updated_at DESC
                """,
                (learner_id,),
            ).fetchall()
        return {
            row["question_id"]: self._row_to_progress(row)
            for row in rows
        }

    @staticmethod
    def _row_to_progress(row: sqlite3.Row) -> QuestionProgress:
        """Convert a database row into a progress dataclass."""
        return QuestionProgress(
            question_id=row["question_id"],
            answered_count=row["answered_count"],
            wrong_count=row["wrong_count"],
            correct_streak=row["correct_streak"],
            mastered=bool(row["mastered"]),
            last_selected_option_index=row["last_selected_option_index"],
        )

    def reset_progress(self, learner_id: str) -> None:
        """Delete all question progress for one learner."""
        with self._transaction() as connection:
            connection.execute(
                "DELETE FROM question_progress WHERE learner_id = ?",
                (learner_id,),
            )
            connection.execute(
                "DELETE FROM category_progress WHERE learner_id = ?",
                (learner_id,),
            )

    def get_category_id_by_slug(self, category_slug: str) -> int | None:
        """Return the database id for one category slug."""
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT id FROM question_categories WHERE slug = ?",
                (category_slug,),
            ).fetchone()
        return int(row["id"]) if row else None

    def upsert_category_progress(
        self,
        learner_id: str,
        category_id: int,
        questions_mastered: int,
        questions_total: int,
    ) -> None:
        """Persist aggregate mastery for one learner and category."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO category_progress (
                    learner_id,
                    category_id,
                    questions_mastered,
                    questions_total,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, category_id) DO UPDATE SET
                    questions_mastered = excluded.questions_mastered,
                    questions_total = excluded.questions_total,
                    updated_at = excluded.updated_at
                """,
                (
                    learner_id,
                    category_id,
                    questions_mastered,
                    questions_total,
                    utc_now_iso(),
                ),
            )

    def get_practice_exam_id(self, exam_id: str) -> int | None:
        """Return the database id for one public exam id."""
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT id FROM practice_exams WHERE exam_id = ?",
                (exam_id,),
            ).fetchone()
        return int(row["id"]) if row else None

    def get_quiz_question_pk(self, question_id: str) -> int | None:
        """Return the database id for one public quiz question id."""
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT id FROM quiz_questions WHERE question_id = ?",
                (question_id,),
            ).fetchone()
        return int(row["id"]) if row else None

    def get_open_question_pk(self, question_id: str) -> int | None:
        """Return the database id for one public open question id."""
        with self._transaction() as connection:
            row = connection.execute(
                "SELECT id FROM open_questions WHERE question_id = ?",
                (question_id,),
            ).fetchone()
        return int(row["id"]) if row else None

    def create_exam_session(
        self,
        learner_id: str,
        practice_exam_id: int,
        expires_at: str | None,
    ) -> int:
        """Create one in-progress exam session."""
        with self._transaction() as connection:
            cursor = connection.execute(
                """
                INSERT INTO exam_sessions (
                    learner_id,
                    exam_id,
                    started_at,
                    expires_at,
                    status
                )
                VALUES (?, ?, ?, ?, 'in_progress')
                """,
                (learner_id, practice_exam_id, utc_now_iso(), expires_at),
            )
            return int(cursor.lastrowid)

    def get_exam_session(self, session_id: int) -> dict[str, Any] | None:
        """Return one exam session joined with exam metadata."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT
                    es.id,
                    es.learner_id,
                    es.started_at,
                    es.expires_at,
                    es.submitted_at,
                    es.score_percent,
                    es.passed,
                    es.status,
                    pe.exam_id AS exam_public_id,
                    pe.passing_score_percent,
                    pe.time_limit_minutes
                FROM exam_sessions es
                JOIN practice_exams pe ON pe.id = es.exam_id
                WHERE es.id = ?
                """,
                (session_id,),
            ).fetchone()
        return dict(row) if row else None

    def save_exam_choice_answer(
        self,
        session_id: int,
        quiz_question_id: int,
        selected_option_index: int,
        is_correct: bool,
    ) -> None:
        """Upsert one single-choice answer for an exam session."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO exam_session_answers (
                    session_id,
                    quiz_question_id,
                    selected_option_index,
                    is_correct,
                    answered_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id, quiz_question_id) DO UPDATE SET
                    selected_option_index = excluded.selected_option_index,
                    is_correct = excluded.is_correct,
                    answered_at = excluded.answered_at
                """,
                (
                    session_id,
                    quiz_question_id,
                    selected_option_index,
                    int(is_correct),
                    utc_now_iso(),
                ),
            )

    def save_exam_open_answer(
        self,
        session_id: int,
        open_question_id: int,
        learner_answer: str,
        self_score: int | None,
    ) -> None:
        """Upsert one open answer for an exam session."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO exam_session_open_answers (
                    session_id,
                    open_question_id,
                    learner_answer,
                    self_score,
                    answered_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id, open_question_id) DO UPDATE SET
                    learner_answer = excluded.learner_answer,
                    self_score = excluded.self_score,
                    answered_at = excluded.answered_at
                """,
                (
                    session_id,
                    open_question_id,
                    learner_answer,
                    self_score,
                    utc_now_iso(),
                ),
            )

    def count_exam_choice_answers(self, session_id: int) -> int:
        """Return how many single-choice answers were saved."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM exam_session_answers
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        return int(row["count"])

    def list_exam_choice_answers(self, session_id: int) -> list[dict[str, Any]]:
        """Return stored single-choice answers for one session."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT quiz_question_id, selected_option_index, is_correct
                FROM exam_session_answers
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def list_exam_open_answers(self, session_id: int) -> list[dict[str, Any]]:
        """Return stored open answers for one session."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT open_question_id, learner_answer, self_score
                FROM exam_session_open_answers
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def finalize_exam_session(
        self,
        session_id: int,
        score_percent: float,
        passed: bool,
    ) -> None:
        """Mark one session as submitted with its final score."""
        with self._transaction() as connection:
            connection.execute(
                """
                UPDATE exam_sessions
                SET status = 'submitted',
                    submitted_at = ?,
                    score_percent = ?,
                    passed = ?
                WHERE id = ?
                """,
                (utc_now_iso(), score_percent, int(passed), session_id),
            )

    def mark_exam_session_expired(self, session_id: int) -> None:
        """Mark one in-progress session as expired."""
        with self._transaction() as connection:
            connection.execute(
                """
                UPDATE exam_sessions
                SET status = 'expired'
                WHERE id = ? AND status = 'in_progress'
                """,
                (session_id,),
            )

    def record_consent(
        self,
        learner_id: str,
        consent_version: str,
        accepted: bool,
    ) -> None:
        """Persist a consent or privacy notice acknowledgement event."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO consent_events (
                    learner_id,
                    consent_version,
                    accepted,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (learner_id, consent_version, int(accepted), utc_now_iso()),
            )

    def list_consents(self, learner_id: str) -> list[dict[str, Any]]:
        """Return all consent events for one learner."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT consent_version, accepted, created_at
                FROM consent_events
                WHERE learner_id = ?
                ORDER BY created_at DESC
                """,
                (learner_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def record_audit_event(
        self,
        event_type: str,
        learner_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Persist a minimal audit event without clear text personal data."""
        with self._transaction() as connection:
            connection.execute(
                """
                INSERT INTO audit_events (
                    learner_id,
                    event_type,
                    metadata_json,
                    created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    learner_id,
                    event_type,
                    json.dumps(metadata or {}, sort_keys=True),
                    utc_now_iso(),
                ),
            )

    def export_learner_data(self, learner_id: str) -> dict[str, Any]:
        """Return all learner-owned data for portability/export."""
        with self._transaction() as connection:
            learner = connection.execute(
                """
                SELECT learner_id, display_name, role, cohort_code, created_at
                FROM learners
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (learner_id,),
            ).fetchone()
            if learner is None:
                raise ValueError("Lernkonto wurde nicht gefunden.")
            progress_rows = connection.execute(
                """
                SELECT
                    question_id,
                    answered_count,
                    wrong_count,
                    correct_streak,
                    mastered,
                    last_selected_option_index,
                    updated_at
                FROM question_progress
                WHERE learner_id = ?
                ORDER BY updated_at DESC
                """,
                (learner_id,),
            ).fetchall()
            consent_rows = connection.execute(
                """
                SELECT consent_version, accepted, created_at
                FROM consent_events
                WHERE learner_id = ?
                ORDER BY created_at DESC
                """,
                (learner_id,),
            ).fetchall()
        return {
            "learner": dict(learner),
            "question_progress": [dict(row) for row in progress_rows],
            "consents": [dict(row) for row in consent_rows],
        }

    def delete_learner_data(self, learner_id: str) -> None:
        """Delete learner profile, sessions, progress, consents, and audit links."""
        with self._transaction() as connection:
            connection.execute(
                "DELETE FROM learners WHERE learner_id = ?",
                (learner_id,),
            )
            connection.execute(
                "DELETE FROM audit_events WHERE learner_id = ?",
                (learner_id,),
            )
