from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent

pairs = [
    ("/passwort", "figma-01-2-passwort.png", "live-passwort.png"),
    ("/sprache", "figma-01-3-sprache.png", "live-sprache.png"),
    ("/onboarding", "figma-01-4-onboarding.png", "live-onboarding.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    for path, figma_name, live_name in pairs:
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(300)
        page.screenshot(path=str(out / live_name), full_page=False)
        figma = Image.open(out / figma_name).convert("RGB")
        live = Image.open(out / live_name).convert("RGB")
        figma = figma.resize(live.size, Image.Resampling.LANCZOS)
        a = np.asarray(figma, dtype=np.float32)
        b = np.asarray(live, dtype=np.float32)
        diff = np.abs(a - b).mean(axis=2)
        pct = float((diff > 30).mean() * 100)
        mae = float(diff.mean())
        phone_h = page.evaluate(
            "() => document.querySelector('.auth-phone').getBoundingClientRect().height"
        )
        print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f} phone_h={phone_h:.0f}")
        heat = np.clip(diff * 3, 0, 255).astype(np.uint8)
        Image.fromarray(heat).save(out / f"diff-{live_name}")
    browser.close()
