"""Locate parent section of new 159 participant screens in overview."""
import re
from pathlib import Path

t = Path(
    r"C:\Users\sinan\.cursor\projects\c-dev-Repositories-Online-Lerncampus"
    r"\agent-tools\9fba5c9c-f3ef-4699-9b08-f57d0f33f0b0.txt"
).read_text(encoding="utf-8")

# Find position of 159:13 and look at section stack
idx = t.find('id="159:13"')
print("159:13 at", idx)
# find all section opens/closes before this - approximate with last section open
before = t[:idx]
secs = list(re.finditer(r'<section id="([^"]+)" name="([^"]+)"', before))
print("last section before 159:13:", secs[-1].groups() if secs else None)

# Labels near the phones
window = t[idx - 800 : idx + 200]
texts = re.findall(r'<text id="([^"]+)" name="([^"]+)"', window)
print("nearby texts:", texts[-15:])

# List the five root phones and neighbors
for nid in ("159:13", "159:129", "159:229", "159:320", "159:456"):
    m = re.search(
        rf'<frame id="{nid}" name="([^"]+)" x="([^"]+)" y="([^"]+)" '
        rf'width="([^"]+)" height="([^"]+)"',
        t,
    )
    if m:
        print(nid, m.groups())

# Any other top-level-ish 159 phones or new NN frames after inventory date
print("\n=== frames with id starting 159 that are product roots ===")
for m in re.finditer(
    r'<frame id="(159:\d+)" name="([^"]+)" x="([^"]+)" y="([^"]+)" '
    r'width="([^"]+)" height="([^"]+)"',
    t,
):
    w, h = float(m.group(5)), float(m.group(6))
    if w >= 390 and h >= 800 and m.group(2) not in (
        "scroll-container",
        "body-content",
        "path-container",
    ):
        print(m.group(1), f"{w}x{h}", m.group(2), f"@({m.group(3)},{m.group(4)})")

# Compare checklist IDs vs Figma NN.N
checklist = Path(
    r"C:\dev\Repositories\Online-Lerncampus\docs\design\figma-136-2-checklist.md"
).read_text(encoding="utf-8")
ck = set(re.findall(r"`(136:\d+|159:\d+)`", checklist))
fig_nn = {
    m.group(1)
    for m in re.finditer(
        r'<frame id="([^"]+)" name="(\d{2}\.\d+[^\"]*)"', t
    )
}
print("\nchecklist nodes", len(ck), "fig NN frames", len(fig_nn))
print("NN in figma not checklist", sorted(fig_nn - ck)[:30], "count", len(fig_nn - ck))
print("159 in checklist", [x for x in ck if x.startswith("159:")])
