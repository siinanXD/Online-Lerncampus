"""Dump hierarchy for key Figma frames used by the frontend rebuild."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figma_extract import _guid, load_document  # noqa: E402

TARGETS = [
    "02.1 Tab Bar",
    "02.2 Status Bar",
    "03.1 Dashboard",
    "01.1 Login",
    "01.5 Landing",
    "04.1 Lernen Hub",
    "06.1 Prüfungsliste",
    "06.1 Pruefungsliste",
    "08.1 Berichtsheft",
    "09.1 Mehr",
    "00.3 Components",
    "00.1 Colors",
    "00.2 Typography",
]


def main() -> None:
    fig = Path("BZE Online Campus Fachkunde Designsystem.fig")
    nodes = load_document(fig)["nodeChanges"]
    children: dict[tuple[int, int], list[dict]] = defaultdict(list)
    named: dict[str, list[dict]] = defaultdict(list)
    for node in nodes:
        name = node.get("name") or ""
        parent = _guid((node.get("parentIndex") or {}).get("guid"))
        if parent:
            children[parent].append(node)
        if name and node.get("type") in {
            "FRAME",
            "COMPONENT",
            "COMPONENT_SET",
            "SECTION",
        }:
            named[name].append(node)

    for target in TARGETS:
        matches = [
            (name, items)
            for name, items in named.items()
            if target.lower() in name.lower()
        ]
        print(f"== target: {target}")
        if not matches:
            print("  (no match)")
            continue
        for name, items in matches[:2]:
            node = items[0]
            size = node.get("size") or {}
            print(
                f"  frame: {name} | {node.get('type')} | "
                f"{size.get('x')}x{size.get('y')}"
            )
            for child in children.get(_guid(node["guid"]), [])[:50]:
                child_size = child.get("size") or {}
                print(
                    f"    - {child.get('type')}: {child.get('name')} "
                    f"({child_size.get('x')}x{child_size.get('y')})"
                )
        print()


if __name__ == "__main__":
    main()
