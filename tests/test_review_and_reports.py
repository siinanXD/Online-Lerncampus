"""Tests for review gate, staff roles, and Berichtsheft API."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


def build_client() -> TestClient:
    return TestClient(create_app())


def login(client: TestClient, identifier: str) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": identifier,
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


from app.api import routes as app_routes


def _reset_one_unit_to_draft() -> None:
    app_routes.bootstrap_content_store()
    with app_routes._database()._transaction() as connection:
        connection.execute(
            """
            UPDATE learning_units
            SET review_status = 'draft'
            WHERE slug = 'messschieber'
            """
        )


def test_reviewer_role_can_list_pending_content() -> None:
    """Staff logins must expose the DB-backed review queue."""
    _reset_one_unit_to_draft()
    client = build_client()
    headers = login(client, f"reviewer-{uuid4()}")
    response = client.get("/api/content/review/pending", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload
    assert payload[0]["entity_type"] in {
        "learning_unit",
        "quiz_question",
        "open_question",
    }


def test_learner_cannot_access_review_queue() -> None:
    """Azubis must not see reviewer endpoints."""
    client = build_client()
    headers = login(client, f"azubi-{uuid4()}")
    response = client.get("/api/content/review/pending", headers=headers)
    assert response.status_code == 403


def test_reviewer_can_approve_learning_unit() -> None:
    """Approved content must become visible when review gate is enabled."""
    _reset_one_unit_to_draft()
    client = build_client()
    headers = login(client, f"reviewer-{uuid4()}")
    pending = client.get("/api/content/review/pending", headers=headers).json()
    unit = next(item for item in pending if item["entity_type"] == "learning_unit")
    response = client.post(
        "/api/content/review/decision",
        headers=headers,
        json={
            "entity_type": "learning_unit",
            "entity_key": unit["entity_key"],
            "to_status": "approved",
            "notes": "Fachlich geprueft und freigegeben.",
        },
    )
    assert response.status_code == 200
    assert response.json()["to_status"] == "approved"


def test_training_report_crud_for_learner() -> None:
    """Learners can maintain their Berichtsheft entries."""
    client = build_client()
    headers = login(client, f"azubi-{uuid4()}")
    create = client.post(
        "/api/training-reports",
        headers=headers,
        json={
            "report_date": "2026-08-12",
            "activities": "CNC-Ruesten, Erstteilpruefung und Berichtsheft-Eintrag.",
            "hours": 8.0,
        },
    )
    assert create.status_code == 201
    report_id = create.json()["id"]
    listing = client.get("/api/training-reports", headers=headers)
    assert listing.status_code == 200
    assert any(item["id"] == report_id for item in listing.json())
    update = client.put(
        f"/api/training-reports/{report_id}",
        headers=headers,
        json={
            "report_date": "2026-08-12",
            "activities": "CNC-Ruesten, Erstteilpruefung, Einweisung SHU.",
            "hours": 8.5,
            "status": "submitted",
        },
    )
    assert update.status_code == 200
    assert update.json()["status"] == "submitted"
