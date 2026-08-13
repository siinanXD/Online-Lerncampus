# -*- coding: utf-8 -*-
"""Compare tightened Mehr screens vs Figma."""
from pathlib import Path
import urllib.request

import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(__file__).resolve().parent

# Fresh screenshots from get_screenshot / get_design_context in this session
figma_urls = {
    "figma-09-4.png": "https://www.figma.com/api/mcp/asset/95e5d551-9cdb-41db-8a91-e9b2897588a7.png",
    "figma-09-5.png": None,  # filled below after fetch
    "figma-09-1b.png": None,
    "figma-09-1d.png": None,
}

pairs = [
    ("/mehr/lernplan", "figma-09-4.png", "live-09-4.png", 844),
    ("/mehr/export", "figma-09-5.png", "live-09-5.png", 846),
    ("/mehr/profil", "figma-09-1b.png", "live-09-1b.png", 844),
    ("/mehr/benachrichtigungen", "figma-09-1d.png", "live-09-1d.png", 844),
]

# Prefer already-downloaded figma-09-4; others must be passed via env or existing files
for name, url in list(figma_urls.items()):
    path = out / name
    if url and (not path.exists() or path.stat().st_size < 1000):
        urllib.request.urlretrieve(url, path)
        print(f"downloaded {name} {path.stat().st_size}")
    elif path.exists():
        print(f"reuse {name} {path.stat().st_size}")
    else:
        print(f"MISSING {name}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 900}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill("input[name=identifier]", "demo-azubi")
    page.fill("input[name=password]", "demo-pass")
    page.click("button[type=submit]")
    page.wait_for_timeout(900)

    for path, figma_name, live_name, h in pairs:
        figma_path = out / figma_name
        if not figma_path.exists() or figma_path.stat().st_size < 1000:
            print(f"skip {path}: no figma {figma_name}")
            continue
        page.set_viewport_size({"width": 390, "height": h + 40})
        page.goto(f"http://127.0.0.1:8000{path}", wait_until="networkidle")
        page.wait_for_timeout(600)
        frame = page.query_selector(".app-frame")
        if frame:
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

        figma = Image.open(figma_path).convert("RGB")
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
