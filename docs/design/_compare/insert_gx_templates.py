from pathlib import Path

ROOT = Path(r"C:\dev\Repositories\Online-Lerncampus")
# Reuse the same generator content by importing from gen file's templates
# Reconstruct by reading gen_gx_screens.py execution: just re-run template portion.

exec_globals = {}
# Load helper definitions by re-reading and extracting from previous script is messy.
# Instead: call the original script's functions by rewriting a focused patcher.

from importlib.machinery import SourceFileLoader
# Rebuild templates with a slim script inline

GX = "/static/figma/gx"

def status_bar():
    return f'''
    <div class="gx-status" aria-hidden="true">
      <span>9:41</span>
      <span class="gx-status-icons">
        <img src="{GX}/ios-signal.svg" width="20" height="20" alt="" />
        <img src="{GX}/ios-wifi.svg" width="20" height="20" alt="" />
        <img src="{GX}/ios-battery.svg" width="28" height="20" alt="" />
      </span>
    </div>'''

def bottom_nav(active):
    tabs = [
        ("home", "/dashboard", "Home", "tab-home.svg"),
        ("learn", "/lernen", "Lernen", "tab-book.svg"),
        ("exam", "/pruefungen", "Prüfung", "tab-award.svg"),
        ("progress", "/fortschritt", "Fortschritt", "tab-trending.svg"),
        ("profile", "/mehr", "Profil", "tab-user.svg"),
    ]
    items = []
    for key, href, label, icon in tabs:
        cls = " active" if key == active else ""
        items.append(
            f'''<a class="gx-tab{cls}" href="{href}" data-page-link data-gx-tab="{key}">
          <img src="{GX}/{icon}" width="22" height="22" alt="" />
          <span>{label}</span>
        </a>'''
        )
    return f'''
    <div class="gx-nav">
      <nav class="gx-bottom" aria-label="App Navigation">
        {''.join(items)}
      </nav>
      <div class="gx-home-indicator" aria-hidden="true"><i></i></div>
    </div>'''

# Import templates from gen_gx_screens by running its template-building section
# Simplest: read gen file and execute only until screens=... then get home etc.
# Actually paste the five templates by re-running gen_gx_screens with fixed condition.

src = Path(r"C:\dev\Repositories\Online-Lerncampus\docs\design\_compare\gen_gx_screens.py").read_text(encoding="utf-8")
# Monkeypatch the condition in a copy
src2 = src.replace(
    'if \'"s19_1-home-dashboard"\' not in screens:',
    'if \'s19_1-home-dashboard\": ()\' not in screens:',
)
# Avoid re-doing route replacements (already done) - wrap so replacements are no-ops if already applied
# Safer: just extract templates by exec of helper functions then insert.

ns = {}
# Execute only the template-building part of gen_gx_screens by importing functions
# Cut: run from start through profil assignment, stop before Patch screens.js
cut = src.split("# Patch screens.js routes")[0]
exec(cut, ns)
home, lernen, pruefung, fortschritt, profil = ns["home"], ns["lernen"], ns["pruefung"], ns["fortschritt"], ns["profil"]

screens_path = ROOT / "app/web/static/screens.js"
screens = screens_path.read_text(encoding="utf-8")
marker = '  "s03_1-dashboard-default":'
if 's19_1-home-dashboard": ()' in screens:
    print("templates already present")
else:
    if marker not in screens:
        raise SystemExit("marker missing")
    screens = screens.replace(marker, home + lernen + pruefung + fortschritt + profil + marker, 1)
    # xp suffix fix
    screens = screens.replace(
        '<strong class="gx-xp" data-bind="xp">2.450 XP</strong>',
        '<strong class="gx-xp"><span data-bind="xp-num">2.450</span> XP</strong>',
    )
    screens_path.write_text(screens, encoding="utf-8")
    print("templates inserted")

t = screens_path.read_text(encoding="utf-8")
print("ok", all(k in t for k in [
    's19_1-home-dashboard": ()',
    's19_2-lernen-journey": ()',
    's19_3-pruefung-hub": ()',
    's19_4-fortschritt-stats": ()',
    's19_5-profil-settings": ()',
]))
print("gx-screen", t.count("gx-screen"))
