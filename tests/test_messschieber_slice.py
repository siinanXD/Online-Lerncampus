"""Vertical slice: Messschieber unit → attempt → dashboard continue."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.progress_service import PILOT_CONTINUE_UNIT_SLUG
from tests.conftest import correct_option_index as _correct_index


def build_client() -> TestClient:
    return TestClient(create_app())


def login(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": f"azubi-{uuid4()}",
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_dashboard_continue_prefers_messschieber_pilot() -> None:
    client = build_client()
    headers = login(client)

    dashboard = client.get("/api/dashboard", headers=headers)
    assert dashboard.status_code == 200
    payload = dashboard.json()
    assert payload["continue_slug"] == PILOT_CONTINUE_UNIT_SLUG
    assert payload["continue_title"] == "Messschieber"
    assert payload["continue_category_slug"] == "m06-messschieber"
    assert payload["continue_total"] >= 1
    assert payload["continue_answered"] == 0


def test_messschieber_attempt_updates_dashboard_continue() -> None:
    client = build_client()
    headers = login(client)

    unit = client.get("/api/learning/units/messschieber")
    assert unit.status_code == 200
    assert unit.json()["slug"] == "messschieber"
    assert "m06-messschieber" in unit.json()["category_slugs"]

    questions = client.get("/api/questions?category_slug=m06-messschieber")
    assert questions.status_code == 200
    pool = questions.json()
    assert len(pool) >= 1
    question = pool[0]
    question_id = question["question_id"]

    before = client.get("/api/dashboard", headers=headers).json()
    assert before["continue_answered"] == 0

    for _ in range(2):
        attempt = client.post(
            "/api/progress/attempt",
            headers=headers,
            json={
                "question_id": question_id,
                "selected_option_index": _correct_index(question_id),
            },
        )
        assert attempt.status_code == 200
        body = attempt.json()
        assert body["is_correct"] is True
        assert body["xp"] >= 10

    after_attempt = client.get("/api/dashboard", headers=headers).json()
    assert after_attempt["continue_answered"] >= 1
    assert after_attempt["answered_questions"] >= 1
    assert after_attempt["mastered_questions"] >= 1
    assert after_attempt["xp"] > before["xp"]
    assert after_attempt["continue_slug"] == PILOT_CONTINUE_UNIT_SLUG

    complete = client.post(
        "/api/learning/units/messschieber/complete",
        headers=headers,
    )
    assert complete.status_code == 200

    after_complete = client.get("/api/dashboard", headers=headers).json()
    assert after_complete["continue_slug"] == "toleranzen-pruefen"
    assert after_complete["units_completed"] >= 1
