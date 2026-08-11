"""Extract design tokens and the screen inventory from a Figma ``.fig`` export.

A ``.fig`` file is a ZIP archive whose ``canvas.fig`` entry holds a kiwi-encoded
document::

    b"fig-kiwi" | uint32 version | (uint32 length + compressed block)*

Block 0 is the kiwi *schema*, block 1 the message payload. Older exports deflate
both blocks; current exports compress the payload with zstd. Because the schema
travels inside the file, the document can be decoded without Figma API access.

Usage::

    python tools/figma_extract.py <file.fig> --css app/web/static/tokens.css
    python tools/figma_extract.py <file.fig> --screens docs/design/screens.md
"""

from __future__ import annotations

import argparse
import struct
import zipfile
import zlib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

KIND_ENUM, KIND_STRUCT, KIND_MESSAGE = 0, 1, 2
ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"

# The variable set that carries semantic, production-ready tokens. The export
# also contains an older blue-based palette ("Colors"/"Spacing"/"Radius") that
# predates the BZE rebrand; only the BZE sets define WEB codeSyntax.
LIGHT_SET = "BZE Color Light"
DARK_SET = "BZE Color Dark Reference"
SPACING_SET = "BZE Spacing"
RADIUS_SET = "BZE Radius"


class Reader:
    """Cursor over a kiwi byte buffer."""

    def __init__(self, data: bytes) -> None:
        self.d = data
        self.i = 0

    def byte(self) -> int:
        b = self.d[self.i]
        self.i += 1
        return b

    def varuint(self) -> int:
        value = shift = 0
        while True:
            b = self.byte()
            value |= (b & 127) << shift
            shift += 7
            if not b & 128 or shift >= 35:
                return value & 0xFFFFFFFF

    def varint(self) -> int:
        v = self.varuint()
        return ~(v >> 1) if v & 1 else v >> 1

    def float(self) -> float:
        first = self.byte()
        if first == 0:
            return 0.0
        bits = first | self.byte() << 8 | self.byte() << 16 | self.byte() << 24
        bits = (bits << 23 | bits >> 9) & 0xFFFFFFFF
        return struct.unpack("<f", struct.pack("<I", bits))[0]

    def string(self) -> str:
        start = self.i
        while self.d[self.i]:
            self.i += 1
        s = self.d[start : self.i].decode("utf-8", errors="replace")
        self.i += 1
        return s


@dataclass(frozen=True)
class Field:
    name: str
    type: int
    is_array: bool
    value: int


@dataclass
class Definition:
    name: str
    kind: int
    fields: list[Field]

    def __post_init__(self) -> None:
        self.by_id = {f.value: f for f in self.fields}


def _parse_schema(data: bytes) -> list[Definition]:
    r = Reader(data)
    defs = []
    for _ in range(r.varuint()):
        name, kind = r.string(), r.byte()
        fields = [
            Field(r.string(), r.varint(), r.byte() != 0, r.varuint())
            for _ in range(r.varuint())
        ]
        defs.append(Definition(name, kind, fields))
    return defs


class Decoder:
    """Decodes kiwi messages against a schema read from the same file."""

    def __init__(self, defs: list[Definition]) -> None:
        self.defs = defs
        self.by_name = {d.name: i for i, d in enumerate(defs)}

    def _value(self, r: Reader, type_: int) -> Any:
        if type_ >= 0:
            return self._definition(r, type_)
        return {
            -1: lambda: r.byte() != 0,
            -2: r.byte,
            -3: r.varint,
            -4: r.varuint,
            -5: r.float,
            -6: r.string,
        }[type_]()

    def _field(self, r: Reader, f: Field) -> Any:
        if f.is_array:
            return [self._value(r, f.type) for _ in range(r.varuint())]
        return self._value(r, f.type)

    def _definition(self, r: Reader, index: int) -> Any:
        d = self.defs[index]
        if d.kind == KIND_ENUM:
            v = r.varuint()
            f = d.by_id.get(v)
            return f.name if f else v
        if d.kind == KIND_STRUCT:
            return {f.name: self._field(r, f) for f in d.fields}
        out: dict[str, Any] = {}
        while True:
            fid = r.varuint()
            if fid == 0:
                return out
            f = d.by_id.get(fid)
            if f is None:
                raise ValueError(f"unknown field id {fid} in {d.name}")
            out[f.name] = self._field(r, f)

    def decode(self, data: bytes, root: str = "Message") -> dict[str, Any]:
        return self._definition(Reader(data), self.by_name[root])


def _decompress(chunk: bytes) -> bytes:
    if chunk[:4] == ZSTD_MAGIC:
        import zstandard

        return zstandard.ZstdDecompressor().decompressobj().decompress(chunk)
    return zlib.decompressobj(-zlib.MAX_WBITS).decompress(chunk)


def load_document(path: Path) -> dict[str, Any]:
    """Return the decoded Figma document message for a ``.fig`` archive."""
    with zipfile.ZipFile(path) as z:
        raw = z.read("canvas.fig")
    if raw[:8] != b"fig-kiwi":
        raise ValueError(f"{path} is not a fig-kiwi document")
    blocks, i = [], 12
    while i + 4 <= len(raw):
        (n,) = struct.unpack_from("<I", raw, i)
        i += 4
        if not n or i + n > len(raw):
            break
        blocks.append(_decompress(raw[i : i + n]))
        i += n
    return Decoder(_parse_schema(blocks[0])).decode(blocks[1])


def _guid(g: dict | None) -> tuple[int, int] | None:
    return (g["sessionID"], g["localID"]) if g else None


def _css_color(value: dict) -> str | None:
    c = value.get("colorValue")
    if not c:
        return None
    r, g, b = (round(c[k] * 255) for k in "rgb")
    a = c.get("a", 1.0)
    return f"rgba({r}, {g}, {b}, {a:.2f})" if a < 1 else f"#{r:02X}{g:02X}{b:02X}"


def collect_variables(nodes: list[dict]) -> dict[str, dict[str, Any]]:
    """Group Figma variables by their variable-set name."""
    sets = {
        _guid(n["guid"]): n.get("name")
        for n in nodes
        if n.get("type") == "VARIABLE_SET"
    }
    grouped: dict[str, dict[str, Any]] = defaultdict(dict)
    for n in nodes:
        if n.get("type") != "VARIABLE":
            continue
        set_name = sets.get(_guid((n.get("variableSetID") or {}).get("guid")), "?")
        css = next(
            (
                e.get("value")
                for e in (n.get("codeSyntax") or {}).get("entries") or []
                if e.get("platform") == "WEB"
            ),
            None,
        )
        values = []
        for e in (n.get("variableDataValues") or {}).get("entries") or []:
            value = (e.get("variableData") or {}).get("value") or {}
            rendered = _css_color(value)
            if rendered is None and "floatValue" in value:
                rendered = value["floatValue"]
            if rendered is not None:
                values.append(rendered)
        grouped[set_name][n["name"]] = {"css": css, "values": values}
    return dict(grouped)


def _token_name(figma_name: str) -> str:
    """``color/bg-subtle`` -> ``--bg-subtle``; ``spacing/4`` -> ``--space-4``."""
    group, _, leaf = figma_name.partition("/")
    groups = {"color": "", "spacing": "space-", "radius": "radius-"}
    prefix = groups.get(group, f"{group}-")
    return f"--{prefix}{leaf}"


def render_css(variables: dict[str, dict[str, Any]]) -> str:
    """Emit CSS custom properties with a light default and a dark override."""
    light = variables.get(LIGHT_SET, {})
    dark = variables.get(DARK_SET, {})
    lines = [
        "/* Generated by tools/figma_extract.py from the BZE Figma design system.",
        "   Do not edit by hand - re-run the extractor instead. */",
        "",
        ":root {",
        "  /* Farben - Light Mode */",
    ]
    for name, t in light.items():
        if t["values"]:
            lines.append(f"  {_token_name(name)}: {t['values'][0]};")
    lines.append("")
    lines.append("  /* Abstaende */")
    for name, t in variables.get(SPACING_SET, {}).items():
        if t["values"]:
            lines.append(f"  {_token_name(name)}: {float(t['values'][0]) / 16:g}rem;")
    lines.append("")
    lines.append("  /* Radien */")
    for name, t in variables.get(RADIUS_SET, {}).items():
        if t["values"]:
            lines.append(f"  {_token_name(name)}: {float(t['values'][0]):g}px;")
    lines += [
        "",
        "  /* Typografie - Inter ist die Hausschrift des Designsystems */",
        '  --font-sans: "Inter", "Segoe UI", system-ui, -apple-system, sans-serif;',
        "}",
        "",
        "/* Dark Mode: folgt der Systemeinstellung, laesst sich per",
        "   data-theme am <html> uebersteuern. */",
        "@media (prefers-color-scheme: dark) {",
        "  :root:not([data-theme='light']) {",
    ]
    for name, t in dark.items():
        if t["values"]:
            lines.append(f"    {_token_name(name)}: {t['values'][0]};")
    lines += ["  }", "}", "", ":root[data-theme='dark'] {"]
    for name, t in dark.items():
        if t["values"]:
            lines.append(f"  {_token_name(name)}: {t['values'][0]};")
    lines += ["}", ""]
    return "\n".join(lines)


def render_screens(nodes: list[dict]) -> str:
    """Emit a markdown inventory of every page and top-level frame."""
    children: dict[tuple[int, int], list[dict]] = defaultdict(list)
    for n in nodes:
        parent = _guid((n.get("parentIndex") or {}).get("guid"))
        if parent:
            children[parent].append(n)
    frame_types = {"FRAME", "SECTION", "COMPONENT", "COMPONENT_SET"}
    lines = [
        "# Screen-Inventar (aus Figma extrahiert)",
        "",
        "Generiert von `tools/figma_extract.py`. Jede Zeile ist ein Top-Level-Frame",
        "im Figma-Designsystem und damit eine zu bauende Ansicht.",
        "",
    ]
    total = 0
    for page in (n for n in nodes if n.get("type") == "CANVAS"):
        frames = [
            f
            for f in children.get(_guid(page["guid"]), [])
            if f.get("type") in frame_types
        ]
        if not frames:
            continue
        lines += [f"## {page.get('name')}", ""]
        for f in frames:
            size = f.get("size") or {}
            dim = f" — {size['x']:.0f}x{size['y']:.0f}" if size.get("x") else ""
            lines.append(f"- [ ] {f.get('name')}{dim}")
            total += 1
        lines.append("")
    lines.insert(4, f"**{total} Frames insgesamt.**\n")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("fig", type=Path, help="Pfad zur .fig-Datei")
    p.add_argument("--css", type=Path, help="Zieldatei fuer die CSS-Tokens")
    p.add_argument("--screens", type=Path, help="Zieldatei fuer das Screen-Inventar")
    args = p.parse_args()

    nodes = load_document(args.fig)["nodeChanges"]
    print(f"{len(nodes)} Nodes dekodiert.")

    if args.css:
        variables = collect_variables(nodes)
        args.css.parent.mkdir(parents=True, exist_ok=True)
        args.css.write_text(render_css(variables), encoding="utf-8")
        sets_used = (LIGHT_SET, SPACING_SET, RADIUS_SET)
        count = sum(len(variables.get(s, {})) for s in sets_used)
        print(f"{count} Tokens -> {args.css}")
    if args.screens:
        args.screens.parent.mkdir(parents=True, exist_ok=True)
        args.screens.write_text(render_screens(nodes), encoding="utf-8")
        print(f"Screen-Inventar -> {args.screens}")


if __name__ == "__main__":
    main()
