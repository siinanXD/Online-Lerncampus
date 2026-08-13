"""Illustrated learning-journey and question assets must be wired and served."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "app/web/static/app.js"
INDEX = ROOT / "app/web/index.html"
SCREENS = ROOT / "app/web/static/screens.js"
VISUALS_JS = ROOT / "app/web/static/visuals.js"
VISUALS_DIR = ROOT / "app/web/static/visuals"


def test_visual_catalog_covers_all_months_and_is_linked() -> None:
    html = INDEX.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")
    screens = SCREENS.read_text(encoding="utf-8")
    catalog = VISUALS_JS.read_text(encoding="utf-8")

    assert 'src="/static/visuals.js"' in html
    assert html.index("/static/visuals.js") < html.index("/static/app.js")
    assert "function visualKeyMatches" in app_js
    assert "fillVisualSlot" in app_js
    assert "unit-hero-visual" in app_js
    assert 'data-bind="question-media"' in screens
    assert 'data-bind="exam-question-media"' in screens

    for month in range(1, 25):
        assert f"{month}: {{ file:" in catalog


def test_visual_assets_are_served() -> None:
    client = TestClient(create_app())
    covers = list(VISUALS_DIR.glob("cover_*.jpg"))
    figures = list(VISUALS_DIR.glob("fig-*.svg"))
    assert len(covers) >= 8
    assert len(figures) >= 6
    for asset in covers[:2] + figures[:2]:
        response = client.get(f"/static/visuals/{asset.name}")
        assert response.status_code == 200, asset.name
        assert len(response.content) > 400
