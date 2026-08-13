"""Measure feedback screen geometry vs Figma reference bands."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")


def sheet_y_from_figma(path: Path, greenish=True):
    """Find approx Y where feedback sheet starts via color transition."""
    img = np.asarray(Image.open(path).convert("RGB"), dtype=np.int16)
    h, w, _ = img.shape
    # sample center column
    col = img[:, w // 2]
    ys = []
    for y in range(200, h - 50):
        r, g, b = col[y]
        if greenish:
            # mint sheet #ecfdf5 ≈ (236,253,245)
            if g > 230 and r > 200 and b > 220 and g - r > 5:
                ys.append(y)
                break
        else:
            # pink sheet #fef2f2
            if r > 240 and g > 220 and b > 220 and r - g > 5:
                ys.append(y)
                break
    return ys[0] if ys else None


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 900}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)

    for path, figma, greenish in [
        ("/lernen/feedback/richtig", "figma-04-7.png", True),
        ("/lernen/feedback/falsch", "figma-04-8.png", False),
        ("/lernen/uebersetzung", "figma-04-10.png", None),
        ("/lernen/fehlerdiagnose", "figma-04-12.png", None),
    ]:
        page.set_viewport_size({"width": 390, "height": 844})
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(350)
        info = page.evaluate(
            """() => {
          const phone = document.querySelector('.app-frame');
          const pr = phone.getBoundingClientRect();
          const rel = (el) => {
            if (!el) return null;
            const r = el.getBoundingClientRect();
            return {y: Math.round(r.y-pr.y), h: Math.round(r.height), b: Math.round(r.bottom-pr.y), w: Math.round(r.width)};
          };
          return {
            clip: {x: pr.x, y: pr.y, width: pr.width, height: Math.min(pr.height, 844)},
            status: rel(document.querySelector('.app-status')),
            session: rel(document.querySelector('.q-session-header')),
            meta: rel(document.querySelector('.q-meta-row')),
            prompt: rel(document.querySelector('.q-prompt')),
            answers: rel(document.querySelector('.fb-answers')),
            sheet: rel(document.querySelector('.fb-sheet, .uebersetz-sheet')),
            btn: rel(document.querySelector('.success-button, .fb-actions-row, .uebersetz-actions')),
            banner: rel(document.querySelector('.fd-banner')),
            cases: rel(document.querySelector('.fd-cases')),
            prog: rel(document.querySelector('.fd-progress')),
            tabs: rel(document.querySelector('.formel-tabs')),
            contentPad: getComputedStyle(document.querySelector('.app-content')||document.body).paddingTop,
          };
        }"""
        )
        fpath = out / figma
        fy = None
        if fpath.exists() and greenish is not None:
            fy = sheet_y_from_figma(fpath, greenish=greenish)
        print(path)
        print("  live:", json.dumps(info, indent=None))
        print(f"  figma sheetY≈{fy}")

        # band MAE for content region ignoring AA
        live_name = {
            "/lernen/feedback/richtig": "live-04-7.png",
            "/lernen/feedback/falsch": "live-04-8.png",
            "/lernen/uebersetzung": "live-04-10.png",
            "/lernen/fehlerdiagnose": "live-04-12.png",
        }[path]
        clip = info["clip"]
        page.screenshot(path=str(out / live_name), clip=clip)
        if fpath.exists():
            f = Image.open(fpath).convert("RGB")
            l = Image.open(out / live_name).convert("RGB")
            f = f.resize(l.size, Image.Resampling.LANCZOS)
            a = np.asarray(f, dtype=np.float32)
            b = np.asarray(l, dtype=np.float32)
            diff = np.abs(a - b).mean(axis=2)
            print(f"  delta={(diff>30).mean()*100:.2f}% mae={diff.mean():.1f}")

    browser.close()
