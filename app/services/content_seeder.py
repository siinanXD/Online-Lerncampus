"""Import Python seed content into the content database tables."""

from __future__ import annotations

import json
from typing import Any

from app.db.dialect import insert_ignore_sql

from app.data.content_bundle import ContentBundle, load_json_bundle, load_python_bundle
from app.data.content.subchapters import slugify
from app.models.domain import ReviewStatus
from app.services.database import Database, utc_now_iso


class ContentSeeder:
    """Idempotent importer from Python or JSON bundles into content tables."""

    OCCUPATION_SLUG = "maschinen-und-anlagenfuehrer"
    SPECIALIZATION_SLUG = "metall-und-kunststofftechnik"

    def __init__(
        self,
        database: Database,
        bundle: ContentBundle | None = None,
    ) -> None:
        """Attach to an initialized application database."""
        self.database = database
        self.bundle = bundle or load_python_bundle()

    def is_empty(self) -> bool:
        """Return True when no quiz questions have been imported yet."""
        with self.database._transaction() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM quiz_questions"
            ).fetchone()
        return int(row["count"]) == 0

    def seed_all(self, *, force: bool = False) -> dict[str, int]:
        """Import the full MAF seed bundle."""
        if force:
            self._clear_content_tables()
        elif not self.is_empty():
            return self.counts()

        counts: dict[str, int] = {}
        with self.database._transaction() as connection:
            occupation_id = self._upsert_occupation(connection)
            specialization_id = self._upsert_specialization(connection, occupation_id)
            month_ids = self._upsert_curriculum_months(
                connection,
                occupation_id,
                specialization_id,
            )
            counts["learning_modules"] = self._upsert_learning_modules(
                connection,
                month_ids,
            )
            counts["source_documents"] = self._upsert_sources(connection)
            category_ids = self._upsert_categories(connection, month_ids)
            counts["question_categories"] = len(category_ids)
            counts["learning_units"] = self._upsert_learning_units(
                connection,
                month_ids,
                category_ids,
            )
            question_pk = self._upsert_quiz_questions(connection, category_ids)
            counts["quiz_questions"] = len(question_pk)
            open_pk = self._upsert_open_questions(connection, category_ids)
            counts["open_questions"] = len(open_pk)
            counts["practice_exams"] = self._upsert_exams(
                connection,
                question_pk,
                open_pk,
                month_ids,
            )
        return self.counts()

    def counts(self) -> dict[str, int]:
        """Return row counts for the main content tables."""
        tables = (
            "occupations",
            "question_categories",
            "learning_units",
            "quiz_questions",
            "open_questions",
            "practice_exams",
        )
        result: dict[str, int] = {}
        with self.database._transaction() as connection:
            for table in tables:
                row = connection.execute(
                    f"SELECT COUNT(*) AS count FROM {table}"
                ).fetchone()
                result[table] = int(row["count"])
        return result

    def _clear_content_tables(self) -> None:
        """Remove imported content while keeping learner tables intact."""
        tables = (
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
            "learning_modules",
            "curriculum_months",
            "specializations",
            "occupations",
            "source_documents",
        )
        with self.database._transaction() as connection:
            for table in tables:
                connection.execute(f"DELETE FROM {table}")

    def _upsert_occupation(self, connection: sqlite3.Connection) -> int:
        occupation = self.bundle.occupations[0]
        connection.execute(
            """
            INSERT INTO occupations (slug, title, duration_months, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(slug) DO UPDATE SET
                title = excluded.title,
                duration_months = excluded.duration_months
            """,
            (
                occupation.slug,
                occupation.title,
                occupation.duration_months,
                utc_now_iso(),
            ),
        )
        row = connection.execute(
            "SELECT id FROM occupations WHERE slug = ?",
            (occupation.slug,),
        ).fetchone()
        return int(row["id"])

    def _upsert_specialization(
        self,
        connection: sqlite3.Connection,
        occupation_id: int,
    ) -> int:
        specialization = self.bundle.occupations[0].specializations[0]
        connection.execute(
            """
            INSERT INTO specializations (occupation_id, slug, title, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(occupation_id, slug) DO UPDATE SET
                title = excluded.title
            """,
            (occupation_id, specialization, specialization.replace("-", " ").title(), utc_now_iso()),
        )
        row = connection.execute(
            """
            SELECT id FROM specializations
            WHERE occupation_id = ? AND slug = ?
            """,
            (occupation_id, specialization),
        ).fetchone()
        return int(row["id"])

    def _upsert_curriculum_months(
        self,
        connection: sqlite3.Connection,
        occupation_id: int,
        specialization_id: int,
    ) -> dict[int, int]:
        month_ids: dict[int, int] = {}
        for entry in self.bundle.curriculum:
            connection.execute(
                """
                INSERT INTO curriculum_months (
                    occupation_id,
                    specialization_id,
                    month,
                    year,
                    title,
                    focus_area,
                    learning_goals_json,
                    is_exam_preparation,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(occupation_id, specialization_id, month) DO UPDATE SET
                    title = excluded.title,
                    focus_area = excluded.focus_area,
                    learning_goals_json = excluded.learning_goals_json,
                    is_exam_preparation = excluded.is_exam_preparation
                """,
                (
                    occupation_id,
                    specialization_id,
                    entry.month,
                    entry.year,
                    entry.title,
                    entry.focus_area,
                    json.dumps(entry.learning_goals, ensure_ascii=False),
                    int(entry.is_exam_preparation),
                    utc_now_iso(),
                ),
            )
            row = connection.execute(
                """
                SELECT id FROM curriculum_months
                WHERE occupation_id = ? AND specialization_id = ? AND month = ?
                """,
                (occupation_id, specialization_id, entry.month),
            ).fetchone()
            month_ids[entry.month] = int(row["id"])
        return month_ids

    def _upsert_learning_modules(
        self,
        connection: sqlite3.Connection,
        month_ids: dict[int, int],
    ) -> int:
        count = 0
        for module in self.bundle.modules:
            curriculum_month_id = month_ids[module.month]
            connection.execute(
                """
                INSERT INTO learning_modules (
                    curriculum_month_id,
                    slug,
                    title,
                    mission_type,
                    lesson_goal,
                    quiz_focus,
                    required_review,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title = excluded.title,
                    mission_type = excluded.mission_type,
                    lesson_goal = excluded.lesson_goal,
                    quiz_focus = excluded.quiz_focus,
                    required_review = excluded.required_review
                """,
                (
                    curriculum_month_id,
                    module.slug,
                    module.title,
                    module.mission_type,
                    module.lesson_goal,
                    module.quiz_focus,
                    int(module.required_review),
                    utc_now_iso(),
                ),
            )
            count += 1
        return count

    def _upsert_sources(self, connection: sqlite3.Connection) -> int:
        for source in self.bundle.sources:
            connection.execute(
                """
                INSERT INTO source_documents (
                    key,
                    title,
                    publisher,
                    url,
                    trust_tier,
                    allowed_usage,
                    topics_json,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    title = excluded.title,
                    publisher = excluded.publisher,
                    url = excluded.url,
                    trust_tier = excluded.trust_tier,
                    allowed_usage = excluded.allowed_usage,
                    topics_json = excluded.topics_json
                """,
                (
                    source.key,
                    source.title,
                    source.publisher,
                    source.url,
                    source.trust_tier,
                    source.allowed_usage,
                    json.dumps(source.topics, ensure_ascii=False),
                    utc_now_iso(),
                ),
            )
        return len(self.bundle.sources)

    def _upsert_categories(
        self,
        connection: sqlite3.Connection,
        month_ids: dict[int, int],
    ) -> dict[str, int]:
        category_ids: dict[str, int] = {}
        for category in self.bundle.categories:
            curriculum_month_id = month_ids[category.month]
            connection.execute(
                """
                INSERT INTO question_categories (
                    slug,
                    curriculum_month_id,
                    subchapter_number,
                    title,
                    description,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description
                """,
                (
                    category.slug,
                    curriculum_month_id,
                    category.subchapter_number,
                    category.title,
                    category.description,
                    utc_now_iso(),
                ),
            )
            row = connection.execute(
                "SELECT id FROM question_categories WHERE slug = ?",
                (category.slug,),
            ).fetchone()
            category_ids[category.slug] = int(row["id"])
        return category_ids

    def _upsert_learning_units(
        self,
        connection: sqlite3.Connection,
        month_ids: dict[int, int],
        category_ids: dict[str, int],
    ) -> int:
        source_key_to_id = self._source_key_map(connection)
        count = 0
        for unit in self.bundle.units:
            curriculum_month_id = month_ids[unit.month]
            connection.execute(
                """
                INSERT INTO learning_units (
                    slug,
                    curriculum_month_id,
                    position,
                    title,
                    subtitle,
                    learning_goals_json,
                    practice_task,
                    estimated_minutes,
                    review_status,
                    version,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                ON CONFLICT(slug) DO UPDATE SET
                    curriculum_month_id = excluded.curriculum_month_id,
                    position = excluded.position,
                    title = excluded.title,
                    subtitle = excluded.subtitle,
                    learning_goals_json = excluded.learning_goals_json,
                    practice_task = excluded.practice_task,
                    estimated_minutes = excluded.estimated_minutes,
                    review_status = excluded.review_status,
                    updated_at = excluded.updated_at
                """,
                (
                    unit.slug,
                    curriculum_month_id,
                    unit.position,
                    unit.title,
                    unit.subtitle,
                    json.dumps(unit.learning_goals, ensure_ascii=False),
                    unit.practice_task,
                    unit.estimated_minutes,
                    unit.review_status.value,
                    utc_now_iso(),
                    utc_now_iso(),
                ),
            )
            row = connection.execute(
                "SELECT id FROM learning_units WHERE slug = ?",
                (unit.slug,),
            ).fetchone()
            unit_id = int(row["id"])
            connection.execute(
                "DELETE FROM theory_blocks WHERE learning_unit_id = ?",
                (unit_id,),
            )
            connection.execute(
                "DELETE FROM glossary_entries WHERE learning_unit_id = ?",
                (unit_id,),
            )
            connection.execute(
                "DELETE FROM learning_unit_categories WHERE learning_unit_id = ?",
                (unit_id,),
            )
            connection.execute(
                """
                DELETE FROM content_source_links
                WHERE entity_type = 'learning_unit' AND entity_id = ?
                """,
                (unit_id,),
            )
            for position, block in enumerate(unit.theory_blocks, start=1):
                connection.execute(
                    """
                    INSERT INTO theory_blocks (
                        learning_unit_id,
                        position,
                        heading,
                        body,
                        key_points_json,
                        norm_references_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        unit_id,
                        position,
                        block.heading,
                        block.body,
                        json.dumps(block.key_points, ensure_ascii=False),
                        json.dumps(block.norm_references, ensure_ascii=False),
                    ),
                )
            for term, definition in unit.glossary.items():
                connection.execute(
                    """
                    INSERT INTO glossary_entries (learning_unit_id, term, definition)
                    VALUES (?, ?, ?)
                    """,
                    (unit_id, term, definition),
                )
            for category_slug in unit.category_slugs:
                category_id = category_ids.get(category_slug)
                if category_id is None:
                    continue
                connection.execute(
                    insert_ignore_sql(
                        "learning_unit_categories",
                        "learning_unit_id, category_id",
                        "?, ?",
                        "learning_unit_id, category_id",
                        self.database.dialect,
                    ),
                    (unit_id, category_id),
                )
            self._link_sources(
                connection,
                source_key_to_id,
                "learning_unit",
                unit_id,
                unit.source_keys,
                self.database.dialect,
            )
            count += 1
        return count

    def _upsert_quiz_questions(
        self,
        connection: sqlite3.Connection,
        category_ids: dict[str, int],
    ) -> dict[str, int]:
        source_key_to_id = self._source_key_map(connection)
        question_pk: dict[str, int] = {}
        for question in self.bundle.questions:
            category_id = category_ids[question.category_slug]
            connection.execute(
                """
                INSERT INTO quiz_questions (
                    question_id,
                    category_id,
                    prompt,
                    options_json,
                    correct_option_index,
                    explanation,
                    difficulty,
                    exam_style,
                    review_status,
                    version,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                ON CONFLICT(question_id) DO UPDATE SET
                    category_id = excluded.category_id,
                    prompt = excluded.prompt,
                    options_json = excluded.options_json,
                    correct_option_index = excluded.correct_option_index,
                    explanation = excluded.explanation,
                    difficulty = excluded.difficulty,
                    exam_style = excluded.exam_style,
                    review_status = excluded.review_status,
                    is_active = excluded.is_active,
                    updated_at = excluded.updated_at
                """,
                (
                    question.question_id,
                    category_id,
                    question.prompt,
                    json.dumps(question.options, ensure_ascii=False),
                    question.correct_option_index,
                    question.explanation,
                    question.difficulty,
                    question.exam_style,
                    ReviewStatus.DRAFT.value,
                    utc_now_iso(),
                    utc_now_iso(),
                ),
            )
            row = connection.execute(
                "SELECT id FROM quiz_questions WHERE question_id = ?",
                (question.question_id,),
            ).fetchone()
            pk = int(row["id"])
            question_pk[question.question_id] = pk
            connection.execute(
                """
                DELETE FROM content_source_links
                WHERE entity_type = 'quiz_question' AND entity_id = ?
                """,
                (pk,),
            )
            self._link_sources(
                connection,
                source_key_to_id,
                "quiz_question",
                pk,
                question.source_keys,
                self.database.dialect,
            )
        return question_pk

    def _upsert_open_questions(
        self,
        connection: sqlite3.Connection,
        category_ids: dict[str, int],
    ) -> dict[str, int]:
        source_key_to_id = self._source_key_map(connection)
        open_pk: dict[str, int] = {}
        for question in self.bundle.open_questions:
            category_id = category_ids[question.category_slug]
            connection.execute(
                """
                INSERT INTO open_questions (
                    question_id,
                    category_id,
                    prompt,
                    answer_format,
                    sample_solution,
                    review_status,
                    version,
                    is_active,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, 1, 1, ?, ?)
                ON CONFLICT(question_id) DO UPDATE SET
                    category_id = excluded.category_id,
                    prompt = excluded.prompt,
                    answer_format = excluded.answer_format,
                    sample_solution = excluded.sample_solution,
                    review_status = excluded.review_status,
                    is_active = excluded.is_active,
                    updated_at = excluded.updated_at
                """,
                (
                    question.question_id,
                    category_id,
                    question.prompt,
                    question.answer_format.value,
                    question.sample_solution,
                    ReviewStatus.DRAFT.value,
                    utc_now_iso(),
                    utc_now_iso(),
                ),
            )
            row = connection.execute(
                "SELECT id FROM open_questions WHERE question_id = ?",
                (question.question_id,),
            ).fetchone()
            pk = int(row["id"])
            open_pk[question.question_id] = pk
            connection.execute(
                "DELETE FROM open_question_criteria WHERE open_question_id = ?",
                (pk,),
            )
            for position, criterion in enumerate(question.criteria, start=1):
                connection.execute(
                    """
                    INSERT INTO open_question_criteria (
                        open_question_id,
                        position,
                        description,
                        points
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (pk, position, criterion.description, criterion.points),
                )
            connection.execute(
                """
                DELETE FROM content_source_links
                WHERE entity_type = 'open_question' AND entity_id = ?
                """,
                (pk,),
            )
            self._link_sources(
                connection,
                source_key_to_id,
                "open_question",
                pk,
                question.source_keys,
                self.database.dialect,
            )
        return open_pk

    def _upsert_exams(
        self,
        connection: sqlite3.Connection,
        question_pk: dict[str, int],
        open_pk: dict[str, int],
        month_ids: dict[int, int],
    ) -> int:
        count = 0
        for exam in self.bundle.exams:
            curriculum_month_id = None
            if exam.exam_id.startswith("checkpoint-"):
                try:
                    month_number = int(exam.exam_id.removeprefix("checkpoint-"))
                    curriculum_month_id = month_ids.get(month_number)
                except ValueError:
                    curriculum_month_id = None
            connection.execute(
                """
                INSERT INTO practice_exams (
                    exam_id,
                    title,
                    description,
                    passing_score_percent,
                    time_limit_minutes,
                    is_checkpoint,
                    curriculum_month_id,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(exam_id) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    passing_score_percent = excluded.passing_score_percent,
                    time_limit_minutes = excluded.time_limit_minutes,
                    is_checkpoint = excluded.is_checkpoint,
                    curriculum_month_id = excluded.curriculum_month_id
                """,
                (
                    exam.exam_id,
                    exam.title,
                    exam.description,
                    exam.passing_score_percent,
                    exam.time_limit_minutes,
                    int(exam.is_checkpoint),
                    curriculum_month_id,
                    utc_now_iso(),
                ),
            )
            row = connection.execute(
                "SELECT id FROM practice_exams WHERE exam_id = ?",
                (exam.exam_id,),
            ).fetchone()
            exam_id = int(row["id"])
            connection.execute(
                "DELETE FROM exam_quiz_questions WHERE exam_id = ?",
                (exam_id,),
            )
            connection.execute(
                "DELETE FROM exam_open_questions WHERE exam_id = ?",
                (exam_id,),
            )
            for position, question_id in enumerate(exam.question_ids, start=1):
                quiz_id = question_pk[question_id]
                connection.execute(
                    """
                    INSERT INTO exam_quiz_questions (
                        exam_id,
                        quiz_question_id,
                        position
                    )
                    VALUES (?, ?, ?)
                    """,
                    (exam_id, quiz_id, position),
                )
            for position, question_id in enumerate(exam.open_question_ids, start=1):
                open_id = open_pk[question_id]
                connection.execute(
                    """
                    INSERT INTO exam_open_questions (
                        exam_id,
                        open_question_id,
                        position
                    )
                    VALUES (?, ?, ?)
                    """,
                    (exam_id, open_id, position),
                )
            count += 1
        return count

    @staticmethod
    def _source_key_map(connection: sqlite3.Connection) -> dict[str, int]:
        rows = connection.execute("SELECT id, key FROM source_documents").fetchall()
        return {row["key"]: int(row["id"]) for row in rows}

    @staticmethod
    def _link_sources(
        connection: Any,
        source_key_to_id: dict[str, int],
        entity_type: str,
        entity_id: int,
        source_keys: list[str],
        dialect: Any,
    ) -> None:
        for source_key in source_keys:
            source_id = source_key_to_id.get(source_key)
            if source_id is None:
                continue
            connection.execute(
                insert_ignore_sql(
                    "content_source_links",
                    "source_id, entity_type, entity_id",
                    "?, ?, ?",
                    "source_id, entity_type, entity_id",
                    dialect,
                ),
                (source_id, entity_type, entity_id),
            )


def first_chapter_payload(
    category_rows: list[dict[str, Any]],
    *,
    first_chapter: dict[str, Any] | None = None,
) -> dict[str, object]:
    """Build the first-chapter response shape from DB category rows."""
    chapter = first_chapter or load_python_bundle().first_chapter
    slugs = chapter["category_slugs"]
    categories = [row for row in category_rows if row["slug"] in slugs]
    if not categories:
        categories = list(category_rows)
    categories.sort(key=lambda row: row["subchapter_number"])
    return {
        "title": chapter["title"],
        "mission_goal": chapter["mission_goal"],
        "fachkunde": chapter["fachkunde"],
        "subchapters": categories,
        "checkpoint_exam_id": chapter["checkpoint_exam_id"],
    }


def month_category_slugs(
    month: int,
    *,
    month_subchapters: dict[int, tuple[str, ...]] | None = None,
) -> list[str]:
    """Return deterministic category slugs for one curriculum month."""
    mapping = month_subchapters or load_python_bundle().month_subchapters
    return [f"m{month:02d}-{slugify(title)}" for title in mapping[month]]
