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
    page.wait_for_timeout(400)
    info = page.evaluate(
        """() => {
      const q = (s) => document.querySelector(s);
      const box = (el) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        const cs = getComputedStyle(el);
        return {
          y: Math.round(r.y), h: Math.round(r.height), x: Math.round(r.x), w: Math.round(r.width),
          pad: cs.padding, gap: cs.gap, mt: cs.marginTop, fs: cs.fontSize, lh: cs.lineHeight
        };
      };
      return {
        frame: box(q('.app-frame')),
        status: box(q('.app-status')),
        content: box(q('.app-content')),
        play: box(q('.q-play')),
        main: box(q('.q-play-main')),
        header: box(q('.q-session-header')),
        body: box(q('.q-play-body')),
        answers: box(q('.fb-answers')),
        a0: box(q('.fb-answer')),
        prompt: box(q('.q-prompt')),
        sheet: box(q('.fb-sheet')),
        explain: box(q('.fb-explain')),
        tip: box(q('.fb-tip')),
        btn: box(q('.success-button')),
        chrome: q('.app-frame')?.getAttribute('data-chrome'),
        bodyScroll: q('.app-content')?.scrollHeight,
      };
    }"""
    )
    print(json.dumps(info, indent=2))
    browser.close()
