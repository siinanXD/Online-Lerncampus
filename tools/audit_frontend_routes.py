"""Audit frontend page routes and API wiring against the FastAPI backend."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_allowed() -> set[str]:
    return set(json.loads((ROOT / "app/web/allowed_pages.json").read_text(encoding="utf-8")))


def load_route_config_paths() -> set[str]:
    screens = (ROOT / "app/web/static/screens.js").read_text(encoding="utf-8")
    keys = re.findall(r'^\s*"(/[^"]*)"\s*:', screens, re.M)
    paths: set[str] = set()
    for key in keys:
        paths.add("" if key == "/" else key.lstrip("/"))
    return paths


def load_frontend_api_calls() -> list[tuple[str, str, bool]]:
    """Extract fetchJson API calls from app.js (and any other static JS)."""
    calls: list[tuple[str, str, bool]] = []
    for js_path in (ROOT / "app/web/static").glob("*.js"):
        text = js_path.read_text(encoding="utf-8")
        for match in re.finditer(r"fetchJson\s*\(", text):
            start = match.end()
            # Limit to this call's argument list so neighboring methods are ignored.
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
                url_match = re.search(r"`(/api/[^`]+)`", window)
            if not url_match:
                continue
            method_match = re.search(r"""method:\s*['"](\w+)""", window)
            auth = "authHeaders" in window or "Authorization" in window
            method = method_match.group(1) if method_match else "GET"
            calls.append((method, url_match.group(1), auth))
    return sorted(set(calls))

def load_backend_endpoints() -> list[tuple[str, str]]:
    routes_py = (ROOT / "app/api/routes.py").read_text(encoding="utf-8")
    endpoints: list[tuple[str, str]] = []
    for match in re.finditer(
        r"@api_router\.(get|post|put|patch|delete)\((.*?)\)\s*\ndef ",
        routes_py,
        re.S,
    ):
        method = match.group(1).upper()
        path_match = re.search(r"""['"]([^'"]+)['"]""", match.group(2))
        if path_match:
            endpoints.append((method, "/api" + path_match.group(1)))
    return sorted(set(endpoints))


def normalize_url(url: str) -> str:
    url = re.sub(r"\$\{[^}]+\}", "{param}", url)
    return url.split("?", 1)[0]


def parts_match(front: str, back: str) -> bool:
    front_parts = front.split("/")
    back_parts = back.split("/")
    if len(front_parts) != len(back_parts):
        return False
    for fp, bp in zip(front_parts, back_parts):
        if fp == bp:
            continue
        if fp.startswith("{") or bp.startswith("{"):
            continue
        return False
    return True


def load_href_paths() -> set[str]:
    html = (ROOT / "app/web/index.html").read_text(encoding="utf-8")
    screens = (ROOT / "app/web/static/screens.js").read_text(encoding="utf-8")
    hrefs = set(re.findall(r'href="(/[^"]*)"', html + screens))
    clean: set[str] = set()
    for href in hrefs:
        href = href.split("#", 1)[0]
        if not href or href.startswith("/static") or href.startswith("/api"):
            continue
        clean.add("" if href == "/" else href.lstrip("/"))
    return clean


def main() -> None:
    allowed = load_allowed()
    routes = load_route_config_paths()
    print(f"allowed_pages count: {len(allowed)}")
    print(f"routeConfig paths: {len(routes)}")
    print("In routeConfig but NOT allowlist:", sorted(routes - allowed))
    print("In allowlist but NOT routeConfig:", sorted(allowed - routes))

    calls = load_frontend_api_calls()
    print("\nFrontend API calls:")
    for method, url, auth in calls:
        print(f"  {method:6} {url:55} auth={auth}")

    backend = load_backend_endpoints()
    print(f"\nBackend endpoints: {len(backend)}")
    for method, url in backend:
        print(f"  {method:6} {url}")

    fe_norm = {(method, normalize_url(url)) for method, url, _ in calls}
    be_norm = set(backend)

    print("\n--- FE calls without BE match ---")
    for method, url in sorted(fe_norm):
        matched = any(bm == method and parts_match(url, bu) for bm, bu in be_norm)
        if not matched:
            print(f"  MISSING? {method} {url}")

    print("\n--- BE orphans (not called by FE) ---")
    for method, url in sorted(be_norm):
        matched = any(fm == method and parts_match(fu, url) for fm, fu in fe_norm)
        if not matched:
            print(f"  ORPHAN  {method} {url}")

    hrefs = load_href_paths()
    print("\nNav/href paths not in allowlist:", sorted(hrefs - allowed))
    print("Nav/href paths not in routeConfig:", sorted(hrefs - routes))


if __name__ == "__main__":
    main()
