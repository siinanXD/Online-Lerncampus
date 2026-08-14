"""Persistence for learner sessions, progress, privacy, and content ops."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from app.db.connection import DbConnection
from app.db.content_schema import initialize_content_schema
from app.db.dialect import DbDialect, normalize_database_url
from app.db.platform_schema import initialize_platform_schema
from app.db.tenant_schema import initialize_tenant_schema
from app.models.progress import QuestionProgress


def utc_now_iso() -> str:
    """Return the current UTC timestamp as ISO string."""
    return datetime.now(tz=UTC).isoformat()


def create_database(database_url: str) -> "Database":
    """Return a database handle for SQLite or PostgreSQL URLs."""
    return Database(database_url)


class Database:
    """Repository for learner data, progress, exams, and content review."""

    def __init__(self, database_url: str) -> None:
        """Open the configured database and initialize its schema."""
        self.database_url = normalize_database_url(database_url)
        self._db = DbConnection(self.database_url)
        self._initialize_schema()

    @property
    def dialect(self) -> DbDialect:
        """Return the active database dialect."""
        return self._db.dialect

    @contextmanager
    def _transaction(self) -> Iterator[DbConnection]:
        """Run database work under a thread lock and transaction."""
        with self._db.transaction() as connection:
            yield connection

    @staticmethod
    def _row_dict(row: Any) -> dict[str, Any]:
        """Normalize sqlite/psycopg rows to plain dictionaries."""
        if row is None:
            raise ValueError("Expected a result row.")
        if isinstance(row, dict):
            return row
        return dict(row)

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

                CREATE TABLE IF NOT EXISTS training_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    learner_id TEXT NOT NULL,
                    report_date TEXT NOT NULL,
                    activities TEXT NOT NULL,
                    hours REAL NOT NULL DEFAULT 8.0,
                    status TEXT NOT NULL DEFAULT 'draft',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (learner_id) REFERENCES learners (learner_id)
                        ON DELETE CASCADE
                );
                """
            )
            self._ensure_password_hash_column(connection)
            self._ensure_requires_password_change_column(connection)
            initialize_content_schema(connection)
            initialize_platform_schema(connection)
            initialize_tenant_schema(connection)

    def _ensure_requires_password_change_column(self, connection: DbConnection) -> None:
        """Add requires_password_change when upgrading an existing local database."""
        if connection.dialect is not DbDialect.SQLITE:
            connection.execute(
                """
                ALTER TABLE learners
                ADD COLUMN IF NOT EXISTS requires_password_change INTEGER NOT NULL DEFAULT 0
                """
            )
            return
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(learners)").fetchall()
        }
        if "requires_password_change" not in columns:
            connection.execute(
                """
                ALTER TABLE learners
                ADD COLUMN requires_password_change INTEGER NOT NULL DEFAULT 0
                """
            )

    def _ensure_password_hash_column(self, connection: DbConnection) -> None:
        """Add password_hash when upgrading an existing local database."""
        if connection.dialect is not DbDialect.SQLITE:
            connection.execute(
                """
                ALTER TABLE learners
                ADD COLUMN IF NOT EXISTS password_hash TEXT
                """
            )
            return
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
                       cohort_code, tenant_id, is_platform_admin,
                       password_hash, requires_password_change, created_at
                FROM learners
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (learner_id,),
            ).fetchone()
        return self._row_dict(row) if row else None

    def get_learner_by_identifier_hash(
        self, identifier_hash: str
    ) -> dict[str, Any] | None:
        """Return one active learner row by pseudonymous login hash."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT learner_id, identifier_hash, display_name, role,
                       cohort_code, tenant_id, is_platform_admin,
                       password_hash, requires_password_change, created_at
                FROM learners
                WHERE identifier_hash = ? AND deleted_at IS NULL
                """,
                (identifier_hash,),
            ).fetchone()
        return self._row_dict(row) if row else None

    def upsert_learner(
        self,
        learner_id: str,
        identifier_hash: str,
        display_name: str,
        role: str,
        cohort_code: str | None,
        tenant_id: str | None = None,
        is_platform_admin: bool = False,
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
                    tenant_id,
                    is_platform_admin,
                    password_hash,
                    created_at,
                    deleted_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
                ON CONFLICT(learner_id) DO UPDATE SET
                    cohort_code = COALESCE(excluded.cohort_code, learners.cohort_code),
                    tenant_id = CASE
                        WHEN excluded.is_platform_admin = 1 THEN NULL
                        ELSE COALESCE(excluded.tenant_id, learners.tenant_id)
                    END,
                    is_platform_admin = excluded.is_platform_admin,
                    role = excluded.role,
                    display_name = excluded.display_name,
                    password_hash = COALESCE(excluded.password_hash, learners.password_hash),
                    deleted_at = NULL
                """,
                (
                    learner_id,
                    identifier_hash,
                    display_name,
                    role,
                    cohort_code,
                    None if is_platform_admin else tenant_id,
                    int(is_platform_admin),
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
                SET password_hash = ?, requires_password_change = 0
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (password_hash, learner_id),
            )

    def set_requires_password_change(self, learner_id: str, required: bool) -> None:
        """Flag whether the learner must change their password on next login."""
        with self._transaction() as connection:
            connection.execute(
                """
                UPDATE learners
                SET requires_password_change = ?
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (int(required), learner_id),
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
                    learners.cohort_code,
                    learners.tenant_id,
                    learners.is_platform_admin
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
        return self._row_dict(row)

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
    def _row_to_progress(row: Any) -> QuestionProgress:
        """Convert a database row into a progress dataclass."""
        payload = Database._row_dict(row)
        return QuestionProgress(
            question_id=payload["question_id"],
            answered_count=payload["answered_count"],
            wrong_count=payload["wrong_count"],
            correct_streak=payload["correct_streak"],
            mastered=bool(payload["mastered"]),
            last_selected_option_index=payload["last_selected_option_index"],
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
            connection.execute(
                "DELETE FROM unit_progress WHERE learner_id = ?",
                (learner_id,),
            )
            connection.execute(
                "DELETE FROM formula_progress WHERE learner_id = ?",
                (learner_id,),
            )
            connection.execute(
                "DELETE FROM diagnosis_progress WHERE learner_id = ?",
                (learner_id,),
            )
            connection.execute(
                "DELETE FROM video_progress WHERE learner_id = ?",
                (learner_id,),
            )
            connection.execute(
                "DELETE FROM daily_goal_progress WHERE learner_id = ?",
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
            return connection.insert_returning_id(
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
        return self._row_dict(row) if row else None

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
        return [self._row_dict(row) for row in rows]

    def list_exam_choice_answers_with_ids(self, session_id: int) -> list[dict[str, Any]]:
        """Return choice answers with public question ids for one session."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT
                    quiz_questions.question_id,
                    exam_session_answers.selected_option_index,
                    exam_session_answers.is_correct
                FROM exam_session_answers
                JOIN quiz_questions
                    ON quiz_questions.id = exam_session_answers.quiz_question_id
                WHERE exam_session_answers.session_id = ?
                """,
                (session_id,),
            ).fetchall()
        return [self._row_dict(row) for row in rows]

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
        return [self._row_dict(row) for row in rows]

    def list_exam_marked_question_ids(self, session_id: int) -> list[str]:
        """Return public question ids marked for review in one session."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT quiz_questions.question_id
                FROM exam_session_marks
                JOIN quiz_questions
                    ON quiz_questions.id = exam_session_marks.quiz_question_id
                WHERE exam_session_marks.session_id = ?
                """,
                (session_id,),
            ).fetchall()
        return [str(row["question_id"]) for row in rows]

    def toggle_exam_mark(self, session_id: int, quiz_question_id: int) -> bool:
        """Toggle a review mark for one exam question. Returns the new marked state."""
        with self._transaction() as connection:
            existing = connection.execute(
                """
                SELECT 1
                FROM exam_session_marks
                WHERE session_id = ? AND quiz_question_id = ?
                """,
                (session_id, quiz_question_id),
            ).fetchone()
            if existing:
                connection.execute(
                    """
                    DELETE FROM exam_session_marks
                    WHERE session_id = ? AND quiz_question_id = ?
                    """,
                    (session_id, quiz_question_id),
                )
                return False
            connection.execute(
                """
                INSERT INTO exam_session_marks (
                    session_id, quiz_question_id, marked_at
                )
                VALUES (?, ?, ?)
                """,
                (session_id, quiz_question_id, utc_now_iso()),
            )
            return True

    def count_exam_marks(self, session_id: int) -> int:
        """Return how many questions are marked in one session."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM exam_session_marks
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
        return int(row["count"])

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
        return [self._row_dict(row) for row in rows]

    def has_privacy_consent(self, learner_id: str) -> bool:
        """Return True when the learner accepted the privacy notice."""
        return any(row["accepted"] for row in self.list_consents(learner_id))

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

    def list_activity_dates(
        self,
        learner_id: str,
        event_types: tuple[str, ...] | None = None,
    ) -> list[str]:
        """Return distinct UTC activity dates (YYYY-MM-DD) for streak calculation."""
        types = event_types or ("progress.attempt", "exam.start", "exam.submit")
        placeholders = ", ".join("?" for _ in types)
        with self._transaction() as connection:
            rows = connection.execute(
                f"""
                SELECT DISTINCT substr(created_at, 1, 10) AS activity_day
                FROM audit_events
                WHERE learner_id = ?
                    AND event_type IN ({placeholders})
                ORDER BY activity_day DESC
                """,
                (learner_id, *types),
            ).fetchall()
        return [str(row["activity_day"]) for row in rows]

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
            unit_rows = connection.execute(
                """
                SELECT learning_units.slug, unit_progress.completed_at
                FROM unit_progress
                JOIN learning_units
                    ON learning_units.id = unit_progress.learning_unit_id
                WHERE unit_progress.learner_id = ?
                """,
                (learner_id,),
            ).fetchall()
            report_rows = connection.execute(
                """
                SELECT report_date, activities, hours, status, created_at
                FROM training_reports
                WHERE learner_id = ?
                ORDER BY report_date DESC
                """,
                (learner_id,),
            ).fetchall()
        return {
            "learner": self._row_dict(learner),
            "question_progress": [self._row_dict(row) for row in progress_rows],
            "consents": [self._row_dict(row) for row in consent_rows],
            "completed_units": [self._row_dict(row) for row in unit_rows],
            "training_reports": [self._row_dict(row) for row in report_rows],
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

    def list_training_reports(self, learner_id: str) -> list[dict[str, Any]]:
        """Return all Berichtsheft entries for one learner."""
        with self._transaction() as connection:
            rows = connection.execute(
                """
                SELECT id, report_date, activities, hours, status,
                       signed_at, trainer_status, created_at, updated_at
                FROM training_reports
                WHERE learner_id = ?
                ORDER BY report_date DESC, id DESC
                """,
                (learner_id,),
            ).fetchall()
        return [self._row_dict(row) for row in rows]

    def create_training_report(
        self,
        learner_id: str,
        report_date: str,
        activities: str,
        hours: float,
    ) -> dict[str, Any]:
        """Create one draft Berichtsheft entry."""
        timestamp = utc_now_iso()
        with self._transaction() as connection:
            report_id = connection.insert_returning_id(
                """
                INSERT INTO training_reports (
                    learner_id,
                    report_date,
                    activities,
                    hours,
                    status,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, 'draft', ?, ?)
                """,
                (learner_id, report_date, activities, hours, timestamp, timestamp),
            )
            row = connection.execute(
                """
                SELECT id, report_date, activities, hours, status,
                       signed_at, trainer_status, created_at, updated_at
                FROM training_reports
                WHERE id = ?
                """,
                (report_id,),
            ).fetchone()
        return self._row_dict(row)

    def update_training_report(
        self,
        learner_id: str,
        report_id: int,
        *,
        report_date: str | None = None,
        activities: str | None = None,
        hours: float | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        """Update one Berichtsheft entry owned by the learner."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM training_reports
                WHERE id = ? AND learner_id = ?
                """,
                (report_id, learner_id),
            ).fetchone()
            if row is None:
                return None
            fields: list[str] = []
            params: list[Any] = []
            if report_date is not None:
                fields.append("report_date = ?")
                params.append(report_date)
            if activities is not None:
                fields.append("activities = ?")
                params.append(activities)
            if hours is not None:
                fields.append("hours = ?")
                params.append(hours)
            if status is not None:
                fields.append("status = ?")
                params.append(status)
            if not fields:
                return self.get_training_report(learner_id, report_id)
            fields.append("updated_at = ?")
            params.append(utc_now_iso())
            params.extend([report_id, learner_id])
            connection.execute(
                f"""
                UPDATE training_reports
                SET {", ".join(fields)}
                WHERE id = ? AND learner_id = ?
                """,
                tuple(params),
            )
        return self.get_training_report(learner_id, report_id)

    def get_training_report(
        self,
        learner_id: str,
        report_id: int,
    ) -> dict[str, Any] | None:
        """Return one Berichtsheft entry."""
        with self._transaction() as connection:
            row = connection.execute(
                """
                SELECT id, report_date, activities, hours, status,
                       signed_at, trainer_status, created_at, updated_at
                FROM training_reports
                WHERE id = ? AND learner_id = ?
                """,
                (report_id, learner_id),
            ).fetchone()
        return self._row_dict(row) if row else None

    def list_pending_reviews(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return draft learning units and questions awaiting review."""
        with self._transaction() as connection:
            unit_rows = connection.execute(
                """
                SELECT 'learning_unit' AS entity_type, id AS entity_id, slug AS entity_key,
                       title, review_status
                FROM learning_units
                WHERE review_status IN ('draft', 'needs_revision')
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            question_rows = connection.execute(
                """
                SELECT 'quiz_question' AS entity_type, id AS entity_id, question_id AS entity_key,
                       prompt AS title, review_status
                FROM quiz_questions
                WHERE review_status IN ('draft', 'needs_revision')
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [self._row_dict(row) for row in [*unit_rows, *question_rows]]

    def apply_content_review(
        self,
        entity_type: str,
        entity_key: str,
        to_status: str,
        reviewer_learner_id: str,
        notes: str,
    ) -> dict[str, Any]:
        """Update review status and append an audit row in content_reviews."""
        table_map = {
            "learning_unit": ("learning_units", "slug"),
            "quiz_question": ("quiz_questions", "question_id"),
            "open_question": ("open_questions", "question_id"),
        }
        if entity_type not in table_map:
            raise ValueError("Unbekannter Inhaltstyp.")
        table, key_column = table_map[entity_type]
        with self._transaction() as connection:
            row = connection.execute(
                f"""
                SELECT id, review_status
                FROM {table}
                WHERE {key_column} = ?
                """,
                (entity_key,),
            ).fetchone()
            if row is None:
                raise ValueError("Inhalt wurde nicht gefunden.")
            payload = self._row_dict(row)
            from_status = payload["review_status"]
            connection.execute(
                f"""
                UPDATE {table}
                SET review_status = ?, updated_at = ?
                WHERE id = ?
                """,
                (to_status, utc_now_iso(), payload["id"]),
            )
            connection.execute(
                """
                INSERT INTO content_reviews (
                    entity_type,
                    entity_id,
                    from_status,
                    to_status,
                    reviewer_learner_id,
                    notes,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity_type,
                    payload["id"],
                    from_status,
                    to_status,
                    reviewer_learner_id,
                    notes,
                    utc_now_iso(),
                ),
            )
        return {
            "entity_type": entity_type,
            "entity_key": entity_key,
            "from_status": from_status,
            "to_status": to_status,
        }

    def approve_all_content(self) -> dict[str, int]:
        """Mark all seeded content as approved for demo environments."""
        counts: dict[str, int] = {}
        with self._transaction() as connection:
            for table in ("learning_units", "quiz_questions", "open_questions"):
                cursor = connection.execute(
                    f"""
                    UPDATE {table}
                    SET review_status = 'approved', updated_at = ?
                    WHERE review_status != 'approved'
                    """,
                    (utc_now_iso(),),
                )
                counts[table] = cursor.rowcount if cursor.rowcount is not None else 0
        return counts
