"""Wiring tests for the adaptive Phone/Tablet/Desktop stylesheet."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "app/web/index.html"
RESPONSIVE_CSS = ROOT / "app/web/static/responsive.css"
APP_JS = ROOT / "app/web/static/app.js"


def test_responsive_stylesheet_is_linked_after_gx() -> None:
    html = INDEX.read_text(encoding="utf-8")
    css = RESPONSIVE_CSS.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")

    assert 'href="/static/responsive.css"' in html
    assert html.index("/static/responsive.css") > html.index("/static/gx.css")
    assert 'class="nav-toggle"' in html
    assert 'id="site-nav-links"' in html
    assert 'name="viewport"' in html
    assert "width=device-width" in html

    assert "container-type: inline-size" in css
    assert "@container gx" in css
    assert "100dvh" in css
    assert "env(safe-area-inset-bottom" in css
    assert 'container-name: app-shell' in css
    assert "width: 100% !important" in css
    assert "min-height: 100dvh !important" in css

    assert "function initSiteNav()" in app_js
    assert "initSiteNav();" in app_js


def test_responsive_assets_are_served() -> None:
    client = TestClient(create_app())
    home = client.get("/")
    assert home.status_code == 200
    assert "/static/responsive.css" in home.text
    assert 'class="nav-toggle"' in home.text

    css = client.get("/static/responsive.css")
    assert css.status_code == 200
    assert "container-type: inline-size" in css.text
    assert "@container gx (min-width: 1024px)" in css.text
    assert "@container app-shell (min-width: 1024px)" in css.text

    login = client.get("/login")
    assert login.status_code == 200
    assert "/static/responsive.css" in login.text
