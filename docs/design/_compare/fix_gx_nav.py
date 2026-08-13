from pathlib import Path

p = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
s = p.read_text(encoding="utf-8")
start = s.find("window.OLC_GX_NAV = (active) => {")
end = s.find("window.OLC_SCREEN_RENDERERS = {", start)
if start < 0 or end < 0:
    raise SystemExit(f"markers missing start={start} end={end}")

fixed = '''window.OLC_GX_NAV = (active) => {
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

s = s[:start] + fixed + s[end:]
p.write_text(s, encoding="utf-8")
print("OLC_GX_NAV repaired")
assert "return `${window.OLC_GX_NAV" not in p.read_text(encoding="utf-8")
print("verified")
