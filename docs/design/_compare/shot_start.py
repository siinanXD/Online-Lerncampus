from playwright.sync_api import sync_playwright
import os

out = os.path.dirname(os.path.abspath(__file__))
os.makedirs(out, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 430, "height": 960})
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill("input[name=identifier]", "demo-azubi")
    page.fill("input[name=password]", "demo-pass")
    page.click("button[type=submit]")
    page.wait_for_timeout(800)

    shots = [
        ("/dashboard/fortsetzen", "live-03-5-fortsetzen.png", 430, 960),
        ("/dashboard/wochenbericht", "live-03-6-wochenbericht.png", 430, 960),
        ("/dashboard/merksaetze", "live-03-7-merksaetze.png", 430, 1100),
        ("/dashboard/tablet", "live-03-8-tablet.png", 800, 1100),
    ]
    for path, name, w, h in shots:
        page.set_viewport_size({"width": w, "height": h})
        page.goto(f"http://127.0.0.1:8000{path}", wait_until="networkidle")
        page.wait_for_timeout(600)
        frame = page.query_selector(".app-frame")
        target = os.path.join(out, name)
        if frame:
            frame.screenshot(path=target)
        else:
            page.screenshot(path=target)
        chrome = page.evaluate(
            "() => document.querySelector('.app-frame')?.dataset.chrome || ''"
        )
        title = page.evaluate("() => document.querySelector('h2')?.textContent || ''")
        print(f"saved {name} chrome={chrome} title={title}")
    browser.close()
print("done")
