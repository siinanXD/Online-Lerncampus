from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 390, "height": 844})
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(600)
    page.goto("http://127.0.0.1:8000/lernen/feedback/richtig", wait_until="networkidle")
    page.wait_for_timeout(400)
    print(
        json.dumps(
            page.evaluate(
                """() => {
      const p = document.querySelector('.q-prompt');
      const a = document.querySelector('.fb-answer.correct .answer-text');
      const t = document.querySelector('.fb-title');
      const e = document.querySelector('.fb-explain > p:not(.fb-label)');
      const sheet = document.querySelector('.fb-sheet');
      const phone = document.querySelector('.app-frame').getBoundingClientRect();
      const rel = (el) => {
        const r = el.getBoundingClientRect();
        return {y: Math.round(r.y-phone.y), h: Math.round(r.height), b: Math.round(r.bottom-phone.y)};
      };
      const cs = el => {
        const s = getComputedStyle(el);
        return {ff:s.fontFamily, fs:s.fontSize, fw:s.fontWeight, lh:s.lineHeight,
                w:Math.round(el.getBoundingClientRect().width), h:Math.round(el.getBoundingClientRect().height)};
      };
      return {
        prompt: cs(p), ans: cs(a), title: cs(t), explain: cs(e),
        sheet: rel(sheet), btn: rel(document.querySelector('.success-button')),
        ansBoxes: [...document.querySelectorAll('.fb-answer')].map(rel),
        inter: document.fonts.check('700 18px Inter'),
        sheetBg: getComputedStyle(sheet).backgroundColor,
        xp: getComputedStyle(document.querySelector('.xp-pill')).fontWeight,
      };
    }"""
            ),
            indent=2,
        )
    )
    b.close()
