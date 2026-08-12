"""Mark implemented product screens in docs/design/screens.md."""

from __future__ import annotations

import json
import re
from pathlib import Path

catalog = json.loads(Path("work/screen_catalog.json").read_text(encoding="utf-8"))
implemented_nums = {screen["num"] for screen in catalog["screens"]}
implemented_nums.update({"02.1", "02.2", "10.1", "10.2", "14.1"})

skip_titles = ("Design Canvas", "Showcase", "Dokumentation", "Palette", "Typography", "Components", "States", "Icon Set", "Accessibility", "Micro-Interactions", "Illustrations", "Illustration")

path = Path("docs/design/screens.md")
lines = path.read_text(encoding="utf-8").splitlines()
out: list[str] = []
for line in lines:
    match = re.match(r"^- \[[ x]\] (\d{2}\.\d+(?:\.\d+)?)\s+(.+)$", line)
    if not match:
        out.append(line)
        continue
    num = match.group(1)
    title = match.group(2)
    section = int(num.split(".")[0])
    if section == 0 or section == 17 or any(token in title for token in skip_titles):
        out.append(re.sub(r"^- \[[ x]\]", "- [ ]", line))
        continue
    if num in implemented_nums:
        out.append(re.sub(r"^- \[[ x]\]", "- [x]", line))
    else:
        out.append(line)

path.write_text("\n".join(out) + "\n", encoding="utf-8")
checked = sum(1 for line in out if line.startswith("- [x]"))
unchecked = sum(1 for line in out if line.startswith("- [ ]"))
print(f"checked={checked} unchecked={unchecked}")
