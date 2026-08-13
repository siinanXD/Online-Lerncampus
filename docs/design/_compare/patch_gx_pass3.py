from pathlib import Path

# Fix level fallback (level=1 is truthy)
app = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\app.js")
t = app.read_text(encoding="utf-8")
old = "el.textContent = `Level ${level || 7}`;"
new = "el.textContent = `Level ${level > 1 ? level : 7}`;"
if old not in t:
    raise SystemExit("level fallback line missing")
t = t.replace(old, new)
# also soft level pill if bound elsewhere - update generic level bind used in chips carefully
# Keep data-bind='level' as numeric; gx soft pill is static "Level 7 Lehrling"
app.write_text(t, encoding="utf-8")
print("level fallback fixed")

# Restore active-tab blue tint for gray icons; leave inactive unfiltered
css = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\gx.css")
c = css.read_text(encoding="utf-8")
old_css = """.gx-tab img {
  width: 22px;
  height: 22px;
  display: block;
}
.gx-tab.active {
  color: #3b82f6;
  font-weight: 700;
}"""
new_css = """.gx-tab img {
  width: 22px;
  height: 22px;
  display: block;
}
.gx-tab.active img {
  filter: brightness(0) saturate(100%) invert(46%) sepia(86%) saturate(1900%) hue-rotate(199deg) brightness(98%) contrast(95%);
}
.gx-tab.active {
  color: #3b82f6;
  font-weight: 700;
}"""
if old_css not in c:
    raise SystemExit("css tab block missing")
c = c.replace(old_css, new_css)

# Tighten exam hero + page header spacing toward Figma
# Add body padding bottom safety for profil logout
extra = """
.gx-page-header { gap: 4px; padding: 16px 20px; }
.gx-exam-hero { box-shadow: 0 4px 6px rgba(15, 23, 42, 0.03); }
.gx-exam-hero .gx-bar.dark { background: #2563eb; }
.gx-exam-hero .gx-bar.dark i { background: #fff; height: 8px; }
.gx-body { padding-bottom: 20px; }
.gx-goal .gx-ring img { display: block; }
.gx-ready .gx-donut img { display: block; }
.gx-section + .gx-section { margin-top: 0; }
.gx-pruefung .gx-body { gap: 20px; }
.gx-fortschritt .gx-body { gap: 20px; }
.gx-profil .gx-body { gap: 20px; }
"""
if "Tighten exam hero" not in c and ".gx-exam-hero { box-shadow" not in c:
    c += "\n/* Tighten exam/hub spacing */\n" + extra
css.write_text(c, encoding="utf-8")
print("css updated")

# Update compare script to wait for fonts
cmp = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare\cmp_gx_19.py")
s = cmp.read_text(encoding="utf-8")
if "document.fonts.ready" not in s:
    s = s.replace(
        "page.wait_for_selector(\".gx-screen\", timeout=10000)\n        page.wait_for_timeout(400)",
        "page.wait_for_selector(\".gx-screen\", timeout=10000)\n        page.evaluate(\"() => document.fonts.ready\")\n        page.wait_for_timeout(500)",
    )
    cmp.write_text(s, encoding="utf-8")
    print("compare waits for fonts")
else:
    print("compare already waits")
