"""Minimal PDF 1.4 writer for Berichtsheft export (no third-party deps)."""

from __future__ import annotations


def _pdf_escape(text: str) -> str:
    """Escape parentheses and backslashes for PDF string literals."""
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
        .replace("\r", "")
    )


def _wrap_lines(title: str, paragraphs: list[str], width: int = 92) -> list[str]:
    """Wrap plain text into Helvetica-safe lines."""
    lines: list[str] = [title, ""]
    for paragraph in paragraphs:
        chunks = paragraph.replace("\r", "").split("\n") or [""]
        for raw in chunks:
            text = raw if raw else " "
            while len(text) > width:
                cut = text.rfind(" ", 0, width)
                if cut < width // 3:
                    cut = width
                lines.append(text[:cut])
                text = text[cut:].lstrip() or ""
            if text:
                lines.append(text)
        lines.append("")
    return lines


def build_simple_pdf(title: str, paragraphs: list[str]) -> bytes:
    """Return a multi-page Helvetica PDF for the given paragraphs."""
    lines = _wrap_lines(title, paragraphs)
    per_page = 48
    pages = [lines[index : index + per_page] for index in range(0, len(lines), per_page)]
    if not pages:
        pages = [[title]]

    objects: list[bytes] = [b""]  # 1-indexed
    page_ids: list[int] = []
    content_ids: list[int] = []

    def add_object(body: bytes) -> int:
        objects.append(body)
        return len(objects) - 1

    font_id = add_object(
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
    )
    for _ in pages:
        page_ids.append(add_object(b""))
        content_ids.append(add_object(b""))

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    pages_id = add_object(
        f"<< /Type /Pages /Kids [{kids}] /Count {len(page_ids)} >>".encode("latin-1")
    )
    catalog_id = add_object(f"<< /Type /Catalog /Pages {pages_id} 0 R >>".encode("latin-1"))

    for index, chunk in enumerate(pages):
        commands = ["BT", "/F1 11 Tf", "50 780 Td", "14 TL"]
        for line in chunk:
            safe = _pdf_escape(line.encode("latin-1", "replace").decode("latin-1"))
            commands.append(f"({safe}) Tj")
            commands.append("T*")
        commands.append("ET")
        stream = "\n".join(commands).encode("latin-1")
        content_ids_index = content_ids[index]
        objects[content_ids_index] = (
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"\nendstream"
        )
        objects[page_ids[index]] = (
            f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> "
            f"/Contents {content_ids_index} 0 R >>"
        ).encode("latin-1")

    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj_id, body in enumerate(objects):
        if obj_id == 0:
            continue
        offsets.append(len(out))
        out.extend(f"{obj_id} 0 obj\n".encode("latin-1"))
        out.extend(body)
        out.extend(b"\nendobj\n")
    xref_pos = len(out)
    out.extend(f"xref\n0 {len(objects)}\n".encode("latin-1"))
    out.extend(b"0000000000 65535 f \n")
    for obj_id in range(1, len(objects)):
        out.extend(f"{offsets[obj_id]:010d} 00000 n \n".encode("latin-1"))
    out.extend(
        (
            f"trailer << /Size {len(objects)} /Root {catalog_id} 0 R >>\n"
            f"startxref\n{xref_pos}\n%%EOF\n"
        ).encode("latin-1")
    )
    return bytes(out)
