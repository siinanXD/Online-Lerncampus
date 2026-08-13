from playwright.sync_api import sync_playwright
from PIL import Image
import numpy as np
from pathlib import Path

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)

    # sweep margin for 04.7
    best = None
    for mt in [-20, -25, -30, -35, -40, -45]:
        page.goto("http://127.0.0.1:8000/lernen/feedback/richtig", wait_until="networkidle")
        page.wait_for_timeout(200)
        page.add_style_tag(content=f".fb-play .fb-sheet.ok {{ margin-top: {mt}px !important; }}")
        page.wait_for_timeout(100)
        page.screenshot(path=str(out / "_tmp.png"), clip={"x": 0, "y": 0, "width": 390, "height": 844})
        f = np.asarray(Image.open(out / "figma-04-7.png").convert("RGB"), dtype=np.float32)
        l = np.asarray(Image.open(out / "_tmp.png").convert("RGB"), dtype=np.float32)
        if f.shape != l.shape:
            f = np.asarray(Image.open(out / "figma-04-7.png").convert("RGB").resize((l.shape[1], l.shape[0])), dtype=np.float32)
        diff = np.abs(f - l).mean(axis=2)
        pct = float((diff > 30).mean() * 100)
        print(f"04.7 mt={mt}: {pct:.2f}%")
        if best is None or pct < best[0]:
            best = (pct, mt)
    print("best", best)

    # measure 04.10
    page.goto("http://127.0.0.1:8000/lernen/uebersetzung", wait_until="networkidle")
    page.wait_for_timeout(300)
    print(page.evaluate("""() => {
      const s = document.querySelector('.uebersetz-sheet');
      const r = s.getBoundingClientRect();
      return {y: Math.round(r.y), h: Math.round(r.height), b: Math.round(r.bottom)};
    }"""))
    browser.close()
