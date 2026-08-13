from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
pairs = [
    ("/lernen/fragen", "figma-04-3.png", "live-04-3.png"),
    ("/lernen/fragen/fehler", "figma-04-4.png", "live-04-4.png"),
    ("/lernen/frage", "figma-04-5.png", "live-04-5.png"),
    ("/lernen/frage/freitext", None, "live-04-6.png"),
    ("/lernen/feedback/richtig", "figma-04-7.png", "live-04-7.png"),
    ("/lernen/feedback/falsch", "figma-04-8.png", "live-04-8.png"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(800)
    for path, figma_name, live_name in pairs:
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(400)
        page.screenshot(path=str(out / live_name), full_page=False)
        if figma_name and (out / figma_name).exists():
            figma = Image.open(out / figma_name).convert("RGB")
            live = Image.open(out / live_name).convert("RGB")
            figma = figma.resize(live.size, Image.Resampling.LANCZOS)
            a = np.asarray(figma, dtype=np.float32)
            b = np.asarray(live, dtype=np.float32)
            diff = np.abs(a - b).mean(axis=2)
            pct = float((diff > 30).mean() * 100)
            mae = float(diff.mean())
            heat = np.clip(diff * 3, 0, 255).astype(np.uint8)
            Image.fromarray(heat).save(out / f"diff-{live_name}")
            print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f}")
        else:
            print(f"{path}: screenshot only -> {live_name}")
    browser.close()
