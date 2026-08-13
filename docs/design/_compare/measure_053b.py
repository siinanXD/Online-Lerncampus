from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 430, "height": 1100}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(500)
    page.goto("http://127.0.0.1:8000/fachkunde/einheit", wait_until="networkidle")
    page.wait_for_timeout(300)
    print(
        page.evaluate(
            """() => {
    return [...document.querySelector('.fk-eu-scroll').children].map(el=>{
      const r=el.getBoundingClientRect();
      const cs=getComputedStyle(el);
      return {cls:el.className, h:Math.round(r.height*10)/10, mt:cs.marginTop, mb:cs.marginBottom};
    });
  }"""
        )
    )
    print(
        page.evaluate(
            """() => {
    const sr=getComputedStyle(document.querySelector('.screen-root'));
    const bot=getComputedStyle(document.querySelector('.fk-eu-bottom'));
    const hi=getComputedStyle(document.querySelector('.fk-eu-bottom .fk-home-indicator'));
    return {screenRoot:{display:sr.display,gap:sr.gap}, bottom:{padding:bot.padding,height:bot.height}, hi:{padding:hi.padding,height:hi.height}};
  }"""
        )
    )
    b.close()
