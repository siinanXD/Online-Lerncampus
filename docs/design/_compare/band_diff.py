from pathlib import Path

import numpy as np
from PIL import Image

out = Path(__file__).resolve().parent


def analyze(figma_name: str, live_name: str, bands: int = 8) -> None:
    figma = Image.open(out / figma_name).convert("RGB")
    live = Image.open(out / live_name).convert("RGB")
    figma = figma.resize(live.size, Image.Resampling.LANCZOS)
    a = np.asarray(figma, dtype=np.float32)
    b = np.asarray(live, dtype=np.float32)
    diff = np.abs(a - b).mean(axis=2)
    h = diff.shape[0]
    print(f"=== {live_name} ===")
    for i in range(bands):
        y0 = h * i // bands
        y1 = h * (i + 1) // bands
        band = diff[y0:y1]
        pct = float((band > 30).mean() * 100)
        print(f"  y {y0:3d}-{y1:3d}: delta={pct:5.2f}% mae={band.mean():5.1f}")


analyze("figma-01-2-passwort.png", "live-passwort.png")
analyze("figma-01-3-sprache.png", "live-sprache.png")
analyze("figma-01-4-onboarding.png", "live-onboarding.png")
