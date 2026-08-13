from pathlib import Path

import numpy as np
from PIL import Image

out = Path(__file__).resolve().parent


def find_blue_button(path: str, label: str) -> None:
    im = Image.open(out / path).convert("RGB")
    # scale to 390 if needed
    if im.size[0] != 390:
        im = im.resize((390, 844), Image.Resampling.LANCZOS)
    arr = np.asarray(im)
    # strong blue-ish primary button
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    mask = (b > 180) & (r < 120) & (g < 140) & (b > r + 40)
    rows = np.where(mask.mean(axis=1) > 0.15)[0]
    if len(rows) == 0:
        print(label, "no button rows")
        return
    print(label, "button y", int(rows.min()), "-", int(rows.max()), "size", im.size)


find_blue_button("figma-01-2-passwort.png", "figma-pw")
find_blue_button("live-passwort.png", "live-pw")
find_blue_button("figma-01-3-sprache.png", "figma-lang")
find_blue_button("live-sprache.png", "live-lang")
find_blue_button("figma-01-4-onboarding.png", "figma-ob")
find_blue_button("live-onboarding.png", "live-ob")
