"""API tests for the FastAPI application."""

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


def test_health_endpoint() -> None:
    """Ensure the health endpoint returns an ok status."""
    client = build_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_page_routes_return_app_shell() -> None:
    """Ensure every allowlisted browser page route serves the SPA shell."""
    from app.web.pages import allowed_frontend_pages

    client = build_client()
    pages = allowed_frontend_pages()
    assert len(pages) >= 100

    for page in sorted(pages):
        page_route = "/" if page == "" else f"/{page}"
        response = client.get(page_route)
        assert response.status_code == 200, page_route
        assert "BZE Online Campus" in response.text


def test_figma_screen_allowlist_is_wired() -> None:
    """Ensure the generated Figma allowlist is loaded by the app."""
    from app.web.pages import allowed_frontend_pages

    pages = allowed_frontend_pages()
    assert "" in pages
    assert "ausbilder" in pages
    assert "admin/nutzer" in pages
    assert "lernen/formeltrainer" in pages
    assert len(pages) >= 100


def test_route_config_matches_page_allowlist() -> None:
    """Ensure screens.js routeConfig keys stay in sync with allowed_pages.json."""
    import json
    import re
    from pathlib import Path

    from app.web.pages import allowed_frontend_pages

    screens_js = Path("app/web/static/screens.js").read_text(encoding="utf-8")
    route_keys = re.findall(r'^\s*"(/[^"]*)"\s*:', screens_js, re.M)
    route_paths = {"" if key == "/" else key.lstrip("/") for key in route_keys}
    allowed = allowed_frontend_pages()

    assert route_paths == allowed
    assert json.loads(Path("app/web/allowed_pages.json").read_text(encoding="utf-8")) == sorted(
        allowed
    )


def test_frontend_api_calls_have_backend_routes() -> None:
    """Ensure every fetchJson /api call in static JS maps to a FastAPI route."""
    import re
    from pathlib import Path

    from app.api.routes import api_router

    backend: set[tuple[str, str]] = set()
    for route in api_router.routes:
        methods = getattr(route, "methods", None) or set()
        path = getattr(route, "path", None)
        if not path:
            continue
        for method in methods:
            if method in {"HEAD", "OPTIONS"}:
                continue
            backend.add((method.upper(), f"/api{path}"))

    calls: set[tuple[str, str]] = set()
    for js_path in Path("app/web/static").glob("*.js"):
        text = js_path.read_text(encoding="utf-8")
        for match in re.finditer(r"fetchJson\s*\(", text):
            start = match.end()
            depth = 1
            end = start
            while end < len(text) and depth:
                if text[end] == "(":
                    depth += 1
                elif text[end] == ")":
                    depth -= 1
                end += 1
            window = text[start:end]
            url_match = re.search(r"""(?:`|"|')(/api/[^`'"]+)(?:`|"|')""", window)
            if not url_match:
                continue
            method_match = re.search(r"""method:\s*['"](\w+)""", window)
            method = (method_match.group(1) if method_match else "GET").upper()
            raw = url_match.group(1).split("?", 1)[0]
            normalized = re.sub(r"\$\{[^}]+\}", "{param}", raw)
            calls.add((method, normalized))

    assert calls, "expected frontend API calls"

    def parts_match(front: str, back: str) -> bool:
        front_parts = front.split("/")
        back_parts = back.split("/")
        if len(front_parts) != len(back_parts):
            return False
        for fp, bp in zip(front_parts, back_parts):
            if fp == bp or fp.startswith("{") or bp.startswith("{"):
                continue
            return False
        return True

    missing = [
        f"{method} {url}"
        for method, url in sorted(calls)
        if not any(bm == method and parts_match(url, bu) for bm, bu in backend)
    ]
    assert not missing, f"frontend API calls without backend routes: {missing}"


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


def _correct_index(question_id: str) -> int:
    """Resolve the correct option from the server-side question bank."""
    question = QuestionRepository().get_question(question_id)
    assert question is not None
    return question.correct_option_index


def test_questions_do_not_leak_solutions() -> None:
    """Learner-facing question lists must not expose solution fields."""
    client = build_client()
    payload = client.get("/api/questions?month=1").json()
    assert payload
    assert "correct_option_index" not in payload[0]
    assert "explanation" not in payload[0]


def test_progress_attempt_requires_two_correct_answers_for_mastery() -> None:
    """Ensure questions are mastered after two consecutive correct answers."""
    client = build_client()
    headers = login_client(client)
    question = client.get("/api/questions?month=1").json()[0]
    attempt_payload = {
        "question_id": question["question_id"],
        "selected_option_index": _correct_index(question["question_id"]),
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
            "selected_option_index": _correct_index(question["question_id"]),
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


def test_exams_endpoint_returns_twenty_training_exams() -> None:
    """Ensure the API exposes the twenty short training exams."""
    client = build_client()
    response = client.get("/api/exams")

    assert response.status_code == 200
    payload = response.json()
    training = [exam for exam in payload if exam["exam_id"].startswith("exam-")]
    assert len(training) == 20
    assert all(len(exam["questions"]) == 10 for exam in training)
