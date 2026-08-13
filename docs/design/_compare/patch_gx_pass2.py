from pathlib import Path
import re

# --- gx.css: stop CSS filters (icons are already active/muted assets) ---
css_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\gx.css")
css = css_path.read_text(encoding="utf-8")
old = """.gx-tab img {
  width: 22px;
  height: 22px;
  display: block;
  filter: grayscale(1) brightness(0) invert(0.68);
}
.gx-tab.active img {
  filter: brightness(0) saturate(100%) invert(46%) sepia(86%) saturate(1900%) hue-rotate(199deg) brightness(98%) contrast(95%);
}"""
new = """.gx-tab img {
  width: 22px;
  height: 22px;
  display: block;
}"""
if old not in css:
    raise SystemExit("gx tab filter block not found")
css = css.replace(old, new)

# Ensure gx-nav works inside legacy chrome screens (exam/fp/bh/mehr/fk/formel)
extra = """

/* Embed gx 5-tab IA inside legacy chrome screens */
.ex-screen .gx-nav,
.fp-screen .gx-nav,
.bh2-screen .gx-nav,
.bh-ne-screen .gx-nav,
.bh-cal-screen .gx-nav,
.bh-pdf-screen .gx-nav,
.bh-empty-screen .gx-nav,
.mehr2-screen .gx-nav,
.mp-screen .gx-nav,
.tr-screen .gx-nav,
.de-screen .gx-nav,
.dl-screen .gx-nav,
.lo-screen .gx-nav,
.fk-screen .gx-nav,
.formel-screen .gx-nav,
.ld-screen .gx-nav {
  margin-top: auto;
  flex-shrink: 0;
  width: 100%;
}
.ex-home-indicator,
.fp-home-indicator {
  display: none !important;
}
"""
if "Embed gx 5-tab IA" not in css:
    css += extra
css_path.write_text(css, encoding="utf-8")
print("gx.css updated")

# --- screens.js: remove orphan home indicators after replaced navs ---
screens = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
s = screens.read_text(encoding="utf-8")
for pat in [
    r'\n\s*<div class="ex-home-indicator"[^>]*></div>',
    r'\n\s*<div class="fp-home-indicator"[^>]*></div>',
]:
    s, n = re.subn(pat, "", s)
    print(f"removed {n} for {pat}")
screens.write_text(s, encoding="utf-8")

# --- index.html: unify tab-bar-learn to 5-tab IA ---
idx = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\index.html")
html = idx.read_text(encoding="utf-8")
old_learn = """          <nav class="tab-bar tab-bar-learn" aria-label="Lernen Navigation" hidden>
            <a href="/lernen" data-page-link data-learn-tab="lernen" class="active">
              <span class="tab-icon-wrap"><img src="/static/figma/learn2/tab-book.svg" width="20" height="20" alt="" /></span>
              Lernen
"""
# Read current learn bar fully
m = re.search(r'<nav class="tab-bar tab-bar-learn"[^>]*>.*?</nav>', html, re.S)
if not m:
    raise SystemExit("tab-bar-learn not found")
new_learn = """<nav class="tab-bar tab-bar-learn" aria-label="App Navigation" hidden>
            <a href="/dashboard" data-page-link data-learn-tab="home">
              <span class="tab-icon-wrap"><img src="/static/figma/gx/tab-home-muted.svg" width="22" height="22" alt="" /></span>
              Home
            </a>
            <a href="/lernen" data-page-link data-learn-tab="lernen" class="active">
              <span class="tab-icon-wrap"><img src="/static/figma/gx/tab-book-active.svg" width="22" height="22" alt="" /></span>
              Lernen
            </a>
            <a href="/pruefungen" data-page-link data-learn-tab="exam">
              <span class="tab-icon-wrap"><img src="/static/figma/gx/tab-award.svg" width="22" height="22" alt="" /></span>
              Prüfung
            </a>
            <a href="/fortschritt" data-page-link data-learn-tab="progress">
              <span class="tab-icon-wrap"><img src="/static/figma/gx/tab-trending.svg" width="22" height="22" alt="" /></span>
              Fortschritt
            </a>
            <a href="/mehr" data-page-link data-learn-tab="profile">
              <span class="tab-icon-wrap"><img src="/static/figma/gx/tab-user.svg" width="22" height="22" alt="" /></span>
              Profil
            </a>
          </nav>"""
html = html[:m.start()] + new_learn + html[m.end():]
idx.write_text(html, encoding="utf-8")
print("index.html learn tab bar updated")

# Verify syntax of screens.js via node-ish check: at least helper + template balance
# Check OLC_GX_NAV exists and sample replacements
assert "window.OLC_GX_NAV" in s
assert 'OLC_GX_NAV("exam")' in s
assert 'OLC_GX_NAV("learn")' in s
assert "<nav class=\"ex-tabs\"" not in s
assert "<nav class=\"fk-tabs\"" not in s
assert "<nav class=\"mehr2-tabs\"" not in s
print("verification ok")
