"""Compact unit pager, fact sheets, and core formulas/terms."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_JS = ROOT / "app/web/static/app.js"
SCREENS = ROOT / "app/web/static/screens.js"
VISUALS_JS = ROOT / "app/web/static/visuals.js"
GX_CSS = ROOT / "app/web/static/gx.css"


def test_unit_detail_is_a_no_scroll_pager() -> None:
    screens = SCREENS.read_text(encoding="utf-8")
    app_js = APP_JS.read_text(encoding="utf-8")
    css = GX_CSS.read_text(encoding="utf-8")

    assert 'class="gx-screen gx-einheit unit-pager"' in screens
    assert "unit-step-next" in app_js
    assert "data-action=\"unit-step-next\"" in app_js
    assert "overflow: hidden" in css
    assert ".unit-step-actions" in css
    assert "Fragen üben" in app_js


def test_fact_sheets_cover_deep_topics() -> None:
    catalog = VISUALS_JS.read_text(encoding="utf-8")
    assert "7,85 g/cm³" in catalog
    assert "20 H7" in catalog
    assert "6 bar" in catalog
    assert "vc = (π × d × n) / 1000" in catalog
    assert "ρ = m / V" in catalog
    assert "Messschieber" in catalog
    for month in (2, 3, 6, 8, 9, 13, 16, 22):
        assert f"{month}" in catalog


def test_formula_and_glossary_use_continue_cards() -> None:
    app_js = APP_JS.read_text(encoding="utf-8")
    assert "formula-step-next" in app_js
    assert "glossary-step-next" in app_js
    assert "OLC_CORE_FORMULA_SLUGS" in app_js
    assert "Wichtigste Begriffe" in app_js
