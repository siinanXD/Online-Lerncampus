"""Vertical slice: Toleranzfeld continues after Messschieber."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from app.services.progress_service import PILOT_CONTINUE_UNIT_SLUGS
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


def test_pilot_continue_order_is_messschieber_then_toleranz() -> None:
    assert PILOT_CONTINUE_UNIT_SLUGS[:2] == ("messschieber", "toleranzen-pruefen")


def test_after_messschieber_complete_continue_is_toleranz() -> None:
    client = build_client()
    headers = login(client)

    before = client.get("/api/dashboard", headers=headers).json()
    assert before["continue_slug"] == "messschieber"

    complete = client.post(
        "/api/learning/units/messschieber/complete",
        headers=headers,
    )
    assert complete.status_code == 200

    after = client.get("/api/dashboard", headers=headers).json()
    assert after["continue_slug"] == "toleranzen-pruefen"
    assert after["continue_title"] == "Toleranzen pruefen"
    assert after["continue_category_slug"] == "m06-toleranzen-pruefen"
    assert after["continue_answered"] == 0
    assert after["continue_total"] >= 1


def test_toleranz_unit_and_questions_are_wired() -> None:
    client = build_client()
    unit = client.get("/api/learning/units/toleranzen-pruefen")
    assert unit.status_code == 200
    payload = unit.json()
    assert payload["slug"] == "toleranzen-pruefen"
    assert "m06-toleranzen-pruefen" in payload["category_slugs"]
    assert payload["review_status"] in {"draft", "approved", "source_checked"}

    questions = client.get("/api/questions?category_slug=m06-toleranzen-pruefen")
    assert questions.status_code == 200
    assert len(questions.json()) >= 1


def test_toleranz_attempt_updates_dashboard_continue() -> None:
    client = build_client()
    headers = login(client)

    assert (
        client.post(
            "/api/learning/units/messschieber/complete",
            headers=headers,
        ).status_code
        == 200
    )

    questions = client.get("/api/questions?category_slug=m06-toleranzen-pruefen").json()
    question_id = questions[0]["question_id"]
    before = client.get("/api/dashboard", headers=headers).json()
    assert before["continue_slug"] == "toleranzen-pruefen"
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
        assert attempt.json()["is_correct"] is True

    after = client.get("/api/dashboard", headers=headers).json()
    assert after["continue_slug"] == "toleranzen-pruefen"
    assert after["continue_answered"] >= 1
    assert after["mastered_questions"] >= 1
    assert after["xp"] > before["xp"]

    complete = client.post(
        "/api/learning/units/toleranzen-pruefen/complete",
        headers=headers,
    )
    assert complete.status_code == 200
    done = client.get("/api/dashboard", headers=headers).json()
    assert done["continue_slug"] not in {"messschieber", "toleranzen-pruefen"}


def test_draft_units_hidden_when_review_required(
    monkeypatch,
    tmp_path,
) -> None:
    """CONTENT_REVIEW_REQUIRED must hide draft pilot units from learners."""
    from app.core.config import get_settings
    import app.api.routes as routes

    db_path = tmp_path / "review-required.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path.as_posix()}")
    monkeypatch.setenv("CONTENT_SOURCE", "db")
    monkeypatch.setenv("CONTENT_REVIEW_REQUIRED", "true")
    monkeypatch.setenv("CONTENT_SEED_FORMAT", "python")
    monkeypatch.setenv("CONTENT_SEED_ON_STARTUP", "true")
    get_settings.cache_clear()
    routes.database = None
    routes.auth_service = None
    routes.question_repository = None
    routes.progress_service = None
    routes.exam_session_service = None

    client = TestClient(create_app())
    headers = login(client)

    units = client.get("/api/learning/units").json()
    slugs = {unit["slug"] for unit in units}
    assert "messschieber" not in slugs
    assert "toleranzen-pruefen" not in slugs

    assert client.get("/api/learning/units/messschieber").status_code == 404
    assert client.get("/api/learning/units/toleranzen-pruefen").status_code == 404

    dashboard = client.get("/api/dashboard", headers=headers).json()
    assert dashboard["continue_slug"] not in {"messschieber", "toleranzen-pruefen"}

    questions = client.get("/api/questions?category_slug=m06-toleranzen-pruefen").json()
    assert questions == []
