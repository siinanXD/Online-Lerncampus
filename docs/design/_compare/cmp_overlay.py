from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent
pairs = [
    ("/lernen/melden", "figma-04-9.png", "live-04-9.png"),
    ("/lernen/uebersetzung", "figma-04-10.png", "live-04-10.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)
    for path, figma_name, live_name in pairs:
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(out / live_name), full_page=False)
        figma = Image.open(out / figma_name).convert("RGB")
        live = Image.open(out / live_name).convert("RGB")
        figma = figma.resize(live.size, Image.Resampling.LANCZOS)
        a = np.asarray(figma, dtype=np.float32)
        b = np.asarray(live, dtype=np.float32)
        diff = np.abs(a - b).mean(axis=2)
        pct = float((diff > 30).mean() * 100)
        mae = float(diff.mean())
        print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f}")
        Image.fromarray(np.clip(diff * 3, 0, 255).astype(np.uint8)).save(out / f"diff-{live_name}")
    browser.close()
