"""Repository for question categories, questions, and practice exams."""

from app.data.learning_units import (
    LEARNING_UNITS,
    LEARNING_UNITS_BY_SLUG,
    OPEN_QUESTIONS_BY_ID,
)
from app.data.question_bank import (
    FIRST_CHAPTER,
    PRACTICE_EXAMS,
    QUESTION_BANK,
    QUESTION_CATEGORIES,
)
from app.models.domain import (
    LearningUnit,
    OpenQuestion,
    PracticeExam,
    QuestionCategory,
    QuizQuestion,
)


class QuestionRepository:
    """Read-only repository for PAL-style practice content."""

    def list_categories(self) -> list[QuestionCategory]:
        """Return all question categories."""
        return QUESTION_CATEGORIES

    def list_learning_units(self, month: int | None = None) -> list[LearningUnit]:
        """Return learning units, optionally restricted to one curriculum month."""
        units = LEARNING_UNITS
        if month is not None:
            units = [unit for unit in units if unit.month == month]
        return sorted(units, key=lambda unit: (unit.month, unit.position))

    def get_learning_unit(self, slug: str) -> LearningUnit:
        """Return one learning unit or raise ``ValueError`` if it is unknown."""
        unit = LEARNING_UNITS_BY_SLUG.get(slug)
        if unit is None:
            raise ValueError(f"Unbekannte Lerneinheit: {slug}")
        return unit

    def list_open_questions(self, question_ids: list[str]) -> list[OpenQuestion]:
        """Return the open tasks for the given ids, skipping unknown ones."""
        return [
            OPEN_QUESTIONS_BY_ID[qid]
            for qid in question_ids
            if qid in OPEN_QUESTIONS_BY_ID
        ]

    def list_questions(
        self,
        category_slug: str | None = None,
        month: int | None = None,
    ) -> list[QuizQuestion]:
        """Return questions filtered by category or curriculum month."""
        questions = QUESTION_BANK
        if category_slug is not None:
            questions = [
                question
                for question in questions
                if question.category_slug == category_slug
            ]
        if month is not None:
            category_months = {
                category.slug: category.month for category in QUESTION_CATEGORIES
            }
            questions = [
                question
                for question in questions
                if category_months.get(question.category_slug) == month
            ]
        return questions

    def get_question(self, question_id: str) -> QuizQuestion | None:
        """Return one question by id or None when it does not exist."""
        return next(
            (
                question
                for question in QUESTION_BANK
                if question.question_id == question_id
            ),
            None,
        )

    def list_exams(self) -> list[PracticeExam]:
        """Return all practice exam definitions."""
        return PRACTICE_EXAMS

    def get_exam(self, exam_id: str) -> tuple[PracticeExam, list[QuizQuestion]] | None:
        """Return one practice exam with its questions."""
        exam = next((item for item in PRACTICE_EXAMS if item.exam_id == exam_id), None)
        if exam is None:
            return None
        question_map = {question.question_id: question for question in QUESTION_BANK}
        questions = [question_map[question_id] for question_id in exam.question_ids]
        return exam, questions

    def get_first_chapter(self) -> dict[str, object]:
        """Return the first chapter package for the MVP."""
        category_slugs = FIRST_CHAPTER["category_slugs"]
        categories = [
            category
            for category in QUESTION_CATEGORIES
            if category.slug in category_slugs
        ]
        return {
            "title": FIRST_CHAPTER["title"],
            "mission_goal": FIRST_CHAPTER["mission_goal"],
            "fachkunde": FIRST_CHAPTER["fachkunde"],
            "subchapters": categories,
            "checkpoint_exam_id": FIRST_CHAPTER["checkpoint_exam_id"],
        }
