"""Learner progress tracking for questions, exams, and dashboard metrics."""

from dataclasses import dataclass
from typing import Any

from app.models.domain import QuizQuestion
from app.services.question_repository import QuestionRepository


@dataclass
class QuestionProgress:
    """Mutable progress state for one learner question."""

    question_id: str
    answered_count: int = 0
    wrong_count: int = 0
    correct_streak: int = 0
    mastered: bool = False
    last_selected_option_index: int | None = None


class ProgressService:
    """Track question attempts and derive dashboard summaries."""

    def __init__(
        self,
        question_repository: QuestionRepository,
        database: Any,
    ) -> None:
        """Initialize progress storage for learners."""
        self.question_repository = question_repository
        self.database = database

    def record_attempt(
        self,
        learner_id: str,
        question_id: str,
        selected_option_index: int,
    ) -> tuple[QuestionProgress, QuizQuestion, bool]:
        """Record one answer attempt and update mastery state."""
        question = self.question_repository.get_question(question_id)
        if question is None:
            raise ValueError("Frage wurde nicht gefunden.")
        if selected_option_index < 0 or selected_option_index >= len(question.options):
            raise ValueError("Antwortindex ist ungueltig.")
        progress = self.database.get_question_progress(
            learner_id=learner_id,
            question_id=question_id,
        ) or QuestionProgress(question_id=question_id)
        is_correct = selected_option_index == question.correct_option_index
        if progress.mastered and not is_correct:
            progress.mastered = False
            progress.correct_streak = 0
        progress.answered_count += 1
        progress.last_selected_option_index = selected_option_index
        if is_correct:
            progress.correct_streak += 1
        else:
            progress.wrong_count += 1
            progress.correct_streak = 0
        progress.mastered = (
            progress.answered_count >= 1 and progress.correct_streak >= 2
        )
        self.database.save_question_progress(
            learner_id=learner_id,
            progress=progress,
        )
        self.database.record_audit_event(
            event_type="progress.attempt",
            learner_id=learner_id,
            metadata={
                "question_id": question_id,
                "is_correct": is_correct,
                "mastered": progress.mastered,
            },
        )
        return progress, question, is_correct

    def get_question_progress(
        self,
        learner_id: str,
        question_id: str,
    ) -> QuestionProgress:
        """Return progress for a question, creating an empty state when needed."""
        return self.database.get_question_progress(
            learner_id=learner_id,
            question_id=question_id,
        ) or QuestionProgress(question_id=question_id)

    def dashboard_summary(self, learner_id: str) -> dict[str, object]:
        """Return dashboard metrics for one learner."""
        learner_progress = self.database.list_question_progress(learner_id)
        questions = self.question_repository.list_questions()
        total_questions = len(questions)
        answered = sum(
            1 for item in learner_progress.values() if item.answered_count > 0
        )
        mastered = sum(1 for item in learner_progress.values() if item.mastered)
        wrong = sum(item.wrong_count for item in learner_progress.values())
        xp = max(0, answered * 10 + mastered * 25 - wrong * 3)
        level = 1 + xp // 120
        weak_categories = self._weak_categories(learner_progress)
        return {
            "learner_id": learner_id,
            "answered_questions": answered,
            "mastered_questions": mastered,
            "total_questions": total_questions,
            "wrong_answers": wrong,
            "xp": xp,
            "level": level,
            "mastery_rule": "1x beantworten und 2x hintereinander richtig loesen",
            "weak_categories": weak_categories,
        }

    def learning_journey(self, learner_id: str) -> list[dict[str, object]]:
        """Return month-by-month journey state for one learner."""
        learner_progress = self.database.list_question_progress(learner_id)
        categories = self.question_repository.list_categories()
        questions = self.question_repository.list_questions()
        category_to_question = {
            question.category_slug: question.question_id for question in questions
        }
        months: list[dict[str, object]] = []
        for month_number in range(1, 25):
            month_categories = [
                category for category in categories if category.month == month_number
            ]
            mastered_count = 0
            for category in month_categories:
                question_id = category_to_question.get(category.slug)
                if question_id and learner_progress.get(question_id, None):
                    mastered_count += int(learner_progress[question_id].mastered)
            total = len(month_categories)
            months.append(
                {
                    "month": month_number,
                    "title": month_categories[0].chapter_title,
                    "completed_categories": mastered_count,
                    "total_categories": total,
                    "locked": month_number > 1 and mastered_count == 0,
                    "checkpoint": month_number in (12, 24),
                }
            )
        return months

    def reset(self, learner_id: str) -> None:
        """Delete all progress for one learner."""
        self.database.reset_progress(learner_id)
        self.database.record_audit_event(
            event_type="progress.reset",
            learner_id=learner_id,
        )

    def export_learner_data(self, learner_id: str) -> dict[str, object]:
        """Return learner data with derived dashboard and journey state."""
        export = self.database.export_learner_data(learner_id)
        export["dashboard"] = self.dashboard_summary(learner_id)
        export["learning_journey"] = self.learning_journey(learner_id)
        return export

    def delete_learner_data(self, learner_id: str) -> None:
        """Delete learner-owned data from persistence."""
        self.database.record_audit_event(
            event_type="privacy.delete_requested",
            learner_id=learner_id,
        )
        self.database.delete_learner_data(learner_id)

    def _weak_categories(
        self,
        learner_progress: dict[str, QuestionProgress],
    ) -> list[dict[str, object]]:
        """Return categories with the highest wrong-answer count."""
        questions = {
            question.question_id: question
            for question in self.question_repository.list_questions()
        }
        category_counts: dict[str, int] = {}
        for question_id, progress in learner_progress.items():
            if progress.wrong_count <= 0:
                continue
            question = questions.get(question_id)
            if question is None:
                continue
            category_counts[question.category_slug] = (
                category_counts.get(question.category_slug, 0) + progress.wrong_count
            )
        return [
            {"category_slug": category_slug, "wrong_count": wrong_count}
            for category_slug, wrong_count in sorted(
                category_counts.items(),
                key=lambda item: item[1],
                reverse=True,
            )[:5]
        ]
