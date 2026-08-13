"""Persistence for preferences, learning tools, and staff extras."""

from __future__ import annotations

import json
from typing import Any

from app.db.dialect import insert_ignore_sql
from app.services.database import Database, utc_now_iso

_DEFAULT_NOTIFICATION_SETTINGS = {
    "daily_reminder": 1,
    "streak_risk": 1,
    "daily_goal_missed": 1,
    "level_up": 1,
    "new_badges": 1,
    "exam_ready": 1,
    "missing_reports": 1,
    "report_approved": 1,
    "new_content": 0,
    "maintenance": 1,
}


class PlatformRepository:
    """SQL access for platform tables on top of the shared Database."""

    def __init__(self, database: Database) -> None:
        """Attach to the application database."""
        self.database = database

    def is_empty(self) -> bool:
        """Return True when formula seed content is missing."""
        with self.database._transaction() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM formulas"
            ).fetchone()
        return int(row["count"]) == 0

    def counts(self) -> dict[str, int]:
        """Return row counts for seeded platform tables."""
        result: dict[str, int] = {}
        with self.database._transaction() as connection:
            for table in (
                "formulas",
                "diagnosis_cases",
                "video_lessons",
                "translations",
                "media_assets",
            ):
                row = connection.execute(
                    f"SELECT COUNT(*) AS count FROM {table}"
                ).fetchone()
                result[table] = int(row["count"])
        return result

    def get_learning_unit_id(self, slug: str) -> int | None:
        """Return the primary key for one learning unit slug."""
        with self.database._transaction() as connection:
            row = connection.execute(
                "SELECT id FROM learning_units WHERE slug = ?",
                (slug,),
            ).fetchone()
        return int(row["id"]) if row else None

    def complete_unit(self, learner_id: str, slug: str) -> dict[str, Any]:
        """Mark one learning unit as completed for the learner."""
        unit_id = self.get_learning_unit_id(slug)
        if unit_id is None:
            raise ValueError("Lerneinheit nicht gefunden.")
        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            connection.execute(
                """
                INSERT INTO unit_progress (learner_id, learning_unit_id, completed_at)
                VALUES (?, ?, ?)
                ON CONFLICT(learner_id, learning_unit_id) DO UPDATE SET
                    completed_at = excluded.completed_at
                """,
                (learner_id, unit_id, timestamp),
            )
        return {"slug": slug, "completed_at": timestamp, "completed": True}

    def list_completed_unit_slugs(self, learner_id: str) -> list[str]:
        """Return slugs of completed learning units."""
        with self.database._transaction() as connection:
            rows = connection.execute(
                """
                SELECT learning_units.slug
                FROM unit_progress
                JOIN learning_units
                    ON learning_units.id = unit_progress.learning_unit_id
                WHERE unit_progress.learner_id = ?
                ORDER BY unit_progress.completed_at
                """,
                (learner_id,),
            ).fetchall()
        return [str(row["slug"]) for row in rows]

    def count_completed_units(self, learner_id: str) -> int:
        """Return how many units the learner completed."""
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM unit_progress
                WHERE learner_id = ?
                """,
                (learner_id,),
            ).fetchone()
        return int(row["count"])

    def ensure_learner_defaults(self, learner_id: str) -> None:
        """Create preference rows and a welcome notification when missing."""
        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            connection.execute(
                insert_ignore_sql(
                    "learner_preferences",
                    "learner_id, language, theme, high_contrast, reduce_motion, "
                    "daily_goal_lessons, updated_at",
                    "?, ?, ?, ?, ?, ?, ?",
                    "learner_id",
                    connection.dialect,
                ),
                (learner_id, "de", "dark", 0, 0, 5, timestamp),
            )
            connection.execute(
                insert_ignore_sql(
                    "notification_settings",
                    "learner_id, daily_reminder, streak_risk, daily_goal_missed, "
                    "level_up, new_badges, exam_ready, missing_reports, "
                    "report_approved, new_content, maintenance, updated_at",
                    "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?",
                    "learner_id",
                    connection.dialect,
                ),
                (
                    learner_id,
                    1, 1, 1, 1, 1, 1, 1, 1, 0, 1,
                    timestamp,
                ),
            )
            existing = connection.execute(
                "SELECT COUNT(*) AS count FROM notifications WHERE learner_id = ?",
                (learner_id,),
            ).fetchone()
            if int(existing["count"]) == 0:
                connection.execute(
                    """
                    INSERT INTO notifications (
                        learner_id, kind, title, body, href, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        learner_id,
                        "welcome",
                        "Willkommen im Lerncampus",
                        "Dein Lernstand wird serverseitig gespeichert. Starte mit Monat 1.",
                        "/dashboard",
                        timestamp,
                    ),
                )

    def get_preferences(self, learner_id: str) -> dict[str, Any]:
        """Return stored UI preferences for one learner."""
        self.ensure_learner_defaults(learner_id)
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT language, theme, high_contrast, reduce_motion, daily_goal_lessons,
                       onboarding_completed
                FROM learner_preferences
                WHERE learner_id = ?
                """,
                (learner_id,),
            ).fetchone()
        payload = Database._row_dict(row)
        payload["high_contrast"] = bool(payload["high_contrast"])
        payload["reduce_motion"] = bool(payload["reduce_motion"])
        payload["onboarding_completed"] = bool(payload.get("onboarding_completed"))
        return payload

    def update_preferences(
        self,
        learner_id: str,
        *,
        language: str | None = None,
        theme: str | None = None,
        high_contrast: bool | None = None,
        reduce_motion: bool | None = None,
        daily_goal_lessons: int | None = None,
    ) -> dict[str, Any]:
        """Patch learner UI preferences."""
        current = self.get_preferences(learner_id)
        next_values = {
            "language": language or current["language"],
            "theme": theme or current["theme"],
            "high_contrast": int(
                current["high_contrast"] if high_contrast is None else high_contrast
            ),
            "reduce_motion": int(
                current["reduce_motion"] if reduce_motion is None else reduce_motion
            ),
            "daily_goal_lessons": (
                current["daily_goal_lessons"]
                if daily_goal_lessons is None
                else daily_goal_lessons
            ),
        }
        with self.database._transaction() as connection:
            connection.execute(
                """
                UPDATE learner_preferences
                SET language = ?, theme = ?, high_contrast = ?, reduce_motion = ?,
                    daily_goal_lessons = ?, updated_at = ?
                WHERE learner_id = ?
                """,
                (
                    next_values["language"],
                    next_values["theme"],
                    next_values["high_contrast"],
                    next_values["reduce_motion"],
                    next_values["daily_goal_lessons"],
                    utc_now_iso(),
                    learner_id,
                ),
            )
        return self.get_preferences(learner_id)

    def complete_onboarding(self, learner_id: str) -> dict[str, Any]:
        """Mark onboarding as finished for one learner."""
        self.ensure_learner_defaults(learner_id)
        with self.database._transaction() as connection:
            connection.execute(
                """
                UPDATE learner_preferences
                SET onboarding_completed = 1, updated_at = ?
                WHERE learner_id = ?
                """,
                (utc_now_iso(), learner_id),
            )
        return self.get_preferences(learner_id)

    def get_notification_settings(self, learner_id: str) -> dict[str, bool]:
        """Return notification toggles as booleans."""
        self.ensure_learner_defaults(learner_id)
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT daily_reminder, streak_risk, daily_goal_missed, level_up,
                       new_badges, exam_ready, missing_reports, report_approved,
                       new_content, maintenance
                FROM notification_settings
                WHERE learner_id = ?
                """,
                (learner_id,),
            ).fetchone()
        payload = Database._row_dict(row)
        return {key: bool(value) for key, value in payload.items()}

    def update_notification_settings(
        self,
        learner_id: str,
        updates: dict[str, bool],
    ) -> dict[str, bool]:
        """Patch one or more notification toggles."""
        current = self.get_notification_settings(learner_id)
        allowed = set(_DEFAULT_NOTIFICATION_SETTINGS)
        merged = {key: updates[key] if key in updates else current[key] for key in allowed}
        with self.database._transaction() as connection:
            connection.execute(
                """
                UPDATE notification_settings
                SET daily_reminder = ?, streak_risk = ?, daily_goal_missed = ?,
                    level_up = ?, new_badges = ?, exam_ready = ?,
                    missing_reports = ?, report_approved = ?, new_content = ?,
                    maintenance = ?, updated_at = ?
                WHERE learner_id = ?
                """,
                (
                    int(merged["daily_reminder"]),
                    int(merged["streak_risk"]),
                    int(merged["daily_goal_missed"]),
                    int(merged["level_up"]),
                    int(merged["new_badges"]),
                    int(merged["exam_ready"]),
                    int(merged["missing_reports"]),
                    int(merged["report_approved"]),
                    int(merged["new_content"]),
                    int(merged["maintenance"]),
                    utc_now_iso(),
                    learner_id,
                ),
            )
        return self.get_notification_settings(learner_id)

    def list_notifications(self, learner_id: str) -> list[dict[str, Any]]:
        """Return inbox items newest first."""
        self.ensure_learner_defaults(learner_id)
        with self.database._transaction() as connection:
            rows = connection.execute(
                """
                SELECT id, kind, title, body, href, read_at, created_at
                FROM notifications
                WHERE learner_id = ?
                ORDER BY created_at DESC
                LIMIT 50
                """,
                (learner_id,),
            ).fetchall()
        result = []
        for row in rows:
            payload = Database._row_dict(row)
            payload["read"] = payload["read_at"] is not None
            result.append(payload)
        return result

    def mark_notification_read(self, learner_id: str, notification_id: int) -> bool:
        """Mark one inbox item as read."""
        with self.database._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE notifications
                SET read_at = ?
                WHERE id = ? AND learner_id = ? AND read_at IS NULL
                """,
                (utc_now_iso(), notification_id, learner_id),
            )
        return bool(cursor.rowcount)

    def bump_daily_goal(
        self,
        learner_id: str,
        *,
        lessons: int = 0,
        questions: int = 0,
        minutes: int = 0,
        goal_date: str | None = None,
    ) -> dict[str, Any]:
        """Increment today's daily-goal counters."""
        day = goal_date or utc_now_iso()[:10]
        with self.database._transaction() as connection:
            connection.execute(
                """
                INSERT INTO daily_goal_progress (
                    learner_id, goal_date, lessons_completed,
                    questions_answered, minutes_studied
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, goal_date) DO UPDATE SET
                    lessons_completed = daily_goal_progress.lessons_completed
                        + excluded.lessons_completed,
                    questions_answered = daily_goal_progress.questions_answered
                        + excluded.questions_answered,
                    minutes_studied = daily_goal_progress.minutes_studied
                        + excluded.minutes_studied
                """,
                (learner_id, day, lessons, questions, minutes),
            )
        return self.get_daily_goal(learner_id, day)

    def list_week_minutes(
        self,
        learner_id: str,
        goal_date: str | None = None,
    ) -> list[int]:
        """Return minutes studied for Monday through Sunday of the current week."""
        from datetime import date, timedelta

        day = goal_date or utc_now_iso()[:10]
        monday = date.fromisoformat(_week_start(day))
        week_days = [(monday + timedelta(days=offset)).isoformat() for offset in range(7)]
        placeholders = ", ".join("?" for _ in week_days)
        with self.database._transaction() as connection:
            rows = connection.execute(
                f"""
                SELECT goal_date, minutes_studied
                FROM daily_goal_progress
                WHERE learner_id = ? AND goal_date IN ({placeholders})
                """,
                (learner_id, *week_days),
            ).fetchall()
        by_day = {
            str(row["goal_date"]): int(row["minutes_studied"])
            for row in rows
        }
        return [by_day.get(day_key, 0) for day_key in week_days]

    def get_daily_goal(
        self,
        learner_id: str,
        goal_date: str | None = None,
    ) -> dict[str, Any]:
        """Return counters and target for one day."""
        self.ensure_learner_defaults(learner_id)
        day = goal_date or utc_now_iso()[:10]
        prefs = self.get_preferences(learner_id)
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT lessons_completed, questions_answered, minutes_studied
                FROM daily_goal_progress
                WHERE learner_id = ? AND goal_date = ?
                """,
                (learner_id, day),
            ).fetchone()
            week_row = connection.execute(
                """
                SELECT COALESCE(SUM(minutes_studied), 0) AS minutes
                FROM daily_goal_progress
                WHERE learner_id = ? AND goal_date >= ?
                """,
                (learner_id, _week_start(day)),
            ).fetchone()
        progress = (
            Database._row_dict(row)
            if row
            else {
                "lessons_completed": 0,
                "questions_answered": 0,
                "minutes_studied": 0,
            }
        )
        target = int(prefs["daily_goal_lessons"])
        done = int(progress["lessons_completed"])
        return {
            "goal_date": day,
            "lessons_completed": done,
            "lessons_goal": target,
            "lessons_remaining": max(target - done, 0),
            "questions_answered": int(progress["questions_answered"]),
            "minutes_studied": int(progress["minutes_studied"]),
            "minutes_studied_week": int(week_row["minutes"]),
            "completed": done >= target,
        }

    def list_formulas(self, topic: str | None = None) -> list[dict[str, Any]]:
        """Return Formeltrainer entries, optionally filtered by topic."""
        with self.database._transaction() as connection:
            if topic and topic != "alle":
                rows = connection.execute(
                    """
                    SELECT id, slug, topic, title, expression, legend_json, example,
                           difficulty, source_keys_json
                    FROM formulas
                    WHERE topic = ?
                    ORDER BY id
                    """,
                    (topic,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT id, slug, topic, title, expression, legend_json, example,
                           difficulty, source_keys_json
                    FROM formulas
                    ORDER BY id
                    """
                ).fetchall()
        return [self._formula_row(row) for row in rows]

    def get_formula(self, slug: str) -> dict[str, Any] | None:
        """Return one formula by slug."""
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT id, slug, topic, title, expression, legend_json, example,
                       difficulty, source_keys_json
                FROM formulas
                WHERE slug = ?
                """,
                (slug,),
            ).fetchone()
        return self._formula_row(row) if row else None

    def record_formula_practice(
        self,
        learner_id: str,
        slug: str,
        correct: bool,
    ) -> dict[str, Any]:
        """Store one Formeltrainer practice attempt."""
        formula = self.get_formula(slug)
        if formula is None:
            raise ValueError("Formel nicht gefunden.")
        with self.database._transaction() as connection:
            connection.execute(
                """
                INSERT INTO formula_progress (
                    learner_id, formula_id, practiced_count, last_correct, updated_at
                )
                VALUES (?, ?, 1, ?, ?)
                ON CONFLICT(learner_id, formula_id) DO UPDATE SET
                    practiced_count = formula_progress.practiced_count + 1,
                    last_correct = excluded.last_correct,
                    updated_at = excluded.updated_at
                """,
                (learner_id, formula["id"], int(correct), utc_now_iso()),
            )
        self.bump_daily_goal(learner_id, questions=1, minutes=1)
        return {"slug": slug, "correct": correct, "saved": True}

    def list_diagnosis_cases(self, learner_id: str | None = None) -> list[dict[str, Any]]:
        """Return Fehlerdiagnose cases with optional solve state."""
        with self.database._transaction() as connection:
            rows = connection.execute(
                """
                SELECT id, slug, topic, title, symptom, options_json,
                       correct_option_index, explanation, difficulty, estimated_minutes
                FROM diagnosis_cases
                ORDER BY id
                """
            ).fetchall()
            solved: set[int] = set()
            if learner_id:
                progress_rows = connection.execute(
                    """
                    SELECT case_id FROM diagnosis_progress
                    WHERE learner_id = ? AND solved = 1
                    """,
                    (learner_id,),
                ).fetchall()
                solved = {int(row["case_id"]) for row in progress_rows}
        result = []
        for row in rows:
            payload = Database._row_dict(row)
            payload["options"] = json.loads(payload.pop("options_json"))
            payload["solved"] = payload["id"] in solved
            result.append(payload)
        return result

    def solve_diagnosis_case(
        self,
        learner_id: str,
        slug: str,
        selected_option_index: int,
    ) -> dict[str, Any]:
        """Score one diagnosis case and persist the attempt."""
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT id, options_json, correct_option_index, explanation, title
                FROM diagnosis_cases
                WHERE slug = ?
                """,
                (slug,),
            ).fetchone()
            if row is None:
                raise ValueError("Diagnosefall nicht gefunden.")
            payload = Database._row_dict(row)
            options = json.loads(payload["options_json"])
            if selected_option_index < 0 or selected_option_index >= len(options):
                raise ValueError("Antwortindex ist ungueltig.")
            correct = selected_option_index == int(payload["correct_option_index"])
            timestamp = utc_now_iso() if correct else None
            connection.execute(
                """
                INSERT INTO diagnosis_progress (
                    learner_id, case_id, solved, selected_option_index, solved_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, case_id) DO UPDATE SET
                    solved = excluded.solved,
                    selected_option_index = excluded.selected_option_index,
                    solved_at = excluded.solved_at
                """,
                (
                    learner_id,
                    payload["id"],
                    int(correct),
                    selected_option_index,
                    timestamp,
                ),
            )
        if correct:
            self.bump_daily_goal(learner_id, lessons=1, minutes=5)
        return {
            "slug": slug,
            "is_correct": correct,
            "correct_option_index": int(payload["correct_option_index"]),
            "explanation": payload["explanation"],
        }

    def list_videos(self, learner_id: str | None = None) -> list[dict[str, Any]]:
        """Return video lessons with optional watch progress."""
        with self.database._transaction() as connection:
            rows = connection.execute(
                """
                SELECT id, slug, title, description, instructor, duration_seconds,
                       topic, thumbnail_url, video_url, chapters_json, next_slug
                FROM video_lessons
                ORDER BY id
                """
            ).fetchall()
            progress_map: dict[int, dict[str, Any]] = {}
            if learner_id:
                progress_rows = connection.execute(
                    """
                    SELECT video_id, watched_seconds, completed
                    FROM video_progress
                    WHERE learner_id = ?
                    """,
                    (learner_id,),
                ).fetchall()
                progress_map = {
                    int(row["video_id"]): Database._row_dict(row)
                    for row in progress_rows
                }
        result = []
        for row in rows:
            payload = Database._row_dict(row)
            payload["chapters"] = json.loads(payload.pop("chapters_json"))
            progress = progress_map.get(int(payload["id"]), {})
            payload["watched_seconds"] = int(progress.get("watched_seconds") or 0)
            payload["completed"] = bool(progress.get("completed"))
            result.append(payload)
        return result

    def record_video_progress(
        self,
        learner_id: str,
        slug: str,
        watched_seconds: int,
        completed: bool = False,
    ) -> dict[str, Any]:
        """Store watch progress for one video lesson."""
        with self.database._transaction() as connection:
            row = connection.execute(
                "SELECT id, duration_seconds FROM video_lessons WHERE slug = ?",
                (slug,),
            ).fetchone()
            if row is None:
                raise ValueError("Videolektion nicht gefunden.")
            video_id = int(row["id"])
            duration = int(row["duration_seconds"] or 0)
            watched = max(0, watched_seconds)
            if duration and watched >= duration:
                completed = True
            connection.execute(
                """
                INSERT INTO video_progress (
                    learner_id, video_id, watched_seconds, completed, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(learner_id, video_id) DO UPDATE SET
                    watched_seconds = excluded.watched_seconds,
                    completed = excluded.completed,
                    updated_at = excluded.updated_at
                """,
                (learner_id, video_id, watched, int(completed), utc_now_iso()),
            )
        if completed:
            self.bump_daily_goal(learner_id, lessons=1, minutes=max(watched // 60, 1))
        return {"slug": slug, "watched_seconds": watched, "completed": completed}

    def search_translations(
        self,
        query: str | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search glossary translations."""
        needle = f"%{(query or '').strip()}%"
        with self.database._transaction() as connection:
            if query and language:
                rows = connection.execute(
                    """
                    SELECT term, language, translation, definition
                    FROM translations
                    WHERE language = ?
                        AND (term LIKE ? OR translation LIKE ? OR definition LIKE ?)
                    ORDER BY term
                    """,
                    (language, needle, needle, needle),
                ).fetchall()
            elif query:
                rows = connection.execute(
                    """
                    SELECT term, language, translation, definition
                    FROM translations
                    WHERE term LIKE ? OR translation LIKE ? OR definition LIKE ?
                    ORDER BY term, language
                    """,
                    (needle, needle, needle),
                ).fetchall()
            elif language:
                rows = connection.execute(
                    """
                    SELECT term, language, translation, definition
                    FROM translations
                    WHERE language = ?
                    ORDER BY term
                    """,
                    (language,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT term, language, translation, definition
                    FROM translations
                    ORDER BY term, language
                    """
                ).fetchall()
        return [Database._row_dict(row) for row in rows]

    def create_content_flag(
        self,
        learner_id: str,
        entity_type: str,
        entity_key: str,
        reason: str,
        notes: str = "",
    ) -> dict[str, Any]:
        """Store a learner content report."""
        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            flag_id = connection.insert_returning_id(
                """
                INSERT INTO content_flags (
                    learner_id, entity_type, entity_key, reason, notes, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (learner_id, entity_type, entity_key, reason, notes, timestamp),
            )
        return {
            "id": flag_id,
            "entity_type": entity_type,
            "entity_key": entity_key,
            "reason": reason,
            "created_at": timestamp,
        }

    def list_media(self) -> list[dict[str, Any]]:
        """Return uploaded or seeded media metadata."""
        with self.database._transaction() as connection:
            rows = connection.execute(
                """
                SELECT id, slug, title, media_type, url, uploaded_by, created_at
                FROM media_assets
                ORDER BY id DESC
                """
            ).fetchall()
        return [Database._row_dict(row) for row in rows]

    def create_media(
        self,
        *,
        slug: str,
        title: str,
        media_type: str,
        url: str,
        uploaded_by: str,
    ) -> dict[str, Any]:
        """Insert one media metadata row."""
        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            media_id = connection.insert_returning_id(
                """
                INSERT INTO media_assets (
                    slug, title, media_type, url, uploaded_by, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (slug, title, media_type, url, uploaded_by, timestamp),
            )
            row = connection.execute(
                """
                SELECT id, slug, title, media_type, url, uploaded_by, created_at
                FROM media_assets
                WHERE id = ?
                """,
                (media_id,),
            ).fetchone()
        return Database._row_dict(row)

    def list_cohort_learners(self, cohort_code: str | None) -> list[dict[str, Any]]:
        """Return active learners in one cohort (no identifier hashes)."""
        return self.list_scoped_learners(cohort_code=cohort_code)

    def list_scoped_learners(
        self,
        *,
        tenant_id: str | None = None,
        cohort_code: str | None = None,
        limit: int = 200,
    ) -> list[dict[str, Any]]:
        """Return active accounts limited to one tenant and/or cohort."""
        clauses = ["deleted_at IS NULL"]
        params: list[Any] = []
        if tenant_id:
            clauses.append("tenant_id = ?")
            params.append(tenant_id)
        if cohort_code:
            clauses.append("cohort_code = ?")
            params.append(cohort_code)
        where = " AND ".join(clauses)
        with self.database._transaction() as connection:
            rows = connection.execute(
                f"""
                SELECT learner_id, display_name, role, cohort_code, tenant_id, created_at
                FROM learners
                WHERE {where}
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()
        return [Database._row_dict(row) for row in rows]

    def list_audit_events(
        self,
        limit: int = 50,
        *,
        tenant_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent audit events for admin views."""
        with self.database._transaction() as connection:
            if tenant_id:
                rows = connection.execute(
                    """
                    SELECT audit_events.id, audit_events.learner_id,
                           audit_events.event_type, audit_events.metadata_json,
                           audit_events.created_at
                    FROM audit_events
                    LEFT JOIN learners
                        ON learners.learner_id = audit_events.learner_id
                    WHERE learners.tenant_id = ?
                    ORDER BY audit_events.id DESC
                    LIMIT ?
                    """,
                    (tenant_id, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT id, learner_id, event_type, metadata_json, created_at
                    FROM audit_events
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        result = []
        for row in rows:
            payload = Database._row_dict(row)
            payload["metadata"] = json.loads(payload.pop("metadata_json") or "{}")
            result.append(payload)
        return result

    def monitoring_snapshot(self, tenant_id: str | None = None) -> dict[str, Any]:
        """Return high-level counts for the admin monitoring screen."""
        with self.database._transaction() as connection:
            def count(sql: str, params: tuple[Any, ...] = ()) -> int:
                return int(connection.execute(sql, params).fetchone()["count"])

            if tenant_id:
                learners = count(
                    """
                    SELECT COUNT(*) AS count FROM learners
                    WHERE deleted_at IS NULL AND tenant_id = ?
                    """,
                    (tenant_id,),
                )
                sessions = count(
                    """
                    SELECT COUNT(*) AS count FROM exam_sessions
                    JOIN learners ON learners.learner_id = exam_sessions.learner_id
                    WHERE learners.tenant_id = ?
                    """,
                    (tenant_id,),
                )
                reports = count(
                    """
                    SELECT COUNT(*) AS count FROM training_reports
                    JOIN learners ON learners.learner_id = training_reports.learner_id
                    WHERE learners.tenant_id = ?
                    """,
                    (tenant_id,),
                )
                flags = count(
                    """
                    SELECT COUNT(*) AS count FROM content_flags
                    JOIN learners ON learners.learner_id = content_flags.learner_id
                    WHERE learners.tenant_id = ?
                    """,
                    (tenant_id,),
                )
            else:
                learners = count(
                    "SELECT COUNT(*) AS count FROM learners WHERE deleted_at IS NULL"
                )
                sessions = count("SELECT COUNT(*) AS count FROM exam_sessions")
                reports = count("SELECT COUNT(*) AS count FROM training_reports")
                flags = count("SELECT COUNT(*) AS count FROM content_flags")
            questions = count("SELECT COUNT(*) AS count FROM quiz_questions")
            units = count("SELECT COUNT(*) AS count FROM learning_units")
            pending = count(
                """
                SELECT COUNT(*) AS count FROM learning_units
                WHERE review_status IN ('draft', 'needs_revision')
                """
            )
        return {
            "learners": learners,
            "quiz_questions": questions,
            "learning_units": units,
            "pending_reviews": pending,
            "exam_sessions": sessions,
            "training_reports": reports,
            "content_flags": flags,
        }

    def list_duplicate_prompts(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return quiz prompts that appear more than once."""
        with self.database._transaction() as connection:
            rows = connection.execute(
                "SELECT question_id, prompt FROM quiz_questions"
            ).fetchall()
        grouped: dict[str, list[str]] = {}
        for row in rows:
            payload = Database._row_dict(row)
            grouped.setdefault(str(payload["prompt"]), []).append(
                str(payload["question_id"])
            )
        duplicates = [
            {
                "prompt": prompt,
                "copies": len(ids),
                "question_ids": ids,
            }
            for prompt, ids in grouped.items()
            if len(ids) > 1
        ]
        duplicates.sort(key=lambda item: item["copies"], reverse=True)
        return duplicates[:limit]

    def get_app_settings(self) -> dict[str, Any]:
        """Return all key/value app settings."""
        with self.database._transaction() as connection:
            rows = connection.execute(
                "SELECT key, value_json FROM app_settings"
            ).fetchall()
        return {
            str(row["key"]): json.loads(row["value_json"])
            for row in rows
        }

    def update_app_setting(self, key: str, value: Any) -> dict[str, Any]:
        """Upsert one app setting."""
        with self.database._transaction() as connection:
            connection.execute(
                """
                INSERT INTO app_settings (key, value_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json = excluded.value_json,
                    updated_at = excluded.updated_at
                """,
                (key, json.dumps(value), utc_now_iso()),
            )
        return self.get_app_settings()

    def update_learner_role(
        self,
        learner_id: str,
        role: str,
        *,
        tenant_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Change a learner's role (admin only)."""
        allowed = {"learner", "reviewer", "trainer", "admin"}
        if role not in allowed:
            raise ValueError("Ungueltige Rolle.")
        current = self.database.get_learner(learner_id)
        if current is None:
            return None
        if tenant_id and current.get("tenant_id") != tenant_id:
            return None
        with self.database._transaction() as connection:
            connection.execute(
                """
                UPDATE learners
                SET role = ?
                WHERE learner_id = ? AND deleted_at IS NULL
                """,
                (role, learner_id),
            )
        return self.database.get_learner(learner_id)

    def sign_training_report(
        self,
        learner_id: str,
        report_id: int,
    ) -> dict[str, Any] | None:
        """Mark a Berichtsheft entry as submitted for signature."""
        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            cursor = connection.execute(
                """
                UPDATE training_reports
                SET status = 'submitted',
                    signed_at = ?,
                    trainer_status = COALESCE(trainer_status, 'pending'),
                    updated_at = ?
                WHERE id = ? AND learner_id = ?
                """,
                (timestamp, timestamp, report_id, learner_id),
            )
            if not cursor.rowcount:
                return None
        return self.database.get_training_report(learner_id, report_id)

    def trainer_update_report(
        self,
        report_id: int,
        trainer_status: str,
        *,
        tenant_id: str | None = None,
        cohort_code: str | None = None,
    ) -> dict[str, Any] | None:
        """Approve or reject a Berichtsheft entry."""
        if trainer_status not in {"pending", "approved", "rejected"}:
            raise ValueError("Ungueltiger Trainer-Status.")
        timestamp = utc_now_iso()
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT training_reports.id, training_reports.learner_id,
                       learners.tenant_id, learners.cohort_code
                FROM training_reports
                JOIN learners ON learners.learner_id = training_reports.learner_id
                WHERE training_reports.id = ?
                """,
                (report_id,),
            ).fetchone()
            if row is None:
                return None
            payload = Database._row_dict(row)
            if tenant_id and payload.get("tenant_id") != tenant_id:
                return None
            if cohort_code and payload.get("cohort_code") != cohort_code:
                return None
            connection.execute(
                """
                UPDATE training_reports
                SET trainer_status = ?, updated_at = ?
                WHERE id = ?
                """,
                (trainer_status, timestamp, report_id),
            )
        return self.database.get_training_report(payload["learner_id"], report_id)

    def list_all_training_reports(
        self,
        limit: int = 100,
        *,
        tenant_id: str | None = None,
        cohort_code: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return recent Berichtsheft entries across learners for trainers."""
        clauses: list[str] = []
        params: list[Any] = []
        if tenant_id:
            clauses.append("learners.tenant_id = ?")
            params.append(tenant_id)
        if cohort_code:
            clauses.append("learners.cohort_code = ?")
            params.append(cohort_code)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.database._transaction() as connection:
            rows = connection.execute(
                f"""
                SELECT training_reports.id, training_reports.learner_id,
                       learners.display_name, learners.cohort_code, learners.tenant_id,
                       training_reports.report_date, training_reports.activities,
                       training_reports.hours, training_reports.status,
                       training_reports.trainer_status, training_reports.signed_at,
                       training_reports.created_at, training_reports.updated_at
                FROM training_reports
                JOIN learners ON learners.learner_id = training_reports.learner_id
                {where}
                ORDER BY training_reports.report_date DESC, training_reports.id DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()
        return [Database._row_dict(row) for row in rows]

    def list_topic_hotspots(
        self,
        *,
        tenant_id: str | None = None,
        cohort_code: str | None = None,
        limit: int = 12,
    ) -> list[dict[str, Any]]:
        """Aggregate wrong answers by topic for the trainer heatmap."""
        clauses = ["learners.deleted_at IS NULL", "learners.role = 'learner'"]
        params: list[Any] = []
        if tenant_id:
            clauses.append("learners.tenant_id = ?")
            params.append(tenant_id)
        if cohort_code:
            clauses.append("learners.cohort_code = ?")
            params.append(cohort_code)
        where = " AND ".join(clauses)
        with self.database._transaction() as connection:
            rows = connection.execute(
                f"""
                SELECT question_categories.slug AS category_slug,
                       question_categories.title AS title,
                       COALESCE(SUM(question_progress.wrong_count), 0) AS wrong_count,
                       COUNT(DISTINCT question_progress.learner_id) AS learner_count
                FROM question_progress
                JOIN quiz_questions
                    ON quiz_questions.question_id = question_progress.question_id
                JOIN question_categories
                    ON question_categories.id = quiz_questions.category_id
                JOIN learners
                    ON learners.learner_id = question_progress.learner_id
                WHERE {where}
                GROUP BY question_categories.slug, question_categories.title
                HAVING COALESCE(SUM(question_progress.wrong_count), 0) > 0
                ORDER BY wrong_count DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()
        result = []
        for row in rows:
            payload = Database._row_dict(row)
            payload["wrong_count"] = int(payload["wrong_count"])
            payload["learner_count"] = int(payload["learner_count"])
            result.append(payload)
        return result

    def export_training_reports_text(self, learner_id: str) -> str:
        """Build a printable text export of Berichtsheft entries."""
        rows = self.database.list_training_reports(learner_id)
        learner = self.database.get_learner(learner_id)
        lines = [
            "BZE Online Campus — Berichtsheft-Export",
            f"Lerner: {learner['display_name'] if learner else learner_id}",
            f"Kohorte: {(learner or {}).get('cohort_code') or '-'}",
            "",
        ]
        for row in rows:
            lines.extend(
                [
                    f"Datum: {row['report_date']}  Stunden: {row['hours']}  "
                    f"Status: {row['status']}",
                    row["activities"],
                    "-" * 40,
                ]
            )
        if not rows:
            lines.append("Keine Eintraege.")
        return "\n".join(lines)

    def export_training_reports_pdf(self, learner_id: str) -> bytes:
        """Build a printable PDF of Berichtsheft entries."""
        from app.services.simple_pdf import build_simple_pdf

        body = self.export_training_reports_text(learner_id)
        return build_simple_pdf(
            "BZE Online Campus — Berichtsheft",
            [body],
        )

    def xp_leaderboard(self, cohort_code: str | None, limit: int = 20) -> list[dict[str, Any]]:
        """Rank learners by answered/mastered question XP within a cohort."""
        learners = [
            row
            for row in self.list_cohort_learners(cohort_code)
            if row["role"] == "learner"
        ]
        board: list[dict[str, Any]] = []
        for learner in learners:
            progress = self.database.list_question_progress(learner["learner_id"])
            answered = sum(1 for item in progress.values() if item.answered_count > 0)
            mastered = sum(1 for item in progress.values() if item.mastered)
            wrong = sum(item.wrong_count for item in progress.values())
            xp = max(0, answered * 10 + mastered * 25 - wrong * 3)
            alias = f"Azubi {learner['learner_id'][-4:]}"
            board.append(
                {
                    "alias": alias,
                    "xp": xp,
                    "level": 1 + xp // 120,
                    "mastered_questions": mastered,
                    "is_self": False,
                    "learner_id": learner["learner_id"],
                }
            )
        board.sort(key=lambda item: item["xp"], reverse=True)
        for index, item in enumerate(board[:limit], start=1):
            item["rank"] = index
        return board[:limit]

    @staticmethod
    def _formula_row(row: Any) -> dict[str, Any]:
        """Decode JSON columns on a formula row."""
        payload = Database._row_dict(row)
        payload["legend"] = json.loads(payload.pop("legend_json"))
        payload["source_keys"] = json.loads(payload.pop("source_keys_json"))
        return payload


def _week_start(day: str) -> str:
    """Return Monday of the ISO week for YYYY-MM-DD."""
    from datetime import date, timedelta

    current = date.fromisoformat(day)
    return (current - timedelta(days=current.weekday())).isoformat()
