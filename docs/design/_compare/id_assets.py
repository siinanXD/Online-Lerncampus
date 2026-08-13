# -*- coding: utf-8 -*-
from pathlib import Path

out = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\figma\fp")
for p in sorted(out.glob("fp-st-*.svg")) + sorted(out.glob("fp-xs-*.svg")) + sorted(out.glob("fp-hm-*.svg")):
    t = p.read_text(encoding="utf-8", errors="replace")
    view = ""
    if "viewBox" in t:
        i = t.find("viewBox")
        view = t[i : i + 50]
    snip = t.replace("\n", " ")[:200]
    print(f"{p.name} len={len(t)} {view}")
    print(f"  {snip}")
