from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
pairs = [
    ("/lernen/feedback/richtig", "figma-04-7.png", "live-04-7.png"),
    ("/lernen/feedback/falsch", "figma-04-8.png", "live-04-8.png"),
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
    page.wait_for_timeout(800)
    for path, figma_name, live_name in pairs:
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(500)
        # Prefer phone frame if present
        clip = page.evaluate(
            """() => {
              const phone = document.querySelector('.app-frame') || document.querySelector('.auth-phone');
              if (!phone) return null;
              const r = phone.getBoundingClientRect();
              return {x: r.x, y: r.y, width: r.width, height: Math.min(r.height, 844)};
            }"""
        )
        if clip and clip["width"] > 0:
            page.screenshot(path=str(out / live_name), clip=clip)
        else:
            page.screenshot(path=str(out / live_name), full_page=False)
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
        print(f"{path}: size={live.size} pixel_delta={pct:.2f}% mae={mae:.1f}")
        # band analysis
        h = live.size[1]
        bands = [("top", 0, 80), ("mid", 80, 420), ("sheet", 420, h)]
        for name, y0, y1 in bands:
            band = diff[y0:y1, :]
            bp = float((band > 30).mean() * 100)
            print(f"  {name}: {bp:.2f}%")
    browser.close()
