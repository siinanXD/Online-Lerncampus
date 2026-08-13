"""Compare live 19.x gx hubs vs Figma screenshots; print pixel deltas."""
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

OUT = Path(__file__).resolve().parent
PAIRS = [
    ("/dashboard", "figma-19-1.png", "live-gx-dashboard.png", "diff-live-19-1.png", 402, 874),
    ("/lernen", "figma-19-2.png", "live-gx-lernen.png", "diff-live-19-2.png", 402, 941),
    ("/pruefungen", "figma-19-3.png", "live-gx-pruefungen.png", "diff-live-19-3.png", 402, 874),
    ("/fortschritt", "figma-19-4.png", "live-gx-fortschritt.png", "diff-live-19-4.png", 402, 943),
    ("/mehr", "figma-19-5.png", "live-gx-mehr.png", "diff-live-19-5.png", 402, 910),
]


def delta(figma_path: Path, live_path: Path, diff_path: Path):
    figma = Image.open(figma_path).convert("RGB")
    live = Image.open(live_path).convert("RGB")
    if figma.size != live.size:
        figma = figma.resize(live.size, Image.Resampling.LANCZOS)
    a = np.asarray(figma, dtype=np.float32)
    b = np.asarray(live, dtype=np.float32)
    d = np.abs(a - b).mean(axis=2)
    pct = float((d > 30).mean() * 100)
    mae = float(d.mean())
    Image.fromarray(np.clip(d * 3, 0, 255).astype(np.uint8)).save(diff_path)
    return pct, mae


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(viewport={"width": 430, "height": 1100}, device_scale_factor=1)
    page = context.new_page()
    page.goto("http://127.0.0.1:8000/login", wait_until="domcontentloaded")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(1000)
    if "/onboarding" in page.url:
        page.goto("http://127.0.0.1:8000/dashboard", wait_until="domcontentloaded")
        page.wait_for_timeout(600)

    for path, figma_name, live_name, diff_name, w, h in PAIRS:
        page.goto(f"http://127.0.0.1:8000{path}", wait_until="domcontentloaded")
        page.wait_for_selector(".gx-screen", timeout=10000)
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(500)
        page.evaluate(
            """([w, h]) => {
              const frame = document.querySelector('.app-frame');
              if (frame) {
                frame.style.width = w + 'px';
                frame.style.height = h + 'px';
                frame.style.minHeight = h + 'px';
                frame.style.maxWidth = w + 'px';
              }
            }""",
            [w, h],
        )
        page.wait_for_timeout(200)
        page.locator(".app-frame").screenshot(path=str(OUT / live_name))
        pct, mae = delta(OUT / figma_name, OUT / live_name, OUT / diff_name)
        print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f} size={w}x{h}")

    browser.close()
