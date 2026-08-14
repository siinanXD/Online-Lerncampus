"""Read learning content from SQLite content tables."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from app.models.domain import (
    AnswerFormat,
    GradingCriterion,
    LearningUnit,
    OpenQuestion,
    PracticeExam,
    QuestionCategory,
    QuizQuestion,
    ReviewStatus,
    TheoryBlock,
)
from app.data.content.helpers import rotate_question_options
from app.data.question_bank import FIRST_CHAPTER
from app.services.database import Database


class ContentRepository:
    """Database-backed repository for curriculum content."""

    def __init__(self, database: Database, *, require_approved: bool = False) -> None:
        """Attach to the application database."""
        self.database = database
        self.require_approved = require_approved

    def _review_clause(self, alias: str) -> tuple[str, tuple[Any, ...]]:
        if not self.require_approved:
            return "", ()
        return f" AND {alias}.review_status = ?", (ReviewStatus.APPROVED.value,)

    def list_categories(self, month: int | None = None) -> list[QuestionCategory]:
        """Return question categories, optionally filtered by month number."""
        query = """
            SELECT
                qc.slug,
                cm.month,
                cm.title AS chapter_title,
                qc.subchapter_number,
                qc.title,
                qc.description
            FROM question_categories qc
            JOIN curriculum_months cm ON cm.id = qc.curriculum_month_id
            WHERE 1 = 1
        """
        params: list[Any] = []
        if month is not None:
            query += " AND cm.month = ?"
            params.append(month)
        query += " ORDER BY cm.month, qc.subchapter_number"
        with self.database._transaction() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_category(row) for row in rows]

    def list_questions(
        self,
        category_slug: str | None = None,
        month: int | None = None,
    ) -> list[QuizQuestion]:
        """Return quiz questions with optional filters."""
        review_sql, review_params = self._review_clause("qq")
        query = f"""
            SELECT
                qq.question_id,
                qc.slug AS category_slug,
                qq.prompt,
                qq.options_json,
                qq.correct_option_index,
                qq.explanation,
                qq.difficulty,
                qq.exam_style,
                GROUP_CONCAT(DISTINCT sd.key) AS source_keys
            FROM quiz_questions qq
            JOIN question_categories qc ON qc.id = qq.category_id
            JOIN curriculum_months cm ON cm.id = qc.curriculum_month_id
            LEFT JOIN content_source_links csl
                ON csl.entity_type = 'quiz_question' AND csl.entity_id = qq.id
            LEFT JOIN source_documents sd ON sd.id = csl.source_id
            WHERE qq.is_active = 1{review_sql}
        """
        params = list(review_params)
        if category_slug is not None:
            query += " AND qc.slug = ?"
            params.append(category_slug)
        if month is not None:
            query += " AND cm.month = ?"
            params.append(month)
        query += """
            GROUP BY
                qq.id,
                qq.question_id,
                qc.slug,
                qq.prompt,
                qq.options_json,
                qq.correct_option_index,
                qq.explanation,
                qq.difficulty,
                qq.exam_style,
                cm.month,
                qc.subchapter_number
            ORDER BY cm.month, qc.subchapter_number, qq.question_id
        """
        with self.database._transaction() as connection:
            rows = connection.execute(query, params).fetchall()
        return [self._row_to_quiz_question(row) for row in rows]

    def get_question(self, question_id: str) -> QuizQuestion | None:
        """Return one quiz question by public id."""
        review_sql, review_params = self._review_clause("qq")
        query = f"""
            SELECT
                qq.question_id,
                qc.slug AS category_slug,
                qq.prompt,
                qq.options_json,
                qq.correct_option_index,
                qq.explanation,
                qq.difficulty,
                qq.exam_style,
                GROUP_CONCAT(DISTINCT sd.key) AS source_keys
            FROM quiz_questions qq
            JOIN question_categories qc ON qc.id = qq.category_id
            LEFT JOIN content_source_links csl
                ON csl.entity_type = 'quiz_question' AND csl.entity_id = qq.id
            LEFT JOIN source_documents sd ON sd.id = csl.source_id
            WHERE qq.question_id = ? AND qq.is_active = 1{review_sql}
            GROUP BY
                qq.id,
                qq.question_id,
                qc.slug,
                qq.prompt,
                qq.options_json,
                qq.correct_option_index,
                qq.explanation,
                qq.difficulty,
                qq.exam_style
        """
        with self.database._transaction() as connection:
            row = connection.execute(query, (question_id, *review_params)).fetchone()
        return self._row_to_quiz_question(row) if row else None

    def list_learning_units(self, month: int | None = None) -> list[LearningUnit]:
        """Return learning units ordered by month and position."""
        review_sql, review_params = self._review_clause("lu")
        query = f"""
            SELECT
                lu.slug,
                cm.month,
                lu.position,
                lu.title,
                lu.subtitle,
                lu.learning_goals_json,
                lu.practice_task,
                lu.estimated_minutes,
                lu.review_status,
                GROUP_CONCAT(DISTINCT qc.slug) AS category_slugs,
                GROUP_CONCAT(DISTINCT sd.key) AS source_keys
            FROM learning_units lu
            JOIN curriculum_months cm ON cm.id = lu.curriculum_month_id
            LEFT JOIN learning_unit_categories luc ON luc.learning_unit_id = lu.id
            LEFT JOIN question_categories qc ON qc.id = luc.category_id
            LEFT JOIN content_source_links csl
                ON csl.entity_type = 'learning_unit' AND csl.entity_id = lu.id
            LEFT JOIN source_documents sd ON sd.id = csl.source_id
            WHERE 1 = 1{review_sql}
        """
        params = list(review_params)
        if month is not None:
            query += " AND cm.month = ?"
            params.append(month)
        query += """
            GROUP BY
                lu.id,
                lu.slug,
                cm.month,
                lu.position,
                lu.title,
                lu.subtitle,
                lu.learning_goals_json,
                lu.practice_task,
                lu.estimated_minutes,
                lu.review_status
            ORDER BY cm.month, lu.position
        """
        with self.database._transaction() as connection:
            rows = connection.execute(query, params).fetchall()
            return [
                self._hydrate_learning_unit(connection, self._row_to_learning_unit(row))
                for row in rows
            ]

    def get_learning_unit(self, slug: str) -> LearningUnit:
        """Return one learning unit or raise ValueError."""
        units = self.list_learning_units()
        for unit in units:
            if unit.slug == slug:
                return unit
        raise ValueError(f"Unbekannte Lerneinheit: {slug}")

    def list_open_questions(self, question_ids: list[str]) -> list[OpenQuestion]:
        """Return open questions for the given public ids."""
        if not question_ids:
            return []
        placeholders = ", ".join("?" for _ in question_ids)
        review_sql, review_params = self._review_clause("oq")
        query = f"""
            SELECT
                oq.question_id,
                qc.slug AS category_slug,
                oq.prompt,
                oq.answer_format,
                oq.sample_solution,
                GROUP_CONCAT(DISTINCT sd.key) AS source_keys
            FROM open_questions oq
            JOIN question_categories qc ON qc.id = oq.category_id
            LEFT JOIN content_source_links csl
                ON csl.entity_type = 'open_question' AND csl.entity_id = oq.id
            LEFT JOIN source_documents sd ON sd.id = csl.source_id
            WHERE oq.question_id IN ({placeholders})
                AND oq.is_active = 1{review_sql}
            GROUP BY
                oq.id,
                oq.question_id,
                qc.slug,
                oq.prompt,
                oq.answer_format,
                oq.sample_solution
        """
        with self.database._transaction() as connection:
            rows = connection.execute(query, (*question_ids, *review_params)).fetchall()
            questions = [self._row_to_open_question(connection, row) for row in rows]
        order = {question_id: index for index, question_id in enumerate(question_ids)}
        return sorted(questions, key=lambda item: order[item.question_id])

    def list_exams(self) -> list[PracticeExam]:
        """Return all practice exam definitions."""
        query = """
            SELECT
                pe.exam_id,
                pe.title,
                pe.description,
                pe.passing_score_percent,
                pe.time_limit_minutes,
                pe.is_checkpoint
            FROM practice_exams pe
            ORDER BY pe.exam_id
        """
        with self.database._transaction() as connection:
            rows = connection.execute(query).fetchall()
            exams: list[PracticeExam] = []
            for row in rows:
                exam_id = row["exam_id"]
                question_ids = [
                    item["question_id"]
                    for item in connection.execute(
                        """
                        SELECT qq.question_id
                        FROM exam_quiz_questions eq
                        JOIN quiz_questions qq ON qq.id = eq.quiz_question_id
                        WHERE eq.exam_id = (
                            SELECT id FROM practice_exams WHERE exam_id = ?
                        )
                        ORDER BY eq.position
                        """,
                        (exam_id,),
                    ).fetchall()
                ]
                open_ids = [
                    item["question_id"]
                    for item in connection.execute(
                        """
                        SELECT oq.question_id
                        FROM exam_open_questions eo
                        JOIN open_questions oq ON oq.id = eo.open_question_id
                        WHERE eo.exam_id = (
                            SELECT id FROM practice_exams WHERE exam_id = ?
                        )
                        ORDER BY eo.position
                        """,
                        (exam_id,),
                    ).fetchall()
                ]
                exams.append(
                    PracticeExam(
                        exam_id=exam_id,
                        title=row["title"],
                        description=row["description"],
                        question_ids=question_ids,
                        passing_score_percent=row["passing_score_percent"],
                        open_question_ids=open_ids,
                        time_limit_minutes=row["time_limit_minutes"],
                    )
                )
        return exams

    def get_exam(self, exam_id: str) -> tuple[PracticeExam, list[QuizQuestion]] | None:
        """Return one exam and its ordered quiz questions."""
        exams = self.list_exams()
        exam = next((item for item in exams if item.exam_id == exam_id), None)
        if exam is None:
            return None
        question_map = {question.question_id: question for question in self.list_questions()}
        questions = [
            question_map[question_id]
            for question_id in exam.question_ids
            if question_id in question_map
        ]
        return exam, questions

    def get_first_chapter(self) -> dict[str, object]:
        """Return the first chapter package from database categories."""
        categories = self.list_categories(month=1)
        category_rows = [
            {
                "slug": category.slug,
                "month": category.month,
                "chapter_title": category.chapter_title,
                "subchapter_number": category.subchapter_number,
                "title": category.title,
                "description": category.description,
            }
            for category in categories
        ]
        return self._first_chapter_payload(category_rows)

    def _first_chapter_payload(
        self,
        category_rows: list[dict[str, object]],
    ) -> dict[str, object]:
        slugs = FIRST_CHAPTER["category_slugs"]
        matched = [row for row in category_rows if row["slug"] in slugs]
        using_defaults = bool(matched)
        categories = matched or list(category_rows)
        categories.sort(key=lambda row: row["subchapter_number"])
        title = FIRST_CHAPTER["title"]
        checkpoint = FIRST_CHAPTER["checkpoint_exam_id"]
        if not using_defaults and categories:
            title = f"Monat 1: {categories[0]['chapter_title']}"
            exams = self.list_exams()
            if exams:
                checkpoint = exams[0].exam_id
        return {
            "title": title,
            "mission_goal": FIRST_CHAPTER["mission_goal"],
            "fachkunde": FIRST_CHAPTER["fachkunde"],
            "subchapters": categories,
            "checkpoint_exam_id": checkpoint,
        }

    def _hydrate_learning_unit(
        self,
        connection: sqlite3.Connection,
        unit: LearningUnit,
    ) -> LearningUnit:
        row = connection.execute(
            "SELECT id FROM learning_units WHERE slug = ?",
            (unit.slug,),
        ).fetchone()
        unit_id = int(row["id"])
        theory_rows = connection.execute(
            """
            SELECT heading, body, key_points_json, norm_references_json
            FROM theory_blocks
            WHERE learning_unit_id = ?
            ORDER BY position
            """,
            (unit_id,),
        ).fetchall()
        glossary_rows = connection.execute(
            """
            SELECT term, definition
            FROM glossary_entries
            WHERE learning_unit_id = ?
            ORDER BY term
            """,
            (unit_id,),
        ).fetchall()
        theory_blocks = [
            TheoryBlock(
                heading=item["heading"],
                body=item["body"],
                key_points=json.loads(item["key_points_json"]),
                norm_references=json.loads(item["norm_references_json"]),
            )
            for item in theory_rows
        ]
        glossary = {item["term"]: item["definition"] for item in glossary_rows}
        return LearningUnit(
            slug=unit.slug,
            month=unit.month,
            position=unit.position,
            title=unit.title,
            subtitle=unit.subtitle,
            learning_goals=unit.learning_goals,
            theory_blocks=theory_blocks,
            practice_task=unit.practice_task,
            glossary=glossary,
            category_slugs=unit.category_slugs,
            source_keys=unit.source_keys,
            review_status=unit.review_status,
            estimated_minutes=unit.estimated_minutes,
        )

    @staticmethod
    def _split_csv(value: str | None) -> list[str]:
        if not value:
            return []
        return [part for part in value.split(",") if part]

    def _row_to_category(self, row: sqlite3.Row) -> QuestionCategory:
        return QuestionCategory(
            slug=row["slug"],
            month=row["month"],
            chapter_title=row["chapter_title"],
            subchapter_number=row["subchapter_number"],
            title=row["title"],
            description=row["description"],
        )

    def _row_to_quiz_question(self, row: sqlite3.Row) -> QuizQuestion:
        source_keys = self._split_csv(row["source_keys"])
        return rotate_question_options(
            QuizQuestion(
                question_id=row["question_id"],
                category_slug=row["category_slug"],
                prompt=row["prompt"],
                options=json.loads(row["options_json"]),
                correct_option_index=row["correct_option_index"],
                explanation=row["explanation"],
                difficulty=row["difficulty"],
                exam_style=row["exam_style"],
                source_keys=source_keys,
            )
        )

    def _row_to_learning_unit(self, row: sqlite3.Row) -> LearningUnit:
        return LearningUnit(
            slug=row["slug"],
            month=row["month"],
            position=row["position"],
            title=row["title"],
            subtitle=row["subtitle"],
            learning_goals=json.loads(row["learning_goals_json"]),
            theory_blocks=[],
            practice_task=row["practice_task"],
            glossary={},
            category_slugs=self._split_csv(row["category_slugs"]),
            source_keys=self._split_csv(row["source_keys"]),
            review_status=ReviewStatus(row["review_status"]),
            estimated_minutes=row["estimated_minutes"],
        )

    def _row_to_open_question(
        self,
        connection: sqlite3.Connection,
        row: sqlite3.Row,
    ) -> OpenQuestion:
        db_row = connection.execute(
            "SELECT id FROM open_questions WHERE question_id = ?",
            (row["question_id"],),
        ).fetchone()
        criteria_rows = connection.execute(
            """
            SELECT description, points
            FROM open_question_criteria
            WHERE open_question_id = ?
            ORDER BY position
            """,
            (int(db_row["id"]),),
        ).fetchall()
        return OpenQuestion(
            question_id=row["question_id"],
            category_slug=row["category_slug"],
            prompt=row["prompt"],
            answer_format=AnswerFormat(row["answer_format"]),
            sample_solution=row["sample_solution"],
            criteria=[
                GradingCriterion(description=item["description"], points=item["points"])
                for item in criteria_rows
            ],
            source_keys=self._split_csv(row["source_keys"]),
        )
