from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)
    page.goto("http://127.0.0.1:8000/lernen/fehlerdiagnose", wait_until="networkidle")
    page.wait_for_timeout(400)
    clip = page.evaluate(
        """() => {
          const r = document.querySelector('.app-frame').getBoundingClientRect();
          return {x: r.x, y: r.y, width: r.width, height: Math.min(r.height, 844)};
        }"""
    )
    page.screenshot(path=str(out / "live-04-12.png"), clip=clip)
    figma = Image.open(out / "figma-04-12.png").convert("RGB").resize((390, 844), Image.Resampling.LANCZOS)
    live = Image.open(out / "live-04-12.png").convert("RGB")
    a = np.asarray(figma, dtype=np.float32)
    b = np.asarray(live, dtype=np.float32)
    d = np.abs(a - b).mean(axis=2)
    print(f"04.12 pixel_delta={float((d > 30).mean() * 100):.2f}% mae={float(d.mean()):.1f}")
    Image.fromarray(np.clip(d * 3, 0, 255).astype(np.uint8)).save(out / "diff-live-04-12.png")
    browser.close()
