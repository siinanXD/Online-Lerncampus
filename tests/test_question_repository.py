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
    """Ensure twenty short training exams with ten questions are available."""
    repository = QuestionRepository()
    training = [e for e in repository.list_exams() if not e.is_checkpoint]

    assert len(training) == 20
    assert all(len(exam.question_ids) == 10 for exam in training)


def test_checkpoint_exams_match_written_exam_format() -> None:
    """Checkpoints carry 50 bound plus 15 open tasks and a time limit."""
    repository = QuestionRepository()
    checkpoints = [e for e in repository.list_exams() if e.is_checkpoint]

    assert checkpoints, "no checkpoint exams were built"
    for exam in checkpoints:
        assert len(exam.question_ids) == 50
        assert len(exam.open_question_ids) == 15
        assert exam.time_limit_minutes == 120


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

    assert len(questions) == 20
    assert all(len(question.options) == 5 for question in questions)


def test_question_bank_covers_all_months() -> None:
    """Ensure every curriculum month has authored quiz questions."""
    repository = QuestionRepository()

    assert len(repository.list_questions()) == 480
