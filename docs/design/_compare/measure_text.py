from playwright.sync_api import sync_playwright

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
    print(page.evaluate("""() => {
      const el = document.querySelector('.q-prompt');
      const cs = getComputedStyle(el);
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      ctx.font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
      const text = el.textContent.trim();
      const full = ctx.measureText(text).width;
      // try break points
      const parts = [
        ['Was ist der Unterschied zwischen einfach-', 'und doppeltwirkendem Zylinder?'],
        ['Was ist der Unterschied zwischen', 'einfach- und doppeltwirkendem Zylinder?'],
        ['Was ist der Unterschied zwischen einfach- und', 'doppeltwirkendem Zylinder?'],
      ];
      return {
        avail: el.clientWidth,
        full,
        font: ctx.font,
        breaks: parts.map(([a,b]) => ({a: ctx.measureText(a).width, b: ctx.measureText(b).width, aText:a, bText:b})),
        explainW: document.querySelector('.fb-explain > p:not(.fb-label)').clientWidth,
        explainFull: ctx.measureText(document.querySelector('.fb-explain > p:not(.fb-label)').textContent.trim()).width,
      };
    }"""))
    browser.close()
