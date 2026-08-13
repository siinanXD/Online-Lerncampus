from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
screens = [
    ("05.2", "/fachkunde/lernpfad", "figma-05-2.png", "live-05-2.png", 1172),
    ("05.3", "/fachkunde/einheit", "figma-05-3.png", "live-05-3.png", 958),
    ("06.1", "/pruefungen", "figma-06-1.png", "live-06-1.png", 906),
    ("07.1", "/fortschritt", "figma-07-1.png", "live-07-1.png", 961),
    ("08.1", "/berichtsheft", "figma-08-1.png", "live-08-1.png", 1099),
]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 430, "height": 1300}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(800)

    for label, route, figma_name, live_name, h in screens:
        page.set_viewport_size({"width": 430, "height": max(h + 100, 1000)})
        page.goto(f"http://127.0.0.1:8000{route}", wait_until="networkidle")
        page.wait_for_timeout(500)
        clip = page.evaluate(
            f"""() => {{
              const r = document.querySelector('.app-frame').getBoundingClientRect();
              return {{x:r.x,y:r.y,width:r.width,height:Math.min(r.height,{h})}};
            }}"""
        )
        page.screenshot(path=str(out / live_name), clip=clip)
        f = Image.open(out / figma_name).convert("RGB")
        l = Image.open(out / live_name).convert("RGB")
        f_r = f.resize(l.size, Image.Resampling.LANCZOS)
        d = np.abs(np.asarray(f_r, np.float32) - np.asarray(l, np.float32)).mean(axis=2)
        print(
            f"{label} pixel_delta={(d > 30).mean() * 100:.2f}% mae={d.mean():.1f} "
            f"live={l.size}"
        )
        heat = np.asarray(l).copy()
        heat[d > 30] = [255, 40, 40]
        Image.fromarray(heat).save(out / f"diff-{live_name}")
    b.close()
