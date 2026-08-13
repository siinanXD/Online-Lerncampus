from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(800)
    page.goto("http://127.0.0.1:8000/lernen/feedback/richtig", wait_until="networkidle")
    # bust css cache
    page.reload(wait_until="networkidle")
    page.wait_for_timeout(400)
    info = page.evaluate(
        """() => {
      const q = (s) => document.querySelector(s);
      const box = (el) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return {y: Math.round(r.y), h: Math.round(r.height), pad: cs.padding, gap: cs.gap, fs: cs.fontSize, height: cs.height};
      };
      return {
        header: box(q('.q-session-header')),
        prompt: box(q('.q-prompt')),
        a0: box(q('.fb-answer')),
        sheet: box(q('.fb-sheet')),
        btn: box(q('.success-button')),
      };
    }"""
    )
    print(json.dumps(info, indent=2))
    browser.close()
