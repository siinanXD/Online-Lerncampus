# -*- coding: utf-8 -*-
from pathlib import Path
import urllib.request

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent

figma_urls = {
    "figma-09-3.png": "https://www.figma.com/api/mcp/asset/45def155-fb58-4323-8cf9-8cdbb7d0e02c.png",
    "figma-09-4.png": "https://www.figma.com/api/mcp/asset/81bf7e4c-8747-49f3-8264-b1c20ea4fd2a.png",
    "figma-09-5.png": "https://www.figma.com/api/mcp/asset/49e90b78-0916-4bdd-bb89-adebc95a9350.png",
    "figma-09-6.png": "https://www.figma.com/api/mcp/asset/0cf44a74-70ec-4d52-9216-5247e2d8db68.png",
}

for name, url in figma_urls.items():
    path = out / name
    urllib.request.urlretrieve(url, path)
    print(f"figma {name} {path.stat().st_size}")

pairs = [
    ("/mehr/coach", "figma-09-3.png", "live-09-3.png", 844),
    ("/mehr/lernplan", "figma-09-4.png", "live-09-4.png", 844),
    ("/mehr/export", "figma-09-5.png", "live-09-5.png", 846),
    ("/mehr/loeschen", "figma-09-6.png", "live-09-6.png", 844),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 900}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill("input[name=identifier]", "demo-azubi")
    page.fill("input[name=password]", "demo-pass")
    page.click("button[type=submit]")
    page.wait_for_timeout(900)

    for path, figma_name, live_name, h in pairs:
        page.set_viewport_size({"width": 390, "height": h + 40})
        page.goto(f"http://127.0.0.1:8000{path}", wait_until="networkidle")
        page.wait_for_timeout(500)
        frame = page.query_selector(".app-frame")
        if frame:
            # force phone height if needed
            page.evaluate(
                """(h) => {
                  const f = document.querySelector('.app-frame');
                  if (f) { f.style.height = h + 'px'; f.style.minHeight = h + 'px'; }
                }""",
                h,
            )
            frame.screenshot(path=str(out / live_name))
        else:
            page.screenshot(path=str(out / live_name), clip={"x": 0, "y": 0, "width": 390, "height": h})

        figma = Image.open(out / figma_name).convert("RGB")
        live = Image.open(out / live_name).convert("RGB")
        if figma.size != live.size:
            figma = figma.resize(live.size, Image.Resampling.LANCZOS)
        a = np.asarray(figma, dtype=np.float32)
        b = np.asarray(live, dtype=np.float32)
        diff = np.abs(a - b).mean(axis=2)
        pct = float((diff > 30).mean() * 100)
        mae = float(diff.mean())
        heat = np.clip(diff * 3, 0, 255).astype(np.uint8)
        Image.fromarray(heat).save(out / f"diff-{live_name}")
        chrome = page.evaluate("() => document.querySelector('.app-frame')?.dataset.chrome || ''")
        print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f} size={live.size} chrome={chrome}")
    browser.close()
