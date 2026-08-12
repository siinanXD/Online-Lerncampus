"""API tests for server-side exam sessions."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.question_repository import QuestionRepository


def build_client() -> TestClient:
    """Create a test client for the application."""
    return TestClient(create_app())


def login_client(client: TestClient, identifier: str | None = None) -> dict[str, str]:
    """Log in and return authorization headers for protected endpoints."""
    login_identifier = identifier or f"test-azubi-{uuid4()}"
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": login_identifier,
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _correct_index(question_id: str) -> int:
    """Resolve the correct option from the server-side question bank."""
    question = QuestionRepository(content_source="memory").get_question(question_id)
    assert question is not None
    return question.correct_option_index


def test_exam_session_requires_authentication() -> None:
    """Ensure exam sessions are only available to logged-in learners."""
    client = build_client()
    response = client.post("/api/exams/exam-01/sessions")
    assert response.status_code == 401


def test_exam_session_lifecycle_grades_correct_answers() -> None:
    """Ensure a full exam session can be started, answered, and submitted."""
    client = build_client()
    headers = login_client(client)
    exam = client.get("/api/exams/exam-01").json()
    start = client.post("/api/exams/exam-01/sessions", headers=headers)
    assert start.status_code == 201
    payload = start.json()
    session_id = payload["session_id"]
    assert payload["status"] == "in_progress"
    assert payload["exam"]["exam_id"] == "exam-01"
    assert len(payload["exam"]["questions"]) == 10

    for question in exam["questions"]:
        save = client.post(
            f"/api/exams/sessions/{session_id}/answers",
            headers=headers,
            json={
                "question_id": question["question_id"],
                "selected_option_index": _correct_index(question["question_id"]),
            },
        )
        assert save.status_code == 200
        assert save.json()["saved"] is True

    submit = client.post(
        f"/api/exams/sessions/{session_id}/submit",
        headers=headers,
    )
    assert submit.status_code == 200
    result = submit.json()
    assert result["status"] == "submitted"
    assert result["choice_correct"] == 10
    assert result["choice_total"] == 10
    assert result["score_percent"] == 100.0
    assert result["passed"] is True
    assert result["weak_categories"] == []

    state = client.get(f"/api/exams/sessions/{session_id}", headers=headers)
    assert state.status_code == 200
    assert state.json()["status"] == "submitted"
    assert state.json()["passed"] is True


def test_exam_session_rejects_unknown_question() -> None:
    """Ensure answers must belong to the active exam."""
    client = build_client()
    headers = login_client(client)
    session_id = client.post(
        "/api/exams/exam-01/sessions",
        headers=headers,
    ).json()["session_id"]
    foreign_question = client.get("/api/exams/exam-02").json()["questions"][0]
    response = client.post(
        f"/api/exams/sessions/{session_id}/answers",
        headers=headers,
        json={
            "question_id": foreign_question["question_id"],
            "selected_option_index": 0,
        },
    )
    assert response.status_code == 400


def test_exam_session_cannot_be_submitted_twice() -> None:
    """Ensure submitted sessions reject further grading attempts."""
    client = build_client()
    headers = login_client(client)
    session_id = client.post(
        "/api/exams/exam-01/sessions",
        headers=headers,
    ).json()["session_id"]
    first = client.post(
        f"/api/exams/sessions/{session_id}/submit",
        headers=headers,
    )
    second = client.post(
        f"/api/exams/sessions/{session_id}/submit",
        headers=headers,
    )
    assert first.status_code == 200
    assert second.status_code == 400
