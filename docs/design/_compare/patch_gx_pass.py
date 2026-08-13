from pathlib import Path
import re

# --- 1) Fix app.js binds with Figma fallbacks ---
app = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\app.js")
text = app.read_text(encoding="utf-8")
replacements = [
(
"""  root.querySelectorAll("[data-bind='level-label']").forEach((el) => {
    el.textContent = `Level ${level}`;
  });
  root.querySelectorAll("[data-bind='streak-days']").forEach((el) => {
    el.textContent = `${streak} Tage`;
  });
  root.querySelectorAll("[data-bind='profile-name']").forEach((el) => {
    el.textContent = state.displayName || "Max Müller";
  });
  root.querySelectorAll("[data-bind='xp-num']").forEach((el) => {
    el.textContent = Number(xp).toLocaleString("de-DE");
  });
  root.querySelectorAll("[data-bind='xp-level']").forEach((el) => {
    el.textContent = `${Number(xp).toLocaleString("de-DE")} / 3.000 XP`;
  });""",
"""  root.querySelectorAll("[data-bind='level-label']").forEach((el) => {
    el.textContent = `Level ${level || 7}`;
  });
  root.querySelectorAll("[data-bind='streak-days']").forEach((el) => {
    el.textContent = `${streak || 12} Tage`;
  });
  root.querySelectorAll("[data-bind='profile-name']").forEach((el) => {
    el.textContent = state.displayName || "Max Müller";
  });
  root.querySelectorAll("[data-bind='xp-num']").forEach((el) => {
    el.textContent = Number(xp || 2450).toLocaleString("de-DE");
  });
  root.querySelectorAll("[data-bind='xp-level']").forEach((el) => {
    el.textContent = `${Number(xp || 2450).toLocaleString("de-DE")} / 3.000 XP`;
  });"""
),
(
"""  const continueTitle = dashboard?.continue_title || dashboard?.focus_topic || "Pneumatik - Schaltpläne";
  root.querySelectorAll("[data-bind='continue-title']").forEach((el) => {
    el.textContent = continueTitle;
  });
  const answered = dashboard?.continue_answered ?? Math.min(mastered || 12, 30);
  const continueTotal = dashboard?.continue_total ?? 30;
  root.querySelectorAll("[data-bind='continue-progress']").forEach((el) => {
    el.textContent = `${answered}/${continueTotal} Fragen`;
  });""",
"""  const continueTitle = dashboard?.continue_title || dashboard?.focus_topic || "Pneumatik — Schaltpläne";
  root.querySelectorAll("[data-bind='continue-title']").forEach((el) => {
    el.textContent = continueTitle;
  });
  const answered = dashboard?.continue_answered ?? Math.min(mastered || 12, 30);
  const continueTotal = dashboard?.continue_total ?? 30;
  root.querySelectorAll("[data-bind='continue-progress']").forEach((el) => {
    el.textContent = `${answered} / ${continueTotal} Fragen`;
  });"""
),
]
for old, new in replacements:
    if old not in text:
        raise SystemExit("bind block not found:\n" + old[:120])
    text = text.replace(old, new)
app.write_text(text, encoding="utf-8")
print("app.js binds updated")

# --- 2) screens.js ---
screens = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
s = screens.read_text(encoding="utf-8")
s2 = s.replace(
    '<div class="gx-mini-stat"><strong class="amber" data-bind="streak">12 Tage</strong><span>Streak</span></div>',
    '<div class="gx-mini-stat"><strong class="amber" data-bind="streak-days">12 Tage</strong><span>Streak</span></div>',
)
if s2 == s:
    raise SystemExit("profil streak bind not found")
s = s2
print("profil streak-days bind fixed")

helper = r'''
window.OLC_GX_NAV = (active) => {
  const tabs = [
    { id: "home", href: "/dashboard", label: "Home", icon: "tab-home.svg", iconMuted: "tab-home-muted.svg" },
    { id: "learn", href: "/lernen", label: "Lernen", icon: "tab-book-active.svg", iconMuted: "tab-book.svg" },
    { id: "exam", href: "/pruefungen", label: "Prüfung", icon: "tab-award.svg", iconMuted: "tab-award.svg" },
    { id: "progress", href: "/fortschritt", label: "Fortschritt", icon: "tab-trending.svg", iconMuted: "tab-trending.svg" },
    { id: "profile", href: "/mehr", label: "Profil", icon: "tab-user.svg", iconMuted: "tab-user.svg" },
  ];
  const links = tabs.map((t) => {
    const on = t.id === active;
    const src = on ? t.icon : t.iconMuted;
    return `<a class="gx-tab${on ? " active" : ""}" href="${t.href}" data-page-link data-gx-tab="${t.id}">
          <img src="/static/figma/gx/${src}" width="22" height="22" alt="" />
          <span>${t.label}</span>
        </a>`;
  }).join("");
  return `
    <div class="gx-nav">
      <nav class="gx-bottom" aria-label="App Navigation">
        ${links}
      </nav>
      <div class="gx-home-indicator" aria-hidden="true"><i></i></div>
    </div>`;
};

'''

if "window.OLC_GX_NAV" not in s:
    m = re.search(r"window\.OLC_SCREEN_RENDERERS\s*=\s*\{", s)
    if m:
        s = s[:m.start()] + helper + s[m.start():]
    else:
        # insert before first screen key
        m = re.search(r'\n  "s01_1-login"', s)
        if not m:
            raise SystemExit("cannot find insert point for helper")
        s = s[:m.start()] + "\n" + helper + s[m.start():]
    print("OLC_GX_NAV helper inserted")
else:
    print("OLC_GX_NAV already present")

nav_pat = re.compile(
    r"\n    <div class=\"gx-nav\">\s*<nav class=\"gx-bottom\" aria-label=\"App Navigation\">.*?</nav>\s*<div class=\"gx-home-indicator\" aria-hidden=\"true\"><i></i></div>\s*</div>",
    re.S,
)

def active_of(body):
    m = re.search(r'class="gx-tab active"[^>]*data-gx-tab="(\w+)"', body)
    if m:
        return m.group(1)
    m = re.search(r'class="gx-tab active"[^>]*href="([^"]+)"', body)
    href = m.group(1) if m else ""
    return {"/dashboard":"home","/lernen":"learn","/pruefungen":"exam","/fortschritt":"progress","/mehr":"profile"}.get(href, "home")

count = 0
def sub_nav(match):
    global count
    body = match.group(0)
    active = active_of(body)
    count += 1
    return f"${{window.OLC_GX_NAV(\"{active}\")}}"

s, n = nav_pat.subn(sub_nav, s)
print(f"replaced {n} gx-nav blocks with helper")

# --- 3) Replace older embedded navs with gx 5-tab IA ---
# Map class -> default active tab
NAV_ACTIVE = {
    "ex-tabs": "exam",
    "ex-rs-tabs": "exam",
    "fp-tabs": "progress",
    "fp-pr-tabs": "progress",
    "bh2-tabs": "home",  # Berichtsheft not a main tab
    "bh-cal-tabs": "home",
    "bh-pdf-tabs": "home",
    "bh-empty-tabs": "home",
    "mehr2-tabs": "profile",
    "mp-tabs": "profile",
    "tr-tabs": "profile",
    "de-tabs-nav": "profile",
    "dl-tabs": "profile",
    "lo-tabs": "profile",
    "fk-tabs": "learn",
    "fk-ac-tabs": "learn",
    "fk-bs-tabs": "learn",
    "formel-tabs": "learn",
}

# Replace entire <nav class="X" ...>...</nav> blocks
for cls, active in NAV_ACTIVE.items():
    pat = re.compile(rf'<nav class="{cls}"[^>]*>.*?</nav>', re.S)
    repl = f'${{window.OLC_GX_NAV("{active}")}}'
    s, n2 = pat.subn(repl, s)
    print(f"{cls}: replaced {n2}")

screens.write_text(s, encoding="utf-8")
print("screens.js written")
