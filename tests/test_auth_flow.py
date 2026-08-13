"""Tests for the 01 auth onboarding flow."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app


def build_client() -> TestClient:
    return TestClient(create_app())


def login(client: TestClient, identifier: str | None = None) -> dict[str, object]:
    response = client.post(
        "/api/auth/login",
        json={
            "identifier": identifier or f"azubi-{uuid4()}",
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    headers = {"Authorization": f"Bearer {payload['access_token']}"}
    return {"headers": headers, "payload": payload}


def test_new_learner_requires_password_change() -> None:
    client = build_client()
    result = login(client)
    payload = result["payload"]
    assert payload["requires_password_change"] is True
    assert payload["onboarding_completed"] is False


def test_demo_learner_skips_password_change() -> None:
    client = build_client()
    result = login(client, "demo-azubi")
    payload = result["payload"]
    assert payload["requires_password_change"] is False


def test_onboarding_complete_endpoint() -> None:
    client = build_client()
    result = login(client, f"flow-{uuid4()}")
    headers = result["headers"]
    complete = client.post("/api/auth/onboarding/complete", headers=headers)
    assert complete.status_code == 200
    assert complete.json()["onboarding_completed"] is True
    profile = client.get("/api/auth/me", headers=headers).json()
    assert profile["onboarding_completed"] is True


def test_password_change_clears_required_flag() -> None:
    client = build_client()
    identifier = f"pw-{uuid4()}"
    login(client, identifier)
    session = client.post(
        "/api/auth/login",
        json={
            "identifier": identifier,
            "password": "demo-pass",
            "cohort_code": "BZE-2026-F",
        },
    ).json()
    headers = {"Authorization": f"Bearer {session['access_token']}"}
    change = client.post(
        "/api/auth/password",
        headers=headers,
        json={
            "current_password": "demo-pass",
            "new_password": "SicheresKennw1!",
            "repeated_password": "SicheresKennw1!",
        },
    )
    assert change.status_code == 200
    profile = client.get("/api/auth/me", headers=headers).json()
    assert profile["requires_password_change"] is False
