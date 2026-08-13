from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    page = b.new_page(viewport={"width": 430, "height": 1100}, device_scale_factor=1)
    page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")
    page.fill('input[name="identifier"]', "demo-azubi")
    page.fill('input[name="password"]', "demo-pass")
    page.click('button[type="submit"]')
    page.wait_for_timeout(600)
    page.goto("http://127.0.0.1:8000/fachkunde/einheit", wait_until="networkidle")
    page.wait_for_timeout(400)
    print(
        page.evaluate(
            """() => {
    const f=document.querySelector('.app-frame').getBoundingClientRect();
    const pick=(sel)=>{
      const el=document.querySelector(sel);
      if(!el) return null;
      const r=el.getBoundingClientRect();
      return {h:r.height,y:r.y-f.y,bottom:r.bottom-f.y, scrollH: el.scrollHeight};
    };
    return {
      frame: {h:f.height,w:f.width},
      status: pick('.app-status'),
      header: pick('.fk-eu-header'),
      scroll: pick('.fk-eu-scroll'),
      bottom: pick('.fk-eu-bottom'),
      quiz: pick('.fk-eu-quiz'),
      merke: pick('.fk-eu-merke'),
      illu: pick('.fk-eu-illu'),
    };
  }"""
        )
    )
    b.close()
