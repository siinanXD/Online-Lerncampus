"""Regression tests for the security hardening changes."""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app
from tests.conftest import staff_login


def build_client() -> TestClient:
    return TestClient(create_app())


def login_payload(client: TestClient, identifier: str, password: str = "demo-pass"):
    return client.post(
        "/api/auth/login",
        json={
            "identifier": identifier,
            "password": password,
            "cohort_code": "BZE-2026-F",
        },
    )


def test_admin_prefix_no_longer_grants_admin_role() -> None:
    """Self-registered accounts must always be plain learners."""
    client = build_client()
    for prefix in ("admin", "reviewer", "trainer"):
        response = login_payload(client, f"{prefix}-{uuid4()}")
        assert response.status_code == 200
        payload = response.json()
        assert payload["role"] == "learner"
        assert payload["is_platform_admin"] is False
        headers = {"Authorization": f"Bearer {payload['access_token']}"}
        denied = client.get("/api/admin/users", headers=headers)
        assert denied.status_code == 403


def test_content_generate_requires_staff_session() -> None:
    """Anonymous callers and learners must not reach the content factory."""
    client = build_client()
    body = {
        "occupation_slug": "maschinen-und-anlagenfuehrer",
        "month": 8,
        "learner_level": "azubi",
    }
    anonymous = client.post("/api/content/generate", json=body)
    assert anonymous.status_code == 401

    learner = login_payload(client, f"azubi-{uuid4()}").json()
    learner_headers = {"Authorization": f"Bearer {learner['access_token']}"}
    denied = client.post("/api/content/generate", headers=learner_headers, json=body)
    assert denied.status_code == 403

    review_denied = client.post(
        "/api/content/review",
        headers=learner_headers,
        json={
            "draft_id": "draft-12345678",
            "approved": True,
            "reviewer_notes": "Nicht erlaubt.",
        },
    )
    assert review_denied.status_code == 403


def test_new_account_rejects_short_password() -> None:
    client = build_client()
    response = login_payload(client, f"azubi-{uuid4()}", password="kurz")
    assert response.status_code == 400
    assert "mindestens 8 Zeichen" in response.json()["detail"]


def test_login_locks_after_repeated_failures() -> None:
    client = build_client()
    identifier = f"azubi-{uuid4()}"
    assert login_payload(client, identifier).status_code == 200
    for _attempt in range(5):
        wrong = login_payload(client, identifier, password="falsches-pw")
        assert wrong.status_code == 400
        assert wrong.json()["detail"] == "Passwort ist falsch."
    locked = login_payload(client, identifier)
    assert locked.status_code == 400
    assert "Zu viele fehlgeschlagene" in locked.json()["detail"]


def test_provisioned_staff_keep_their_role() -> None:
    client = build_client()
    headers, payload = staff_login(client, "reviewer")
    assert payload["role"] == "reviewer"
    pending = client.get("/api/content/review/pending", headers=headers)
    assert pending.status_code == 200


def test_bootstrap_admin_is_provisioned(monkeypatch: pytest.MonkeyPatch) -> None:
    identifier = f"bootstrap-admin-{uuid4()}"
    monkeypatch.setenv("BOOTSTRAP_ADMIN_IDENTIFIER", identifier)
    monkeypatch.setenv("BOOTSTRAP_ADMIN_PASSWORD", "Bootstrap-Pass1!")
    get_settings.cache_clear()
    client = build_client()
    # Trigger the lazy content bootstrap, which provisions the admin.
    assert client.get("/api/content/stats").status_code == 200
    response = login_payload(client, identifier, password="Bootstrap-Pass1!")
    assert response.status_code == 200
    payload = response.json()
    assert payload["role"] == "admin"
    assert payload["is_platform_admin"] is True


def test_login_sets_httponly_session_cookie() -> None:
    client = build_client()
    response = login_payload(client, f"azubi-{uuid4()}")
    assert response.status_code == 200
    set_cookie = response.headers.get("set-cookie", "")
    assert "ol_session=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    # The cookie alone must authenticate follow-up requests.
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["role"] == "learner"


def test_logout_clears_session_cookie() -> None:
    client = build_client()
    assert login_payload(client, f"azubi-{uuid4()}").status_code == 200
    assert client.get("/api/auth/me").status_code == 200
    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200
    assert 'ol_session=""' in logout.headers.get("set-cookie", "")
    assert client.get("/api/auth/me").status_code == 401


def test_bearer_header_still_works_for_api_clients() -> None:
    client = build_client()
    payload = login_payload(client, f"azubi-{uuid4()}").json()
    client.cookies.clear()
    headers = {"Authorization": f"Bearer {payload['access_token']}"}
    assert client.get("/api/auth/me", headers=headers).status_code == 200


def test_security_headers_are_present() -> None:
    client = build_client()
    for path in ("/", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert "default-src 'self'" in response.headers["content-security-policy"]
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "same-origin"
        assert "camera=()" in response.headers["permissions-policy"]
        # HSTS only outside local development.
        assert "strict-transport-security" not in response.headers


def test_index_has_no_inline_script() -> None:
    """CSP forbids inline scripts, so index.html must only load static files."""
    from pathlib import Path

    html = Path("app/web/index.html").read_text(encoding="utf-8")
    for line in html.splitlines():
        if "<script" in line:
            assert 'src="/static/' in line, line


def test_production_env_rejects_insecure_defaults(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    get_settings.cache_clear()
    with pytest.raises(RuntimeError, match="Unsichere Konfiguration"):
        create_app()
    monkeypatch.setenv("APP_SECRET", "x" * 40)
    monkeypatch.setenv("APP_DEBUG", "false")
    get_settings.cache_clear()
    app = create_app()
    assert app is not None
