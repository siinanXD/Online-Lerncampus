from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 390, "height": 895}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)
    page.goto("http://127.0.0.1:8000/fachkunde", wait_until="networkidle")
    page.wait_for_timeout(400)
    clip = page.evaluate(
        """() => {
          const r = document.querySelector('.app-frame').getBoundingClientRect();
          return {x:r.x,y:r.y,width:r.width,height:Math.min(r.height,895)};
        }"""
    )
    page.screenshot(path=str(out / "live-05-1.png"), clip=clip)
    f = Image.open(out / "figma-05-1.png").convert("RGB")
    l = Image.open(out / "live-05-1.png").convert("RGB")
    f = f.resize(l.size, Image.Resampling.LANCZOS)
    d = np.abs(np.asarray(f, np.float32) - np.asarray(l, np.float32)).mean(axis=2)
    print(f"05.1 pixel_delta={(d > 30).mean() * 100:.2f}% mae={d.mean():.1f} size={l.size}")
    b.close()
