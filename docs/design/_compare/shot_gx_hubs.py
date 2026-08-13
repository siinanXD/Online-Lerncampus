from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare")
routes = [
    ("dashboard", "/dashboard"),
    ("lernen", "/lernen"),
    ("pruefungen", "/pruefungen"),
    ("fortschritt", "/fortschritt"),
    ("mehr", "/mehr"),
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_context(viewport={"width": 430, "height": 1000}).new_page()
    page.goto("http://127.0.0.1:8000/login", wait_until="domcontentloaded")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"].login-submit')
    page.wait_for_timeout(1200)
    if "/onboarding" in page.url:
        skip = page.locator('a[href="/dashboard"]')
        if skip.count():
            skip.first.click()
            page.wait_for_timeout(800)
        else:
            page.goto("http://127.0.0.1:8000/dashboard")
            page.wait_for_timeout(800)
    for name, path in routes:
        page.goto(f"http://127.0.0.1:8000{path}", wait_until="domcontentloaded")
        page.wait_for_selector(".gx-screen", timeout=10000)
        page.wait_for_timeout(300)
        chrome = page.locator(".app-frame").get_attribute("data-chrome")
        tabs = [t.replace("\n", " ").strip() for t in page.locator(".gx-tab").all_inner_texts()]
        active = page.locator(".gx-tab.active").inner_text().replace("\n", " ").strip()
        page.locator(".app-frame").screenshot(path=str(OUT / f"live-gx-{name}.png"))
        print(path, chrome, active, tabs)
    browser.close()
    print("DONE")
