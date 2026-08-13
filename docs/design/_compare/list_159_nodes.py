"""List all 159:* nodes from overview metadata dump."""
import re
from pathlib import Path

t = Path(
    r"C:\Users\sinan\.cursor\projects\c-dev-Repositories-Online-Lerncampus"
    r"\agent-tools\903ae17d-bda8-4d37-bd21-945c18114b56.txt"
).read_text(encoding="utf-8")

print("=== 159:* frames ===")
for m in re.finditer(
    r'<frame id="(159:[^"]+)" name="([^"]+)" x="([^"]+)" y="([^"]+)" '
    r'width="([^"]+)" height="([^"]+)"',
    t,
):
    print(f"{m.group(1)}\t{m.group(5)}x{m.group(6)}\t{m.group(2)[:80]}")

print("\n=== 159:* large (>=350x600) any type ===")
for m in re.finditer(
    r"<(frame|instance|component|section) id=\"(159:[^\"]+)\" name=\"([^\"]+)\"[^>]*"
    r'width="([^"]+)" height="([^"]+)"',
    t,
):
    w, h = float(m.group(4)), float(m.group(5))
    if w >= 350 and h >= 600:
        print(f"{m.group(2)}\t{m.group(1)}\t{w}x{h}\t{m.group(3)[:80]}")

# Context around Gamification section: find 136:18709 and nearby 159 parents
print("\n=== parents of named participant screens ===")
for name in (
    "home-dashboard",
    "lernen-journey",
    "pruefung-hub",
    "fortschritt-stats",
    "profil-settings",
):
    idx = t.find(f'name="{name}"')
    if idx < 0:
        print(f"MISSING {name}")
        continue
    # walk back for enclosing frame with NN.N or screen-like name
    window = t[max(0, idx - 2000) : idx + 200]
    parents = re.findall(
        r'<(?:frame|section) id="([^"]+)" name="([^"]+)"', window
    )
    print(f"{name}: last parents {parents[-5:]}")
