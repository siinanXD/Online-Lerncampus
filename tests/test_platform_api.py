"""Tests for platform APIs: tools, preferences, trainer and admin."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import staff_login


def build_client() -> TestClient:
    return TestClient(create_app())


def login(client: TestClient, identifier: str | None = None, role_prefix: str = "azubi") -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": identifier or f"{role_prefix}-{uuid4()}",
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_formulas_and_diagnosis_are_seeded() -> None:
    client = build_client()
    formulas = client.get("/api/formulas")
    assert formulas.status_code == 200
    payload = formulas.json()
    assert len(payload) == 24
    assert payload[0]["expression"]
    assert payload[0]["legend"]

    pneumatik = client.get("/api/formulas?topic=pneumatik").json()
    assert pneumatik
    assert all(item["topic"] == "pneumatik" for item in pneumatik)

    diagnosis = client.get("/api/diagnosis").json()
    assert len(diagnosis) == 8
    assert diagnosis[0]["correct_option_index"] is None
    assert diagnosis[0]["explanation"] is None


def test_learner_tools_persist_progress() -> None:
    client = build_client()
    headers = login(client)
    slug = client.get("/api/formulas").json()[0]["slug"]
    practice = client.post(
        f"/api/formulas/{slug}/practice",
        headers=headers,
        json={"correct": True},
    )
    assert practice.status_code == 200
    assert practice.json()["saved"] is True

    case = client.get("/api/diagnosis", headers=headers).json()[0]
    solve = client.post(
        f"/api/diagnosis/{case['slug']}/solve",
        headers=headers,
        json={"selected_option_index": 0},
    )
    assert solve.status_code == 200
    after = client.get("/api/diagnosis", headers=headers).json()
    solved = next(item for item in after if item["slug"] == case["slug"])
    if solve.json()["is_correct"]:
        assert solved["solved"] is True
        assert solved["explanation"]

    videos = client.get("/api/videos", headers=headers).json()
    assert videos
    watch = client.post(
        f"/api/videos/{videos[0]['slug']}/progress",
        headers=headers,
        json={"watched_seconds": 30, "completed": False},
    )
    assert watch.status_code == 200
    assert watch.json()["watched_seconds"] == 30

    glossary = client.get("/api/glossary?q=Messschieber")
    assert glossary.status_code == 200
    assert glossary.json()


def test_preferences_daily_goal_and_unit_complete() -> None:
    client = build_client()
    headers = login(client)
    prefs = client.get("/api/me/preferences", headers=headers)
    assert prefs.status_code == 200
    assert prefs.json()["language"] == "de"

    updated = client.put(
        "/api/me/preferences",
        headers=headers,
        json={"language": "en", "theme": "light", "daily_goal_lessons": 3},
    )
    assert updated.status_code == 200
    assert updated.json()["language"] == "en"
    assert updated.json()["daily_goal_lessons"] == 3

    goal = client.get("/api/daily-goal", headers=headers).json()
    assert goal["lessons_goal"] == 3

    units = client.get("/api/learning/units?month=1", headers=headers).json()
    slug = units[0]["slug"]
    complete = client.post(
        f"/api/learning/units/{slug}/complete",
        headers=headers,
    )
    assert complete.status_code == 200
    assert complete.json()["completed"] is True
    again = client.get("/api/learning/units?month=1", headers=headers).json()
    assert next(item for item in again if item["slug"] == slug)["completed"] is True

    dashboard = client.get("/api/dashboard", headers=headers).json()
    assert dashboard["units_completed"] >= 1
    assert dashboard["daily_lessons_done"] >= 1
    assert dashboard["readiness_percent"] >= 0

    inbox = client.get("/api/notifications", headers=headers).json()
    assert inbox
    marked = client.post(
        f"/api/notifications/{inbox[0]['id']}/read",
        headers=headers,
    )
    assert marked.json()["read"] is True


def test_training_report_suggest_sign_and_export() -> None:
    client = build_client()
    headers = login(client)
    created = client.post(
        "/api/training-reports",
        headers=headers,
        json={
            "report_date": "2026-08-13",
            "activities": "Drehen, Pruefen und Dokumentation im Betrieb.",
            "hours": 8,
        },
    )
    assert created.status_code == 201
    report_id = created.json()["id"]
    signed = client.post(
        f"/api/training-reports/{report_id}/sign",
        headers=headers,
    )
    assert signed.status_code == 200
    assert signed.json()["status"] == "submitted"

    suggest = client.get("/api/training-reports/suggest", headers=headers)
    assert suggest.status_code == 200
    assert "Betriebliche" in suggest.json()["activities"]

    exported = client.get("/api/training-reports/export", headers=headers)
    assert exported.status_code == 200
    assert "Berichtsheft" in exported.json()["body"]

    pdf = client.get("/api/training-reports/export.pdf", headers=headers)
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF")


def test_coach_chat_uses_learning_plan() -> None:
    client = build_client()
    headers = login(client)
    plan = client.get("/api/coach/plan", headers=headers)
    assert plan.status_code == 200
    chat = client.post(
        "/api/coach/chat",
        headers=headers,
        json={"message": "Ich verstehe die Formel fuer Kolbenkraft nicht."},
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert "F = p" in payload["reply"] or "Kolbenkraft" in payload["reply"]
    assert payload["href"] == "/lernen/formeltrainer"


def test_content_flag_and_leaderboard() -> None:
    client = build_client()
    headers = login(client)
    flagged = client.post(
        "/api/content/flags",
        headers=headers,
        json={
            "entity_type": "quiz_question",
            "entity_key": "q-demo",
            "reason": "unklar",
            "notes": "Formulierung ist mehrdeutig.",
        },
    )
    assert flagged.status_code == 200
    board = client.get("/api/leaderboard", headers=headers)
    assert board.status_code == 200
    assert isinstance(board.json(), list)


def test_staff_and_admin_endpoints() -> None:
    client = build_client()
    learner_headers = login(client, f"azubi-{uuid4()}")
    trainer_headers, _trainer = staff_login(client, "trainer")
    admin_headers, _admin = staff_login(client, "admin", platform_admin=True)

    assert client.get("/api/trainer/learners", headers=learner_headers).status_code == 403
    learners = client.get("/api/trainer/learners", headers=trainer_headers)
    assert learners.status_code == 200
    risk = client.get("/api/trainer/risk", headers=trainer_headers)
    assert risk.status_code == 200
    reports = client.get("/api/trainer/reports", headers=trainer_headers)
    assert reports.status_code == 200
    media = client.get("/api/media", headers=trainer_headers)
    assert media.status_code == 200
    assert media.json()

    monitoring = client.get("/api/admin/monitoring", headers=admin_headers)
    assert monitoring.status_code == 200
    assert monitoring.json()["quiz_questions"] == 480
    assert monitoring.json()["learning_units"] == 240
    audit = client.get("/api/admin/audit", headers=admin_headers)
    assert audit.status_code == 200
    settings = client.get("/api/admin/settings", headers=admin_headers)
    assert settings.status_code == 200
    assert "content_version" in settings.json()["settings"]
    users = client.get("/api/admin/users", headers=admin_headers)
    assert users.status_code == 200
    assert client.get("/api/admin/monitoring", headers=learner_headers).status_code == 403
