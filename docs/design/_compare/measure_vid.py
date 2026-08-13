from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 390, "height": 905})
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(600)
    page.goto("http://127.0.0.1:8000/lernen/video", wait_until="networkidle")
    page.wait_for_timeout(400)
    print(
        json.dumps(
            page.evaluate(
                """() => {
      const phone = document.querySelector('.app-frame').getBoundingClientRect();
      const rel = (el) => {
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return {y: Math.round(r.y-phone.y), h: Math.round(r.height), b: Math.round(r.bottom-phone.y)};
      };
      return {
        frameH: Math.round(phone.height),
        header: rel(document.querySelector('.formel-header')),
        scroll: rel(document.querySelector('.vid-scroll')),
        player: rel(document.querySelector('.vid-player')),
        chapters: rel(document.querySelector('.vid-chapters')),
        next: rel(document.querySelector('.vid-next')),
        nextXp: rel(document.querySelector('.vid-next-xp')),
        tabs: rel(document.querySelector('.formel-tabs')),
        hi: rel(document.querySelector('.formel-home-indicator')),
        scrollOverflow: (() => {
          const s = document.querySelector('.vid-scroll');
          return {sh: s.scrollHeight, ch: s.clientHeight};
        })(),
      };
    }"""
            ),
            indent=2,
        )
    )
    b.close()
