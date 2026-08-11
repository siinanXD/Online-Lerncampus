"""Tests for question categories and practice exams."""

from app.services.question_repository import QuestionRepository


def test_question_categories_cover_24_months_with_10_subchapters() -> None:
    """Ensure every curriculum month has ten question categories."""
    repository = QuestionRepository()
    categories = repository.list_categories()

    assert len(categories) == 240
    assert len([category for category in categories if category.month == 1]) == 10
    assert len([category for category in categories if category.month == 24]) == 10


def test_practice_exam_count_and_size() -> None:
    """Ensure twenty practice exams with ten questions are available."""
    repository = QuestionRepository()
    exams = repository.list_exams()

    assert len(exams) == 20
    assert all(len(exam.question_ids) == 10 for exam in exams)


def test_first_chapter_has_checkpoint_exam() -> None:
    """Ensure the first chapter contains ten subchapters and an exam id."""
    repository = QuestionRepository()
    chapter = repository.get_first_chapter()

    assert len(chapter["subchapters"]) == 10
    assert chapter["checkpoint_exam_id"] == "exam-01"


def test_questions_have_five_options() -> None:
    """Ensure generated questions use the PAL-like five-option structure."""
    repository = QuestionRepository()
    questions = repository.list_questions(month=1)

    assert len(questions) == 10
    assert all(len(question.options) == 5 for question in questions)
