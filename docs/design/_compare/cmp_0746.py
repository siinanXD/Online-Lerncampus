# -*- coding: utf-8 -*-
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

out = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
pairs = [
    ("/fortschritt/verlauf", "figma-07-4.png", "live-07-4.png", 971, False),
    ("/fortschritt/xp", "figma-07-5.png", "live-07-5.png", 844, False),
    ("/fortschritt/heatmap", "figma-07-6.png", "live-07-6.png", 1003, False),
]


def strip_device_chrome(img: Image.Image, fill=(250, 250, 249)) -> Image.Image:
    """Remove Figma mockup border (#d6d3d1) + white rounded corners for fair compare."""
    arr = np.asarray(img.convert("RGB")).copy()
    h, w = arr.shape[:2]
    # overwrite 1px edge border
    arr[0, :] = fill
    arr[-1, :] = fill
    arr[:, 0] = fill
    arr[:, -1] = fill
    # paint white corners (outside ~32px radius) with fill
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, w - 1, h - 1], radius=32, fill=255)
    m = np.asarray(mask)
    outside = m == 0
    arr[outside] = fill
    return Image.fromarray(arr)


with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 430, "height": 1200}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(800)

    for path, figma_name, live_name, h, light in pairs:
        page.set_viewport_size({"width": 430, "height": max(h + 80, 1100)})
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(600)
        clip = page.evaluate(
            f"""() => {{
              const r = document.querySelector('.app-frame').getBoundingClientRect();
              return {{x:r.x,y:r.y,width:r.width,height:Math.min(r.height,{h})}};
            }}"""
        )
        page.screenshot(path=str(out / live_name), clip=clip)
        f = Image.open(out / figma_name).convert("RGB")
        l = Image.open(out / live_name).convert("RGB")
        if light:
            f = strip_device_chrome(f)
        f = f.resize(l.size, Image.Resampling.LANCZOS)
        d = np.abs(np.asarray(f, np.float32) - np.asarray(l, np.float32)).mean(axis=2)
        print(
            f"{path} pixel_delta={(d > 30).mean()*100:.2f}% mae={d.mean():.1f} "
            f"live={l.size}"
        )
        heat = np.asarray(l).copy()
        heat[d > 30] = [255, 40, 40]
        Image.fromarray(heat).save(out / f"diff-{live_name}")
    b.close()
