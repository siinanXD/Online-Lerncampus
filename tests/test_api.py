"""API tests for the FastAPI application."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


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


def test_health_endpoint() -> None:
    """Ensure the health endpoint returns an ok status."""
    client = build_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_page_routes_return_app_shell() -> None:
    """Ensure browser page routes are directly reachable."""
    client = build_client()
    page_routes = [
        "/",
        "/funktionen",
        "/login",
        "/dashboard",
        "/lernreise",
        "/lernen",
        "/pruefungen",
        "/defizite",
        "/review",
        "/datenschutz",
    ]

    for page_route in page_routes:
        response = client.get(page_route)

        assert response.status_code == 200
        assert "BZE Online Campus" in response.text


def test_unknown_frontend_route_returns_404() -> None:
    """Ensure unknown frontend routes do not silently return the app shell."""
    client = build_client()
    response = client.get("/unbekannte-seite")

    assert response.status_code == 404


def test_curriculum_endpoint_returns_24_months() -> None:
    """Ensure the curriculum endpoint returns the full roadmap."""
    client = build_client()
    response = client.get("/api/occupations/maschinen-und-anlagenfuehrer/curriculum")

    assert response.status_code == 200
    assert len(response.json()) == 24


def test_generate_content_endpoint() -> None:
    """Ensure the generation endpoint returns a draft mission."""
    client = build_client()
    response = client.post(
        "/api/content/generate",
        json={
            "occupation_slug": "maschinen-und-anlagenfuehrer",
            "specialization_slug": "metall-und-kunststofftechnik",
            "month": 8,
            "learner_level": "azubi",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Mission 08: Pneumatik Grundlagen"
    assert payload["review_status"] == "draft"


def test_generate_content_endpoint_rejects_unknown_month() -> None:
    """Ensure invalid generation context returns a client error."""
    client = build_client()
    response = client.post(
        "/api/content/generate",
        json={
            "occupation_slug": "maschinen-und-anlagenfuehrer",
            "month": 25,
            "learner_level": "azubi",
        },
    )

    assert response.status_code == 400


def test_first_chapter_endpoint() -> None:
    """Ensure the learning endpoint returns the first chapter package."""
    client = build_client()
    response = client.get("/api/learning/first-chapter")

    assert response.status_code == 200
    payload = response.json()
    assert payload["checkpoint_exam_id"] == "exam-01"
    assert len(payload["subchapters"]) == 10


def test_login_endpoint_returns_pseudonymous_session() -> None:
    """Ensure login returns a token and pseudonymous learner id."""
    client = build_client()
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": f"azubi-test-{uuid4()}",
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["learner_id"].startswith("learner_")
    assert payload["display_name"] == "Azubi"
    assert payload["role"] == "learner"


def test_dashboard_requires_authentication() -> None:
    """Ensure private learning metrics require a bearer token."""
    client = build_client()
    response = client.get("/api/dashboard")

    assert response.status_code == 401


def test_dashboard_endpoint_returns_mastery_rule() -> None:
    """Ensure the dashboard exposes the learning rule and counters."""
    client = build_client()
    headers = login_client(client)
    response = client.get("/api/dashboard", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert (
        payload["mastery_rule"]
        == "1x beantworten und 2x hintereinander richtig loesen"
    )
    assert payload["mastered_questions"] == 0
    assert payload["total_questions"] >= 120


def test_learning_journey_endpoint_returns_24_months() -> None:
    """Ensure the authenticated learning journey covers the full training time."""
    client = build_client()
    headers = login_client(client)
    response = client.get("/api/learning/journey", headers=headers)

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 24
    assert payload[11]["checkpoint"] is True
    assert payload[23]["checkpoint"] is True


def test_progress_attempt_requires_two_correct_answers_for_mastery() -> None:
    """Ensure questions are mastered after two consecutive correct answers."""
    client = build_client()
    headers = login_client(client)
    question = client.get("/api/questions?month=1").json()[0]
    attempt_payload = {
        "question_id": question["question_id"],
        "selected_option_index": question["correct_option_index"],
    }

    first_attempt = client.post(
        "/api/progress/attempt",
        headers=headers,
        json=attempt_payload,
    )
    second_attempt = client.post(
        "/api/progress/attempt",
        headers=headers,
        json=attempt_payload,
    )

    assert first_attempt.status_code == 200
    assert first_attempt.json()["mastered"] is False
    assert second_attempt.status_code == 200
    assert second_attempt.json()["mastered"] is True


def test_privacy_export_contains_progress_and_consent() -> None:
    """Ensure learners can export profile, progress, and consent events."""
    client = build_client()
    headers = login_client(client)
    question = client.get("/api/questions?month=1").json()[0]
    client.post(
        "/api/privacy/consent",
        headers=headers,
        json={"accepted": True},
    )
    client.post(
        "/api/progress/attempt",
        headers=headers,
        json={
            "question_id": question["question_id"],
            "selected_option_index": question["correct_option_index"],
        },
    )

    response = client.get("/api/privacy/export", headers=headers)

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["learner"]["learner_id"].startswith("learner_")
    assert len(data["question_progress"]) == 1
    assert len(data["consents"]) == 1


def test_logout_revokes_session() -> None:
    """Ensure logout makes a token unusable."""
    client = build_client()
    headers = login_client(client)
    logout_response = client.post("/api/auth/logout", headers=headers)
    dashboard_response = client.get("/api/dashboard", headers=headers)

    assert logout_response.status_code == 200
    assert logout_response.json() == {"success": True}
    assert dashboard_response.status_code == 401


def test_delete_account_removes_private_data() -> None:
    """Ensure account deletion removes the learner and invalidates access."""
    client = build_client()
    headers = login_client(client)
    delete_response = client.delete("/api/privacy/account", headers=headers)
    export_response = client.get("/api/privacy/export", headers=headers)

    assert delete_response.status_code == 200
    assert delete_response.json() == {"deleted": True}
    assert export_response.status_code == 401


def test_exams_endpoint_returns_twenty_exams() -> None:
    """Ensure the API exposes twenty test exams."""
    client = build_client()
    response = client.get("/api/exams")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 20
    assert all(len(exam["questions"]) == 10 for exam in payload)
