"""Tests for learning units, open exam tasks, and the checkpoint exam format."""

from fastapi.testclient import TestClient

from app.data.learning_units import LEARNING_UNITS, OPEN_QUESTIONS
from app.data.sources import TRUSTED_SOURCES
from app.main import app
from app.models.domain import AnswerFormat, ReviewStatus


def build_client() -> TestClient:
    """Return a test client for the FastAPI app."""
    return TestClient(app)


def test_every_learning_unit_cites_known_sources() -> None:
    """Content must only reference sources tracked in the source catalogue."""
    known = {source.key for source in TRUSTED_SOURCES}

    for unit in LEARNING_UNITS:
        assert unit.source_keys, f"{unit.slug} hat keine Quellenangabe"
        assert set(unit.source_keys) <= known, f"{unit.slug} zitiert unbekannte Quelle"


def test_learning_units_start_unapproved() -> None:
    """Generated content must not silently reach learners as approved."""
    assert all(unit.review_status is ReviewStatus.DRAFT for unit in LEARNING_UNITS)


def test_open_questions_cover_all_answer_formats() -> None:
    """The open exam part needs text, calculation, and sketch tasks."""
    formats = {question.answer_format for question in OPEN_QUESTIONS}

    assert formats == set(AnswerFormat)


def test_open_question_points_match_criteria() -> None:
    """``max_points`` must be the sum of the marking scheme."""
    for question in OPEN_QUESTIONS:
        assert question.criteria, f"{question.question_id} hat kein Bewertungsraster"
        expected = sum(criterion.points for criterion in question.criteria)
        assert question.max_points == expected


def test_learning_unit_endpoint_returns_theory_and_glossary() -> None:
    """The API exposes a full learning unit for the app."""
    client = build_client()
    response = client.get("/api/learning/units/messschieber")

    assert response.status_code == 200
    payload = response.json()
    assert payload["title"] == "Messschieber"
    assert len(payload["theory_blocks"]) >= 3
    assert "Nonius" in payload["glossary"]
    assert "DIN 862" in payload["theory_blocks"][0]["norm_references"]


def test_unknown_learning_unit_returns_404() -> None:
    """An unknown slug must not fall through to a server error."""
    client = build_client()

    assert client.get("/api/learning/units/gibt-es-nicht").status_code == 404


def test_learning_units_can_be_filtered_by_month() -> None:
    """The month filter narrows the unit list."""
    client = build_client()

    month_one = client.get("/api/learning/units?month=1").json()
    month_twenty_four = client.get("/api/learning/units?month=24").json()
    assert len(month_one) == 10
    assert len(month_twenty_four) == 2


def test_checkpoint_exam_hides_sample_solutions() -> None:
    """A learner must not be able to read the solution out of the payload."""
    client = build_client()
    response = client.get("/api/exams/checkpoint-01")

    assert response.status_code == 200
    payload = response.json()
    assert payload["is_checkpoint"] is True
    assert payload["time_limit_minutes"] == 120
    assert len(payload["questions"]) == 50
    assert len(payload["open_questions"]) == 15
    assert all(task["sample_solution"] is None for task in payload["open_questions"])
    assert all(task["max_points"] > 0 for task in payload["open_questions"])


def test_training_exams_have_no_open_tasks() -> None:
    """Short training exams stay pure single-choice."""
    client = build_client()
    payload = client.get("/api/exams/exam-01").json()

    assert payload["is_checkpoint"] is False
    assert payload["open_questions"] == []
    assert payload["time_limit_minutes"] == 0
