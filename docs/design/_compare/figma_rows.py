from pathlib import Path

import numpy as np
from PIL import Image

out = Path(__file__).resolve().parent
figma = Image.open(out / "figma-01-2-passwort.png").convert("RGB")
# center crop to 390
w, h = figma.size
left = max(0, (w - 390) // 2)
figma = figma.crop((left, 0, left + 390, h))
arr = np.asarray(figma)
# Find first non-white-ish rows in content columns to detect vertical structure
gray = arr.mean(axis=2)
# content mask: not near-white
content = gray < 250
row_density = content.mean(axis=1)
# print bands where content density jumps
prev = False
for y, d in enumerate(row_density):
    is_c = d > 0.02
    if is_c != prev:
        print(f"y={y}: content={is_c} density={d:.3f}")
        prev = is_c
