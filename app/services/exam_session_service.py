"""Exam session lifecycle: start, answer, submit, and grade."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

from app.services.database import Database, utc_now_iso
from app.services.question_repository import QuestionRepository


@dataclass(frozen=True)
class ExamSessionState:
    """Serializable exam session metadata."""

    session_id: int
    exam_id: str
    learner_id: str
    status: str
    started_at: str
    expires_at: str | None
    submitted_at: str | None
    score_percent: float | None
    passed: bool | None
    passing_score_percent: int
    time_limit_minutes: int


class ExamSessionService:
    """Manage timed exam attempts with server-side grading."""

    def __init__(
        self,
        database: Database,
        question_repository: QuestionRepository,
    ) -> None:
        """Wire persistence and content access."""
        self.database = database
        self.question_repository = question_repository

    def start_session(self, learner_id: str, exam_id: str) -> ExamSessionState:
        """Create a new in-progress exam session for one learner."""
        exam_result = self.question_repository.get_exam(exam_id)
        if exam_result is None:
            raise ValueError("Pruefung wurde nicht gefunden.")
        exam, _questions = exam_result
        practice_exam_id = self.database.get_practice_exam_id(exam_id)
        if practice_exam_id is None:
            raise ValueError("Pruefung wurde nicht gefunden.")
        expires_at = None
        if exam.time_limit_minutes > 0:
            expires_at = (
                datetime.now(tz=UTC) + timedelta(minutes=exam.time_limit_minutes)
            ).isoformat()
        session_id = self.database.create_exam_session(
            learner_id=learner_id,
            practice_exam_id=practice_exam_id,
            expires_at=expires_at,
        )
        self.database.record_audit_event(
            event_type="exam.start",
            learner_id=learner_id,
            metadata={"exam_id": exam_id, "session_id": session_id},
        )
        return ExamSessionState(
            session_id=session_id,
            exam_id=exam_id,
            learner_id=learner_id,
            status="in_progress",
            started_at=utc_now_iso(),
            expires_at=expires_at,
            submitted_at=None,
            score_percent=None,
            passed=None,
            passing_score_percent=exam.passing_score_percent,
            time_limit_minutes=exam.time_limit_minutes,
        )

    def get_session(self, learner_id: str, session_id: int) -> ExamSessionState:
        """Return one session after enforcing ownership and expiry."""
        row = self._require_session_row(learner_id, session_id)
        self._expire_if_needed(row)
        row = self.database.get_exam_session(session_id) or row
        return self._row_to_state(row)

    def record_choice_answer(
        self,
        learner_id: str,
        session_id: int,
        question_id: str,
        selected_option_index: int,
    ) -> dict[str, object]:
        """Store one single-choice answer without revealing the solution."""
        row = self._require_active_session(learner_id, session_id)
        exam_id = row["exam_public_id"]
        exam, questions = self._require_exam(exam_id)
        question = next((item for item in questions if item.question_id == question_id), None)
        if question is None:
            raise ValueError("Frage gehoert nicht zu dieser Pruefung.")
        if selected_option_index < 0 or selected_option_index >= len(question.options):
            raise ValueError("Antwortindex ist ungueltig.")
        quiz_pk = self.database.get_quiz_question_pk(question_id)
        if quiz_pk is None:
            raise ValueError("Frage wurde nicht gefunden.")
        is_correct = selected_option_index == question.correct_option_index
        self.database.save_exam_choice_answer(
            session_id=session_id,
            quiz_question_id=quiz_pk,
            selected_option_index=selected_option_index,
            is_correct=is_correct,
        )
        return {
            "question_id": question_id,
            "saved": True,
            "answered_count": self.database.count_exam_choice_answers(session_id),
            "total_choice_questions": len(questions),
        }

    def get_progress(
        self,
        learner_id: str,
        session_id: int,
        current_question_id: str | None = None,
    ) -> dict[str, object]:
        """Return live counts and per-question progress for one active session."""
        row = self._require_active_session(learner_id, session_id)
        exam_id = row["exam_public_id"]
        exam, questions = self._require_exam(exam_id)
        answers = self.database.list_exam_choice_answers_with_ids(session_id)
        answer_by_id = {item["question_id"]: item for item in answers}
        marked_ids = set(self.database.list_exam_marked_question_ids(session_id))
        resolved_current_id = current_question_id
        if not resolved_current_id:
            for question in questions:
                if question.question_id not in answer_by_id:
                    resolved_current_id = question.question_id
                    break
        if not resolved_current_id and questions:
            resolved_current_id = questions[-1].question_id
        current_index = 1
        current_prompt = None
        progress_items: list[dict[str, object]] = []
        for index, question in enumerate(questions, start=1):
            is_current = question.question_id == resolved_current_id
            if is_current:
                current_index = index
                current_prompt = question.prompt
            answer = answer_by_id.get(question.question_id)
            progress_items.append(
                {
                    "index": index,
                    "question_id": question.question_id,
                    "answered": question.question_id in answer_by_id,
                    "marked": question.question_id in marked_ids,
                    "is_current": is_current,
                    "selected_option_index": (
                        int(answer["selected_option_index"])
                        if answer and answer["selected_option_index"] is not None
                        else None
                    ),
                }
            )
        total = len(questions)
        answered_count = len(answer_by_id)
        return {
            "session_id": session_id,
            "exam_id": exam_id,
            "exam_title": exam.title,
            "expires_at": row["expires_at"],
            "total_questions": total,
            "answered_count": answered_count,
            "open_count": max(total - answered_count, 0),
            "marked_count": len(marked_ids),
            "current_index": current_index,
            "current_question_id": resolved_current_id,
            "current_prompt": current_prompt,
            "progress_percent": round((answered_count / total) * 100) if total else 0,
            "questions": progress_items,
        }

    def toggle_mark(
        self,
        learner_id: str,
        session_id: int,
        question_id: str,
    ) -> dict[str, object]:
        """Toggle the review mark for one exam question."""
        row = self._require_active_session(learner_id, session_id)
        exam_id = row["exam_public_id"]
        _exam, questions = self._require_exam(exam_id)
        if question_id not in {question.question_id for question in questions}:
            raise ValueError("Frage gehoert nicht zu dieser Pruefung.")
        quiz_pk = self.database.get_quiz_question_pk(question_id)
        if quiz_pk is None:
            raise ValueError("Frage wurde nicht gefunden.")
        marked = self.database.toggle_exam_mark(session_id, quiz_pk)
        return {
            "question_id": question_id,
            "marked": marked,
            "marked_count": self.database.count_exam_marks(session_id),
        }

    def record_open_answer(
        self,
        learner_id: str,
        session_id: int,
        question_id: str,
        learner_answer: str,
        self_score: int | None = None,
    ) -> dict[str, object]:
        """Store one open task answer and optional self-assessment."""
        row = self._require_active_session(learner_id, session_id)
        exam_id = row["exam_public_id"]
        exam, _questions = self._require_exam(exam_id)
        if question_id not in exam.open_question_ids:
            raise ValueError("Offene Aufgabe gehoert nicht zu dieser Pruefung.")
        open_questions = self.question_repository.list_open_questions(exam.open_question_ids)
        open_question = next(
            (item for item in open_questions if item.question_id == question_id),
            None,
        )
        if open_question is None:
            raise ValueError("Offene Aufgabe wurde nicht gefunden.")
        if self_score is not None and (
            self_score < 0 or self_score > open_question.max_points
        ):
            raise ValueError("Selbsteinschaetzung liegt ausserhalb der Punktespanne.")
        open_pk = self.database.get_open_question_pk(question_id)
        if open_pk is None:
            raise ValueError("Offene Aufgabe wurde nicht gefunden.")
        self.database.save_exam_open_answer(
            session_id=session_id,
            open_question_id=open_pk,
            learner_answer=learner_answer.strip(),
            self_score=self_score,
        )
        return {
            "question_id": question_id,
            "saved": True,
            "max_points": open_question.max_points,
        }

    def submit_session(self, learner_id: str, session_id: int) -> dict[str, object]:
        """Grade a session and mark it submitted."""
        row = self._require_active_session(learner_id, session_id)
        exam_id = row["exam_public_id"]
        exam, questions = self._require_exam(exam_id)
        choice_answers = self.database.list_exam_choice_answers(session_id)
        open_answers = self.database.list_exam_open_answers(session_id)
        choice_score = sum(1 for item in choice_answers if item["is_correct"])
        choice_total = len(questions)
        wrong_count = sum(1 for item in choice_answers if not item["is_correct"])
        unanswered_count = max(choice_total - len(choice_answers), 0)
        started_at = datetime.fromisoformat(row["started_at"])
        duration_seconds = max(0, int((datetime.now(tz=UTC) - started_at).total_seconds()))
        open_questions = self.question_repository.list_open_questions(exam.open_question_ids)
        open_max = sum(question.max_points for question in open_questions)
        open_score = sum(
            item["self_score"] or 0
            for item in open_answers
            if item["self_score"] is not None
        )
        if open_max > 0:
            total_points = choice_total + open_max
            earned = choice_score + open_score
        else:
            total_points = choice_total
            earned = choice_score
        score_percent = round((earned / total_points) * 100, 1) if total_points else 0.0
        passed = score_percent >= exam.passing_score_percent
        xp_awarded = 200 if passed else 50
        self.database.finalize_exam_session(
            session_id=session_id,
            score_percent=score_percent,
            passed=passed,
        )
        self.database.record_audit_event(
            event_type="exam.submit",
            learner_id=learner_id,
            metadata={
                "exam_id": exam_id,
                "session_id": session_id,
                "score_percent": score_percent,
                "passed": passed,
            },
        )
        category_stats = self._weak_categories_from_answers(questions, choice_answers)
        return {
            "session_id": session_id,
            "exam_id": exam_id,
            "exam_title": exam.title,
            "status": "submitted",
            "score_percent": score_percent,
            "passed": passed,
            "passing_score_percent": exam.passing_score_percent,
            "choice_correct": choice_score,
            "choice_total": choice_total,
            "wrong_count": wrong_count,
            "unanswered_count": unanswered_count,
            "duration_seconds": duration_seconds,
            "xp_awarded": xp_awarded,
            "open_score": open_score,
            "open_max_points": open_max,
            "weak_categories": category_stats["weak_categories"],
            "category_breakdown": category_stats["category_breakdown"],
        }

    def _weak_categories_from_answers(
        self,
        questions: list[Any],
        choice_answers: list[dict[str, Any]],
    ) -> list[dict[str, object]]:
        answer_by_pk = {item["quiz_question_id"]: item for item in choice_answers}
        stats: dict[str, dict[str, int]] = {}
        for question in questions:
            slug = question.category_slug
            bucket = stats.setdefault(
                slug,
                {"total_count": 0, "wrong_count": 0},
            )
            bucket["total_count"] += 1
            pk = self.database.get_quiz_question_pk(question.question_id)
            if pk is None:
                bucket["wrong_count"] += 1
                continue
            answer = answer_by_pk.get(pk)
            if answer is None or not answer["is_correct"]:
                bucket["wrong_count"] += 1
        rows: list[dict[str, object]] = []
        for slug, data in stats.items():
            total = data["total_count"]
            wrong = data["wrong_count"]
            correct = max(total - wrong, 0)
            percent = round((correct / total) * 100) if total else 0
            rows.append(
                {
                    "category_slug": slug,
                    "wrong_count": wrong,
                    "total_count": total,
                    "correct_count": correct,
                    "percent": percent,
                }
            )
        rows.sort(key=lambda item: (int(item["percent"]), -int(item["wrong_count"])))
        return {
            "category_breakdown": rows[:5],
            "weak_categories": [row for row in rows if int(row["wrong_count"]) > 0][:5],
        }

    def _require_exam(self, exam_id: str):
        result = self.question_repository.get_exam(exam_id)
        if result is None:
            raise ValueError("Pruefung wurde nicht gefunden.")
        return result

    def _require_session_row(self, learner_id: str, session_id: int) -> dict[str, Any]:
        row = self.database.get_exam_session(session_id)
        if row is None:
            raise ValueError("Pruefungssession wurde nicht gefunden.")
        if row["learner_id"] != learner_id:
            raise ValueError("Pruefungssession gehoert nicht zum angemeldeten Azubi.")
        return row

    def _require_active_session(self, learner_id: str, session_id: int) -> dict[str, Any]:
        row = self._require_session_row(learner_id, session_id)
        self._expire_if_needed(row)
        row = self.database.get_exam_session(session_id) or row
        if row["status"] != "in_progress":
            raise ValueError("Diese Pruefungssession ist bereits abgeschlossen.")
        if row["expires_at"]:
            expires_at = datetime.fromisoformat(row["expires_at"])
            if expires_at <= datetime.now(tz=UTC):
                self.database.mark_exam_session_expired(session_id)
                raise ValueError("Die Pruefungszeit ist abgelaufen.")
        return row

    def _expire_if_needed(self, row: dict[str, Any]) -> None:
        if row["status"] != "in_progress" or not row["expires_at"]:
            return
        expires_at = datetime.fromisoformat(row["expires_at"])
        if expires_at <= datetime.now(tz=UTC):
            self.database.mark_exam_session_expired(int(row["id"]))

    def _row_to_state(self, row: dict[str, Any]) -> ExamSessionState:
        return ExamSessionState(
            session_id=int(row["id"]),
            exam_id=row["exam_public_id"],
            learner_id=row["learner_id"],
            status=row["status"],
            started_at=row["started_at"],
            expires_at=row["expires_at"],
            submitted_at=row["submitted_at"],
            score_percent=row["score_percent"],
            passed=bool(row["passed"]) if row["passed"] is not None else None,
            passing_score_percent=row["passing_score_percent"],
            time_limit_minutes=row["time_limit_minutes"],
        )
