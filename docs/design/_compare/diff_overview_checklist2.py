# -*- coding: utf-8 -*-
import re
from pathlib import Path

meta = Path(
    r"C:\Users\sinan\.cursor\projects\c-dev-Repositories-Online-Lerncampus\agent-tools\903ae17d-bda8-4d37-bd21-945c18114b56.txt"
).read_text(encoding="utf-8", errors="replace")
checklist = Path(
    r"C:\dev\Repositories\Online-Lerncampus\docs\design\figma-136-2-checklist.md"
).read_text(encoding="utf-8", errors="replace")
cids = set(re.findall(r"`(\d+:\d+)`", checklist))

print("=== SECTIONS ===")
for m in re.finditer(r'<section id="([^"]+)" name="([^"]+)"[^>]*>', meta):
    print(m.group(1), m.group(2))

phone = []
for m in re.finditer(
    r'<frame id="([^"]+)" name="([^"]+)" x="[^"]+" y="[^"]+" width="([^"]+)" height="([^"]+)">',
    meta,
):
    nid, name, w, h = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
    if 380 <= w <= 400 and 800 <= h <= 1300:
        phone.append((nid, name, int(w), int(h)))

print("\nphone-ish frames", len(phone))
new_phone = [p for p in phone if p[0] not in cids]
print("phone not in checklist", len(new_phone))
for p in new_phone:
    print(f"{p[0]}\t{p[2]}x{p[3]}\t{p[1]}")

print("\n=== large frames not in checklist (name != Frame) ===")
large = []
for m in re.finditer(
    r'<frame id="([^"]+)" name="([^"]+)" x="[^"]+" y="[^"]+" width="([^"]+)" height="([^"]+)">',
    meta,
):
    nid, name, w, h = m.group(1), m.group(2), float(m.group(3)), float(m.group(4))
    if nid in cids:
        continue
    if name.lower() in {"frame", "group"}:
        continue
    if w >= 360 and h >= 700:
        large.append((nid, name, int(w), int(h)))

# Prefer names that look like screens
for p in sorted(large, key=lambda x: x[1]):
    print(f"{p[0]}\t{p[2]}x{p[3]}\t{p[1]}")

# Direct children of sections: frames with NN.N OR screen-ish that are first level under section
print("\n=== section direct child frames NEW ===")
# crude: find section blocks and first-level frame children by scanning lines
lines = meta.splitlines()
section = None
depth_stack = []
for line in lines:
    sm = re.match(r'^(\s*)<section id="([^"]+)" name="([^"]+)"', line)
    if sm:
        section = (sm.group(2), sm.group(3), len(sm.group(1)))
        continue
    fm = re.match(r'^(\s*)<frame id="([^"]+)" name="([^"]+)" x="[^"]+" y="[^"]+" width="([^"]+)" height="([^"]+)"', line)
    if fm and section:
        ind = len(fm.group(1))
        # section indent + 2 spaces typically
        if ind == section[2] + 2:
            nid = fm.group(2)
            name = fm.group(3)
            w, h = int(float(fm.group(4))), int(float(fm.group(5)))
            if nid not in cids and name.lower() != "frame":
                print(f"NEW under {section[1]}: {nid}\t{w}x{h}\t{name}")
