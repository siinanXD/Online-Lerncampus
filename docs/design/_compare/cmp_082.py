# -*- coding: utf-8 -*-
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 430, "height": 1400}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)
    page.goto("http://127.0.0.1:8000/berichtsheft/neu", wait_until="networkidle")
    page.wait_for_timeout(600)
    clip = page.evaluate(
        """() => {
          const r = document.querySelector('.app-frame').getBoundingClientRect();
          return {x:r.x,y:r.y,width:r.width,height:Math.min(r.height,1211)};
        }"""
    )
    page.screenshot(path=str(out / "live-08-2.png"), clip=clip)
    f = Image.open(out / "figma-08-2.png").convert("RGB")
    l = Image.open(out / "live-08-2.png").convert("RGB")
    f = f.resize(l.size, Image.Resampling.LANCZOS)
    d = np.abs(np.asarray(f, np.float32) - np.asarray(l, np.float32)).mean(axis=2)
    print(f"08.2 pixel_delta={(d > 30).mean()*100:.2f}% mae={d.mean():.1f} live={l.size}")
    heat = np.asarray(l).copy()
    heat[d > 30] = [255, 40, 40]
    Image.fromarray(heat).save(out / "diff-live-08-2.png")
    b.close()
