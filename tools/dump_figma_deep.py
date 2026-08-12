"""Dump nested text + frame names for selected Figma screens."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.figma_extract import _guid, load_document  # noqa: E402


def walk(node_id, children, depth=0, max_depth=4, limit=80):
    rows = []
    if depth > max_depth or limit <= 0:
        return rows
    for child in children.get(node_id, []):
        size = child.get("size") or {}
        name = child.get("name") or ""
        typ = child.get("type") or ""
        rows.append(
            (
                depth,
                typ,
                name,
                size.get("x"),
                size.get("y"),
            )
        )
        rows.extend(
            walk(
                _guid(child.get("guid")),
                children,
                depth + 1,
                max_depth,
                limit - len(rows),
            )
        )
        if len(rows) >= limit:
            break
    return rows


def main() -> None:
    fig = Path("BZE Online Campus Fachkunde Designsystem.fig")
    nodes = load_document(fig)["nodeChanges"]
    children: dict = defaultdict(list)
    named: dict = defaultdict(list)
    for node in nodes:
        parent = _guid((node.get("parentIndex") or {}).get("guid"))
        if parent:
            children[parent].append(node)
        name = node.get("name") or ""
        if name:
            named[name].append(node)

    wanted = [
        "03.1 Dashboard - Default",
        "01.1 Login",
        "04.1 Lernen Hub",
        "06.1 Prüfungsliste",
        "08.1 Berichtsheft — Liste",
        "tab-bar-container",
        "section-buttons",
        "section-navigation",
        "section-cards",
        "bottom-navigation",
    ]
    out = Path("work_figma_deep.txt")
    lines: list[str] = []
    for key in wanted:
        matches = [n for name, items in named.items() if key.lower() in name.lower() for n in items]
        lines.append(f"## {key} ({len(matches)})")
        if not matches:
            lines.append("(none)")
            lines.append("")
            continue
        node = matches[0]
        for depth, typ, name, x, y in walk(_guid(node.get("guid")), children):
            indent = "  " * depth
            lines.append(f"{indent}{typ}: {name} ({x}x{y})")
        lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
