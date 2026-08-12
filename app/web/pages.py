"""Frontend page allowlist derived from the Figma screen catalog."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

_ALLOWED_PATH = Path(__file__).resolve().parent / "allowed_pages.json"

# Fallback keep legacy routes if the generated file is missing in a deploy.
_FALLBACK_PAGES = {
    "",
    "funktionen",
    "login",
    "dashboard",
    "lernreise",
    "lernen",
    "pruefungen",
    "berichtsheft",
    "defizite",
    "review",
    "datenschutz",
    "mehr",
}


@lru_cache(maxsize=1)
def allowed_frontend_pages() -> set[str]:
    """Return all browser page paths that should serve the SPA shell."""
    if _ALLOWED_PATH.exists():
        payload = json.loads(_ALLOWED_PATH.read_text(encoding="utf-8"))
        return {str(item) for item in payload}
    return set(_FALLBACK_PAGES)
