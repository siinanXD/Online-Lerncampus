from playwright.sync_api import sync_playwright
import json

paths = [
    "/lernen/feedback/richtig",
    "/lernen/feedback/falsch",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)
    for path in paths:
        page.goto("http://127.0.0.1:8000" + path, wait_until="networkidle")
        page.wait_for_timeout(350)
        info = page.evaluate(
            """() => {
          const q = (s) => document.querySelector(s);
          const box = (el) => el ? (() => { const r = el.getBoundingClientRect(); return {y: Math.round(r.y), h: Math.round(r.height), b: Math.round(r.bottom)}; })() : null;
          const last = [...document.querySelectorAll('.fb-answer')].pop();
          return {
            lastAns: box(last),
            sheet: box(q('.fb-sheet')),
            btn: box(q('.success-button, .fb-actions-row')),
            playH: box(q('.q-play')),
          };
        }"""
        )
        print(path, json.dumps(info))
    browser.close()
