"""Multi-tenant isolation for trainer and admin panels."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import staff_login


def build_client() -> TestClient:
    return TestClient(create_app())


def login(
    client: TestClient,
    identifier: str,
    *,
    password: str = "demo-pass",
    cohort_code: str | None = None,
) -> tuple[dict[str, str], dict[str, object]]:
    payload: dict[str, str] = {"identifier": identifier, "password": password}
    if cohort_code:
        payload["cohort_code"] = cohort_code
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200, response.text
    body = response.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body


def login_prefixed(
    client: TestClient,
    prefix: str,
    cohort: str,
) -> tuple[dict[str, str], dict[str, object]]:
    return login(client, f"{prefix}-{uuid4()}", cohort_code=cohort)


def test_seeded_tenants_and_login_scope() -> None:
    client = build_client()
    admin, payload = staff_login(client, "admin", platform_admin=True)
    tenants = client.get("/api/tenants", headers=admin)
    assert tenants.status_code == 200
    slugs = {row["slug"] for row in tenants.json()}
    assert {"bze-euskirchen", "campus-demo"} <= slugs
    assert payload["is_platform_admin"] is True
    assert payload["tenant_id"] is None

    learner, _me = login_prefixed(client, "azubi", "BZE-2026-F")
    me = client.get("/api/auth/me", headers=learner)
    assert me.status_code == 200
    assert me.json()["tenant_id"] == "bze-euskirchen"
    assert me.json()["tenant_name"] == "BZE Euskirchen"
    assert me.json()["is_platform_admin"] is False


def test_trainer_cannot_see_other_tenant_learners() -> None:
    client = build_client()
    _bze_learner, bze_payload = login_prefixed(client, "azubi-bze", "BZE-2026-F")
    _demo_learner, demo_payload = login_prefixed(client, "azubi-demo", "DEMO-2026-A")
    bze_id = bze_payload["learner_id"]
    demo_id = demo_payload["learner_id"]

    bze_trainer, _bze_tr = staff_login(client, "trainer", cohort_code="BZE-2026-F")
    demo_trainer, _demo_tr = staff_login(client, "trainer", cohort_code="DEMO-2026-A")

    bze_rows = client.get("/api/trainer/learners", headers=bze_trainer)
    demo_rows = client.get("/api/trainer/learners", headers=demo_trainer)
    assert bze_rows.status_code == 200
    assert demo_rows.status_code == 200
    bze_ids = {row["learner_id"] for row in bze_rows.json()}
    demo_ids = {row["learner_id"] for row in demo_rows.json()}
    assert bze_id in bze_ids
    assert demo_id not in bze_ids
    assert demo_id in demo_ids
    assert bze_id not in demo_ids

    cockpit = client.get("/api/trainer/cockpit", headers=bze_trainer)
    assert cockpit.status_code == 200
    cockpit_ids = {row["learner_id"] for row in cockpit.json()["learners"]}
    assert bze_id in cockpit_ids
    assert demo_id not in cockpit_ids
    assert cockpit.json()["tenant_id"] == "bze-euskirchen"

    hotspots = client.get("/api/trainer/hotspots", headers=bze_trainer)
    assert hotspots.status_code == 200
    assert isinstance(hotspots.json(), list)


def test_trainer_reports_are_tenant_scoped() -> None:
    client = build_client()
    bze_learner, bze_payload = login_prefixed(client, "azubi-bze", "BZE-2026-F")
    demo_learner, demo_payload = login_prefixed(client, "azubi-demo", "DEMO-2026-A")
    for headers in (bze_learner, demo_learner):
        created = client.post(
            "/api/training-reports",
            headers=headers,
            json={
                "report_date": "2026-03-10",
                "activities": "Drehen und Messen dokumentiert.",
                "hours": 8,
            },
        )
        assert created.status_code == 201, created.text

    bze_trainer, _trainer = staff_login(client, "trainer", cohort_code="BZE-2026-F")
    reports = client.get("/api/trainer/reports", headers=bze_trainer)
    assert reports.status_code == 200
    learner_ids = {row["learner_id"] for row in reports.json()}
    assert bze_payload["learner_id"] in learner_ids
    assert demo_payload["learner_id"] not in learner_ids


def test_platform_admin_sees_all_and_can_create_tenant() -> None:
    client = build_client()
    login_prefixed(client, "azubi-bze", "BZE-2026-F")
    login_prefixed(client, "azubi-demo", "DEMO-2026-A")
    admin, _admin = staff_login(client, "admin", platform_admin=True)
    users = client.get("/api/admin/users", headers=admin)
    assert users.status_code == 200
    tenants = {row.get("tenant_id") for row in users.json()}
    assert "bze-euskirchen" in tenants
    assert "campus-demo" in tenants

    created = client.post(
        "/api/tenants",
        headers=admin,
        json={"name": "IHK Musterstadt", "slug": f"ihk-{uuid4().hex[:8]}"},
    )
    assert created.status_code == 200, created.text
    tenant_id = created.json()["tenant_id"]
    cohort = client.post(
        f"/api/tenants/{tenant_id}/cohorts",
        headers=admin,
        json={"code": f"IHK-{uuid4().hex[:6].upper()}", "name": "Fachklasse 2027"},
    )
    assert cohort.status_code == 200, cohort.text
    user = client.post(
        "/api/admin/users",
        headers=admin,
        json={
            "identifier": f"azubi-ihk-{uuid4().hex[:8]}",
            "password": "demo-pass",
            "role": "learner",
            "display_name": "Azubi IHK",
            "cohort_code": cohort.json()["code"],
            "tenant_id": tenant_id,
        },
    )
    assert user.status_code == 200, user.text
    assert user.json()["tenant_id"] == tenant_id
    assert user.json()["role"] == "learner"


def test_trainer_cannot_create_tenants() -> None:
    client = build_client()
    trainer, _payload = staff_login(client, "trainer", cohort_code="BZE-2026-F")
    denied = client.post(
        "/api/tenants",
        headers=trainer,
        json={"name": "Fremder Betrieb", "slug": "fremd-betrieb"},
    )
    assert denied.status_code == 403
    visible = client.get("/api/tenants", headers=trainer)
    assert visible.status_code == 200
    assert {row["tenant_id"] for row in visible.json()} == {"bze-euskirchen"}
