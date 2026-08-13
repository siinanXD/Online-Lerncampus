"""Compare live vs Figma for Lernen feedback + new frames."""
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
pairs = [
    ("/lernen/feedback/richtig", "figma-04-7.png", "live-04-7.png", 844),
    ("/lernen/feedback/falsch", "figma-04-8.png", "live-04-8.png", 844),
    ("/lernen/uebersetzung", "figma-04-10.png", "live-04-10.png", 844),
    ("/lernen/fehlerdiagnose", "figma-04-12.png", "live-04-12.png", 844),
    ("/lernen/video", "figma-04-13.png", "live-04-13.png", 905),
    ("/lernen/detail", "figma-04-14.png", "live-04-14.png", 844),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 920}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(800)
    for path, figma_name, live_name, h in pairs:
        page.set_viewport_size({"width": 390, "height": h})
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(400)
        clip = page.evaluate(
            """(h) => {
              const phone = document.querySelector('.app-frame');
              if (!phone) return null;
              const r = phone.getBoundingClientRect();
              return {x: r.x, y: r.y, width: r.width, height: Math.min(r.height, h)};
            }""",
            h,
        )
        page.screenshot(path=str(out / live_name), clip=clip if clip else None)
        figma_path = out / figma_name
        if figma_path.exists():
            figma = Image.open(figma_path).convert("RGB")
            live = Image.open(out / live_name).convert("RGB")
            figma = figma.resize(live.size, Image.Resampling.LANCZOS)
            a = np.asarray(figma, dtype=np.float32)
            b = np.asarray(live, dtype=np.float32)
            diff = np.abs(a - b).mean(axis=2)
            pct = float((diff > 30).mean() * 100)
            mae = float(diff.mean())
            Image.fromarray(np.clip(diff * 3, 0, 255).astype(np.uint8)).save(
                out / f"diff-{live_name}"
            )
            print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f} size={live.size}")
        else:
            print(f"{path}: screenshot only (no figma)")
    browser.close()
