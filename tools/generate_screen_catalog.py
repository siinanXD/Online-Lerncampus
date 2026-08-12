"""Build screen catalog JSON from extracted Figma text."""

from __future__ import annotations

import json
import re
from pathlib import Path


def slugify(value: str) -> str:
    value = value.lower()
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "—": "-",
        "–": "-",
        " ": "-",
        "/": "-",
        "&": "und",
        ".": "",
        ",": "",
        ":": "",
        '"': "",
        "'": "",
        "(": "",
        ")": "",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    value = re.sub(r"[^a-z0-9\-]+", "-", value)
    return re.sub(r"-+", "-", value).strip("-")[:64]


SKIP_TOKENS = {
    "(no text)",
    "time",
    "header-title",
    "title",
    "desc",
    "tag",
    "btn-label",
    "txt",
    "stat",
    "pct",
    "tab-label",
    "indicator",
    "duration",
    "video-heading",
    "instructor-name",
    "instructor-badge",
    "sect-title",
    "time-label",
    "chapter-title",
    "card-title",
    "card-subtitle",
    "formula-math",
    "leg-symbol",
    "leg-desc",
    "example-title",
    "example-text",
    "diff-label",
    "btn-xp",
    "preview-math",
    "result-info",
    "xp",
    "retry-link",
    "lock-condition",
    "badge-text",
    "diff",
    "chip-label",
    "9:41",
    "09:41",
}

PATH_OVERRIDES = {
    "01.1": "/login",
    "01.2": "/passwort",
    "01.3": "/sprache",
    "01.4": "/onboarding",
    "01.5": "/",
    "01.6": "/level-up",
    "03.1": "/dashboard",
    "03.2": "/dashboard/tagesziel",
    "03.3": "/dashboard/streak",
    "03.5": "/dashboard/fortsetzen",
    "03.6": "/dashboard/wochenbericht",
    "03.7": "/dashboard/merksaetze",
    "03.8": "/dashboard/tablet",
    "04.1": "/lernen",
    "04.2": "/lernen/themen",
    "04.3": "/lernen/fragen",
    "04.4": "/lernen/fragen/fehler",
    "04.5": "/lernen/frage",
    "04.6": "/lernen/frage/freitext",
    "04.7": "/lernen/feedback/richtig",
    "04.8": "/lernen/feedback/falsch",
    "04.9": "/lernen/melden",
    "04.10": "/lernen/uebersetzung",
    "04.11": "/lernen/formeltrainer",
    "04.12": "/lernen/fehlerdiagnose",
    "04.13": "/lernen/video",
    "04.14": "/lernen/detail",
    "04.15": "/lernen/tablet",
    "04.16": "/lernen/lernpfad",
    "04.17": "/lernen/einheit",
    "04.18": "/lernen/glossar",
    "04.19": "/lernen/flashcard",
    "05.1": "/fachkunde",
    "05.2": "/fachkunde/lernpfad",
    "05.3": "/fachkunde/einheit",
    "05.4": "/fachkunde/glossar",
    "05.5": "/fachkunde/abschluss",
    "05.6": "/fachkunde/bausteine",
    "05.7": "/fachkunde/toleranz",
    "05.8": "/fachkunde/spritzguss",
    "05.9": "/fachkunde/messschieber",
    "05.10": "/fachkunde/freigabe",
    "06.1": "/pruefungen",
    "06.2": "/pruefungen/frage",
    "06.3": "/pruefungen/uebersicht",
    "06.4": "/pruefungen/timer",
    "06.5": "/pruefungen/abgabe",
    "06.6": "/pruefungen/bestanden",
    "06.7": "/pruefungen/durchgefallen",
    "06.8": "/pruefungen/schwach",
    "06.9": "/pruefungen/kammertermine",
    "07.1": "/fortschritt",
    "07.2": "/fortschritt/pruefungsreife",
    "07.3": "/fortschritt/ausstehend",
    "07.4": "/fortschritt/verlauf",
    "07.5": "/fortschritt/xp",
    "07.6": "/fortschritt/heatmap",
    "08.1": "/berichtsheft",
    "08.2": "/berichtsheft/neu",
    "08.3": "/berichtsheft/ki",
    "08.4": "/berichtsheft/unterschrift",
    "08.5": "/berichtsheft/kalender",
    "08.6": "/berichtsheft/export",
    "08.7": "/berichtsheft/leer",
    "09.1": "/mehr",
    "09.2": "/mehr/ausbilder-sicht",
    "09.3": "/mehr/coach",
    "09.4": "/mehr/lernplan",
    "09.5": "/mehr/export",
    "09.6": "/mehr/loeschen",
    "09.7": "/mehr/logout",
    "11.1": "/ausbilder",
    "11.2": "/ausbilder/teilnehmer",
    "11.3": "/ausbilder/pruefungsreife",
    "11.4": "/ausbilder/risiko",
    "11.5": "/ausbilder/hotspots",
    "11.6": "/ausbilder/kohorte",
    "11.7": "/ausbilder/kohorte/detail",
    "12.1": "/ausbilder/review",
    "12.2": "/ausbilder/review/detail",
    "12.3": "/ausbilder/fragen",
    "12.4": "/ausbilder/generator",
    "12.5": "/ausbilder/themen",
    "12.6": "/ausbilder/frage-bearbeiten",
    "12.7": "/ausbilder/freigabe",
    "12.8": "/ausbilder/editor",
    "12.9": "/ausbilder/medien",
    "13.1": "/ausbilder/berichte",
    "13.3": "/ausbilder/bericht-export",
    "15.1": "/admin/nutzer",
    "15.2": "/admin/nutzer/detail",
    "15.3": "/admin/audit",
    "15.4": "/admin/einstellungen",
    "15.5": "/admin/monitoring",
    "15.6": "/admin/zugangsdaten",
    "16.1": "/admin/content",
    "16.2": "/admin/content/liste",
    "16.4": "/admin/wissen",
    "16.5": "/admin/lernziele",
    "16.6": "/admin/quiz",
    "16.10": "/admin/import",
    "16.11": "/admin/dubletten",
}

DUP_PATHS = {
    ("13.2", "Prüfungsplanung — Detail"): "/ausbilder/planung",
    ("13.2", "Berichtsheft-Detail — Ausbilder"): "/ausbilder/bericht-detail",
    ("16.3", "Qualitätsprüfung"): "/admin/content/qualitaet",
    ("16.3", "Content-Detail"): "/admin/content/detail",
}


def layout_for(num: str, path: str) -> str:
    if path == "/":
        return "landing"
    if path == "/login":
        return "login"
    section = int(num.split(".")[0])
    if section == 1:
        return "auth"
    if section <= 9 or section == 18:
        return "app"
    if section <= 13:
        return "trainer"
    return "admin"


def tab_for(num: str) -> str | None:
    section = int(num.split(".")[0])
    return {
        3: "dashboard",
        4: "learn",
        5: "learn",
        6: "exam",
        7: "progress",
        8: "reports",
        9: "profile",
        18: "profile",
    }.get(section)


def parse_screens(text: str) -> list[dict]:
    blocks = re.split(r"\n### ", text)
    screens_raw: list[dict] = []
    for block in blocks:
        if not block.strip():
            continue
        first = block.split("\n", 1)[0]
        match = re.match(
            r"^(\d{2}\.\d+(?:\.\d+)?)\s+(.+?)\s+\((\d+(?:\.\d+)?)x(\d+(?:\.\d+)?)\)$",
            first,
        )
        if not match:
            continue
        num, title, width, height = (
            match.group(1),
            match.group(2),
            float(match.group(3)),
            float(match.group(4)),
        )
        if width < 300 or height < 500:
            continue
        lines: list[str] = []
        for line in block.split("\n")[1:]:
            if not line.startswith("- "):
                continue
            value = line[2:].strip()
            if value and value not in SKIP_TOKENS and not value.startswith("chip-"):
                lines.append(value)
        screens_raw.append(
            {
                "num": num,
                "title": title,
                "w": int(width),
                "h": int(height),
                "texts": lines[:24],
            }
        )

    best: dict[tuple[str, str], dict] = {}
    for screen in screens_raw:
        key = (screen["num"], screen["title"])
        previous = best.get(key)
        if previous is None or screen["w"] * screen["h"] > previous["w"] * previous["h"]:
            best[key] = screen
    return sorted(best.values(), key=lambda item: (item["num"], item["title"]))


def main() -> None:
    text = Path("work/figma_screen_text.md").read_text(encoding="utf-8")
    screens = [
        screen
        for screen in parse_screens(text)
        if screen["num"] not in {"03.4", "05.11"}
        and not screen["num"].startswith(("00.", "17."))
    ]

    used_paths: set[str] = set()
    catalog: list[dict] = []
    for screen in screens:
        key = (screen["num"], screen["title"])
        path = DUP_PATHS.get(key) or PATH_OVERRIDES.get(screen["num"])
        if not path:
            path = f"/{slugify(screen['title'])}"
        original = path
        suffix = 2
        while path in used_paths:
            path = f"{original}-{suffix}"
            suffix += 1
        used_paths.add(path)
        catalog.append(
            {
                **screen,
                "id": f"s{screen['num'].replace('.', '_')}-{slugify(screen['title'])[:40]}",
                "path": path,
                "layout": layout_for(screen["num"], path),
                "tab": tab_for(screen["num"]),
            }
        )

    extras = [
        {
            "num": "02.1",
            "title": "Tab Bar",
            "path": "/shell/tab-bar",
            "layout": "app",
            "tab": "dashboard",
            "texts": ["Start", "Lernen", "Pruefung", "Bericht", "Mehr"],
            "w": 390,
            "h": 961,
        },
        {
            "num": "10.1",
            "title": "Ausbilder Top Navigation",
            "path": "/ausbilder/nav",
            "layout": "trainer",
            "tab": None,
            "texts": ["Cockpit", "Review", "Content", "Berichte"],
            "w": 1280,
            "h": 750,
        },
        {
            "num": "10.2",
            "title": "Ausbilder Shell Desktop",
            "path": "/ausbilder/shell",
            "layout": "trainer",
            "tab": None,
            "texts": ["Shell"],
            "w": 1280,
            "h": 900,
        },
        {
            "num": "14.1",
            "title": "Admin Shell",
            "path": "/admin",
            "layout": "admin",
            "tab": None,
            "texts": ["Nutzer", "Content", "Betrieb"],
            "w": 1440,
            "h": 900,
        },
        {
            "num": "18.1",
            "title": "Gamification Übersicht",
            "path": "/gamification",
            "layout": "app",
            "tab": "profile",
            "texts": ["XP", "Level", "Badges", "Streaks", "Leaderboard"],
            "w": 1400,
            "h": 2306,
        },
        {
            "num": "18.2",
            "title": "XP & Level",
            "path": "/gamification/xp",
            "layout": "app",
            "tab": "profile",
            "texts": ["Level", "XP Fortschritt"],
            "w": 1200,
            "h": 800,
        },
        {
            "num": "18.3",
            "title": "Badges",
            "path": "/gamification/badges",
            "layout": "app",
            "tab": "profile",
            "texts": ["Abzeichen"],
            "w": 1200,
            "h": 800,
        },
        {
            "num": "18.4",
            "title": "Streaks & Leaderboard",
            "path": "/gamification/streaks",
            "layout": "app",
            "tab": "profile",
            "texts": ["Streak", "Rangliste"],
            "w": 1200,
            "h": 800,
        },
    ]
    for extra in extras:
        if extra["path"] in used_paths:
            continue
        used_paths.add(extra["path"])
        catalog.append(
            {
                "num": extra["num"],
                "title": extra["title"],
                "w": extra["w"],
                "h": extra["h"],
                "texts": extra["texts"],
                "id": f"s{extra['num'].replace('.', '_')}-{slugify(extra['title'])[:40]}",
                "path": extra["path"],
                "layout": extra["layout"],
                "tab": extra["tab"],
            }
        )

    aliases = {
        "/funktionen": "/",
        "/lernreise": "/fortschritt/verlauf",
        "/defizite": "/fortschritt",
        "/review": "/ausbilder/review",
        "/datenschutz": "/mehr/export",
    }

    Path("work/screen_catalog.json").write_text(
        json.dumps({"screens": catalog, "aliases": aliases}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    layouts = {
        key: sum(1 for screen in catalog if screen["layout"] == key)
        for key in ("landing", "auth", "app", "trainer", "admin")
    }
    print(f"catalog={len(catalog)} aliases={len(aliases)} layouts={layouts}")


if __name__ == "__main__":
    main()
