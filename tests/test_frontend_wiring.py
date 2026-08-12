"""Tests for gamification, coach plan, auth/me, consent, reset, open answers."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.question_repository import QuestionRepository


def build_client() -> TestClient:
    return TestClient(create_app())


def login(client: TestClient, identifier: str | None = None) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": identifier or f"azubi-{uuid4()}",
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _correct_index(question_id: str) -> int:
    question = QuestionRepository(content_source="memory").get_question(question_id)
    assert question is not None
    return question.correct_option_index


def test_auth_me_returns_profile() -> None:
    client = build_client()
    headers = login(client, f"azubi-{uuid4()}")
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["role"] == "learner"
    assert payload["learner_id"].startswith("learner_")


def test_progress_reset_clears_mastery() -> None:
    client = build_client()
    headers = login(client)
    question = client.get("/api/questions?month=1").json()[0]
    for _ in range(2):
        client.post(
            "/api/progress/attempt",
            headers=headers,
            json={
                "question_id": question["question_id"],
                "selected_option_index": _correct_index(question["question_id"]),
            },
        )
    before = client.get("/api/dashboard", headers=headers).json()
    assert before["mastered_questions"] >= 1
    reset = client.post("/api/progress/reset", headers=headers)
    assert reset.status_code == 204
    after = client.get("/api/dashboard", headers=headers).json()
    assert after["mastered_questions"] == 0
    assert after["answered_questions"] == 0


def test_gamification_and_coach_plan_endpoints() -> None:
    client = build_client()
    headers = login(client)
    question = client.get("/api/questions?month=1").json()[0]
    client.post(
        "/api/progress/attempt",
        headers=headers,
        json={
            "question_id": question["question_id"],
            "selected_option_index": _correct_index(question["question_id"]),
        },
    )
    gamification = client.get("/api/gamification", headers=headers)
    assert gamification.status_code == 200
    payload = gamification.json()
    assert payload["xp"] >= 10
    assert payload["level"] >= 1
    assert payload["streak_days"] >= 1
    assert "Erster Schritt" in payload["badges"]

    coach = client.get("/api/coach/plan", headers=headers)
    assert coach.status_code == 200
    plan = coach.json()
    assert plan["tips"]
    assert plan["focus_month"] >= 1
    dashboard = client.get("/api/dashboard", headers=headers).json()
    assert dashboard["streak_days"] >= 1
    assert dashboard["xp"] == payload["xp"]


def test_privacy_consent_endpoint() -> None:
    client = build_client()
    headers = login(client)
    response = client.post(
        "/api/privacy/consent",
        headers=headers,
        json={"accepted": True},
    )
    assert response.status_code == 200
    assert response.json()["accepted"] is True
    assert response.json()["consent_version"]


def test_checkpoint_exam_open_answer_can_be_saved() -> None:
    client = build_client()
    headers = login(client)
    exam = client.get("/api/exams/checkpoint-01").json()
    assert exam["open_questions"]
    start = client.post("/api/exams/checkpoint-01/sessions", headers=headers)
    assert start.status_code == 201
    session_id = start.json()["session_id"]
    open_question = exam["open_questions"][0]
    save = client.post(
        f"/api/exams/sessions/{session_id}/open-answers",
        headers=headers,
        json={
            "question_id": open_question["question_id"],
            "learner_answer": "Messschieber Nonius ablesen und dokumentieren.",
            "self_score": min(2, open_question["max_points"]),
        },
    )
    assert save.status_code == 200
    assert save.json()["saved"] is True


def test_occupations_modules_and_sources_are_wired() -> None:
    client = build_client()
    occupations = client.get("/api/occupations")
    assert occupations.status_code == 200
    assert occupations.json()
    slug = occupations.json()[0]["slug"]
    modules = client.get(f"/api/occupations/{slug}/modules")
    assert modules.status_code == 200
    sources = client.get("/api/sources")
    assert sources.status_code == 200
    assert sources.json()
