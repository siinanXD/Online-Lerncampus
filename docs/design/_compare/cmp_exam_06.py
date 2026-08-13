# -*- coding: utf-8 -*-
from pathlib import Path
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")

pairs = [
    ("/pruefungen/uebersicht", "figma-06-3.png", "live-06-3.png", 844),
    ("/pruefungen/timer", "figma-06-4.png", "live-06-4.png", 844),
    ("/pruefungen/abgabe", "figma-06-5.png", "live-06-5.png", 844),
    ("/pruefungen/bestanden", "figma-06-6.png", "live-06-6.png", 958),
    ("/pruefungen/durchgefallen", "figma-06-7.png", "live-06-7.png", 961),
    ("/pruefungen/schwach", "figma-06-8.png", "live-06-8.png", 967),
    ("/pruefungen/kammertermine", "figma-06-9.png", "live-06-9.png", 928),
]

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 430, "height": 1200}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)

    for path, figma_name, live_name, h in pairs:
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
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
        f = f.resize(l.size, Image.Resampling.LANCZOS)
        d = np.abs(np.asarray(f, np.float32) - np.asarray(l, np.float32)).mean(axis=2)
        pct = float((d > 30).mean() * 100)
        mae = float(d.mean())
        heat = np.clip(d * 3, 0, 255).astype(np.uint8)
        Image.fromarray(heat).save(out / f"diff-{live_name}")
        print(f"{path}: pixel_delta={pct:.2f}% mae={mae:.1f} live={l.size} clip_h={clip['height']:.0f}")
    b.close()
