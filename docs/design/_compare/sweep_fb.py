"""Sweep sheet margin and capture band deltas for 04.7/04.8/04.10."""
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")


def delta(figma_path, live_arr):
    f = Image.open(figma_path).convert("RGB")
    f = f.resize((live_arr.shape[1], live_arr.shape[0]), Image.Resampling.LANCZOS)
    a = np.asarray(f, dtype=np.float32)
    d = np.abs(a - live_arr).mean(axis=2)
    return float((d > 30).mean() * 100), float(d.mean())


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)

    print("=== 04.7 margin sweep ===")
    best7 = None
    for mt in range(-10, -40, -2):
        page.goto("http://127.0.0.1:8000/lernen/feedback/richtig", wait_until="networkidle")
        page.wait_for_timeout(200)
        page.add_style_tag(
            content=f".fb-play .fb-sheet.ok {{ margin-top: {mt}px !important; }}"
        )
        page.wait_for_timeout(80)
        clip = page.evaluate(
            """() => { const r=document.querySelector('.app-frame').getBoundingClientRect();
            return {x:r.x,y:r.y,width:r.width,height:Math.min(r.height,844)}; }"""
        )
        page.screenshot(path=str(out / "_tmp.png"), clip=clip)
        live = np.asarray(Image.open(out / "_tmp.png").convert("RGB"), dtype=np.float32)
        pct, mae = delta(out / "figma-04-7.png", live)
        print(f"  mt={mt}: {pct:.2f}% mae={mae:.1f}")
        if best7 is None or pct < best7[0]:
            best7 = (pct, mt, mae)
    print("best7", best7)

    print("=== 04.8 margin sweep ===")
    best8 = None
    for mt in range(0, -30, -2):
        page.goto("http://127.0.0.1:8000/lernen/feedback/falsch", wait_until="networkidle")
        page.wait_for_timeout(200)
        page.add_style_tag(
            content=f".fb-play .fb-sheet.bad {{ margin-top: {mt}px !important; }}"
        )
        page.wait_for_timeout(80)
        clip = page.evaluate(
            """() => { const r=document.querySelector('.app-frame').getBoundingClientRect();
            return {x:r.x,y:r.y,width:r.width,height:Math.min(r.height,844)}; }"""
        )
        page.screenshot(path=str(out / "_tmp.png"), clip=clip)
        live = np.asarray(Image.open(out / "_tmp.png").convert("RGB"), dtype=np.float32)
        pct, mae = delta(out / "figma-04-8.png", live)
        print(f"  mt={mt}: {pct:.2f}% mae={mae:.1f}")
        if best8 is None or pct < best8[0]:
            best8 = (pct, mt, mae)
    print("best8", best8)

    # 04.10 sheet top
    page.goto("http://127.0.0.1:8000/lernen/uebersetzung", wait_until="networkidle")
    page.wait_for_timeout(300)
    info = page.evaluate(
        """() => {
      const phone=document.querySelector('.app-frame').getBoundingClientRect();
      const s=document.querySelector('.uebersetz-sheet').getBoundingClientRect();
      return {sheetY: Math.round(s.y-phone.y), sheetH: Math.round(s.height)};
    }"""
    )
    print("04.10 live sheet", info)
    img = np.asarray(Image.open(out / "figma-04-10.png").convert("RGB"))
    # white sheet starts
    for y in range(200, 700):
        row = img[y, 40:350].mean(0)
        if row[0] > 250 and row[1] > 250 and row[2] > 250:
            print("04.10 figma sheetY", y)
            break

    # 04.12
    page.goto("http://127.0.0.1:8000/lernen/fehlerdiagnose", wait_until="networkidle")
    page.wait_for_timeout(300)
    clip = page.evaluate(
        """() => { const r=document.querySelector('.app-frame').getBoundingClientRect();
        return {x:r.x,y:r.y,width:r.width,height:Math.min(r.height,844)}; }"""
    )
    page.screenshot(path=str(out / "live-04-12.png"), clip=clip)
    live = np.asarray(Image.open(out / "live-04-12.png").convert("RGB"), dtype=np.float32)
    pct, mae = delta(out / "figma-04-12.png", live)
    print(f"04.12: {pct:.2f}% mae={mae:.1f}")

    browser.close()
