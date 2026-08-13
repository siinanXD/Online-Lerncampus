# -*- coding: utf-8 -*-
"""Diff Figma overview metadata vs checklist node IDs."""
import re
from pathlib import Path

meta_path = Path(r"C:\Users\sinan\.cursor\projects\c-dev-Repositories-Online-Lerncampus\agent-tools\903ae17d-bda8-4d37-bd21-945c18114b56.txt")
checklist_path = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\figma-136-2-checklist.md")

meta = meta_path.read_text(encoding="utf-8", errors="replace")
checklist = checklist_path.read_text(encoding="utf-8", errors="replace")

checklist_ids = set(re.findall(r"`(\d+:\d+)`", checklist))

frames = []
# Prefer XML-ish attrs: id= name= width= height=
for m in re.finditer(r"<(?:frame|FRAME)\b([^>]*)>", meta, re.I):
    attrs = m.group(1)
    idm = re.search(r'\bid="([^"]+)"', attrs)
    nm = re.search(r'\bname="([^"]+)"', attrs)
    wm = re.search(r'\bwidth="([^"]+)"', attrs)
    hm = re.search(r'\bheight="([^"]+)"', attrs)
    if not (idm and nm):
        continue
    name = nm.group(1)
    # Top-level product screens typically named NN.N ...
    if re.match(r"^\d{2}\.\d+", name):
        frames.append(
            (
                idm.group(1),
                name,
                float(wm.group(1)) if wm else 0,
                float(hm.group(1)) if hm else 0,
            )
        )

# dedupe by id, keep first
seen = set()
uniq = []
for f in frames:
    if f[0] in seen:
        continue
    seen.add(f[0])
    uniq.append(f)

print(f"CHECKLIST_IDS={len(checklist_ids)}")
print(f"FIGMA_NN_FRAMES={len(uniq)}")

new = [f for f in uniq if f[0] not in checklist_ids]
missing_in_figma = sorted(checklist_ids - {f[0] for f in uniq})

print("\n=== NEW in Figma (not in checklist) ===")
for nid, name, w, h in sorted(new, key=lambda x: x[1]):
    print(f"{nid}\t{int(w)}x{int(h)}\t{name}")

# Also surface participant-looking new frames (01-09, 18)
print("\n=== NEW participant-ish (01-09 / 18) ===")
for nid, name, w, h in sorted(new, key=lambda x: x[1]):
    if re.match(r"^(0[1-9]|18)\.", name):
        print(f"{nid}\t{int(w)}x{int(h)}\t{name}")

print("\n=== Checklist IDs not matching NN.N frame names (sample) ===")
print(f"count={len(missing_in_figma)}")
for nid in missing_in_figma[:30]:
    print(nid)

# Dump all NN frames for sections 01-09
print("\n=== ALL Figma 01-09 / 18 frames ===")
for nid, name, w, h in sorted(uniq, key=lambda x: x[1]):
    if re.match(r"^(0[1-9]|18)\.", name):
        mark = "NEW" if nid not in checklist_ids else "ok"
        print(f"{mark}\t{nid}\t{int(w)}x{int(h)}\t{name}")
