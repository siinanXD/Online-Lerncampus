from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(700)
    page.goto("http://127.0.0.1:8000/lernen/feedback/richtig", wait_until="networkidle")
    page.wait_for_timeout(400)
    info = page.evaluate(
        """() => {
      const q = (s) => document.querySelector(s);
      const box = (el) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return {y: Math.round(r.y), h: Math.round(r.height), bottom: Math.round(r.bottom)};
      };
      const answers = [...document.querySelectorAll('.fb-answer')].map(box);
      return {
        meta: box(q('.q-meta-row')),
        prompt: box(q('.q-prompt')),
        promptFont: getComputedStyle(q('.q-prompt')).fontFamily,
        answers,
        answersBox: box(q('.fb-answers')),
        sheet: box(q('.fb-sheet')),
        head: box(q('.fb-sheet-head')),
        explain: box(q('.fb-explain')),
        tip: box(q('.fb-tip')),
        btn: box(q('.success-button')),
        explainPs: [...document.querySelectorAll('.fb-explain > p, .fb-explain .fb-tip')].map(el => ({
          t: (el.className||el.tagName), h: Math.round(el.getBoundingClientRect().height),
          text: (el.textContent||'').slice(0,40)
        })),
      };
    }"""
    )
    print(json.dumps(info, indent=2))
    browser.close()
