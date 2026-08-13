# -*- coding: utf-8 -*-
"""Patch Fortschritt 07.4–07.6 pixel screens into screens.js + ui.css."""
from pathlib import Path
import re

screens_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
css_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\ui.css")

text = screens_path.read_text(encoding="utf-8")

tabs = '''
        <nav class="fp-pr-tabs" aria-label="Fortschritt Navigation">
          <a href="/dashboard" data-page-link>
            <img src="/static/figma/fp/fp-pr-tab-book.svg" width="20" height="20" alt="" />
            Campus
          </a>
          <a href="/lernen" data-page-link>
            <img src="/static/figma/fp/fp-pr-tab-edit.svg" width="20" height="20" alt="" />
            Üben
          </a>
          <a href="/fortschritt" data-page-link class="active">
            <img src="/static/figma/fp/fp-pr-tab-activity.svg" width="20" height="20" alt="" />
            Bericht
          </a>
          <a href="/mehr" data-page-link>
            <img src="/static/figma/fp/fp-pr-tab-user.svg" width="20" height="20" alt="" />
            Profil
          </a>
        </nav>
        <div class="fp-pr-home" aria-hidden="true"></div>'''

# Heatmap cell levels from Figma 136:9459–9486
# l0=#334155, l1=13%, l2=31%, l3=50%, l4=#10b981
heat_cells = [
    "l0", "l4", "l2", "l4", "l1", "l0", "l4",
    "l3", "l0", "l1", "l2", "l0", "l4", "l4",
    "l0", "l1", "l3", "l4", "l2", "l0", "l0",
    "l2", "l4", "l1", "l4", "l0", "l3", "l4",
]
heat_html = [f'<i class="{c}"></i>' for c in heat_cells]

# Streak calendar colors from Figma 07.5
streak_rows = [
    ["#86efac", "#4ade80", "#f5f5f4", "#bbf7d0", "#16a34a", "#4ade80", "#86efac"],
    ["#4ade80", "#f5f5f4", "#86efac", "#16a34a", "#bbf7d0", "#86efac", "#4ade80"],
    ["#16a34a", "#4ade80", "#4ade80", "#86efac", "#f5f5f4", "#bbf7d0", "#16a34a"],
    ["#4ade80", "#16a34a", "#bbf7d0", "#86efac", "#4ade80", "#86efac", "today"],
]
streak_html_parts = []
for row in streak_rows:
    cells = []
    for c in row:
        if c == "today":
            cells.append('<i class="today"><img src="/static/figma/fp/fp-xs-today.svg" width="34" height="34" alt="" /></i>')
        else:
            cells.append(f'<i style="background:{c}"></i>')
    streak_html_parts.append(f'<div class="fp-xs-streak-row">{"".join(cells)}</div>')
streak_grid = "\n              ".join(streak_html_parts)

rank_rows = [
    (1, "Arbeitssicherheit", 92, "green", "⭐⭐⭐", False),
    (2, "Grundlagen Metall", 100, "green", "⭐⭐⭐", False),
    (3, "Werkstoffkunde", 85, "green", "⭐⭐½", False),
    (4, "Messtechnik", 60, "blue", "⭐⭐", False),
    (5, "Pneumatik", 40, "orange", "⭐", False),
    (6, "Hydraulik", 10, "red", "—", False),
    (7, "Steuerungstechnik", 0, "muted", "🔒", True),
    (8, "Elektrotechnik", 0, "muted", "🔒", True),
]
rank_html = []
for n, name, pct, tone, stars, locked in rank_rows:
    lc = " locked" if locked else ""
    rank_html.append(
        f'''            <article class="fp-hm-rank{lc}">
              <span class="fp-hm-rank-n">{n}</span>
              <div class="fp-hm-rank-body">
                <strong>{name}</strong>
                <div class="fp-hm-rank-bar-row">
                  <div class="fp-hm-rank-track"><i class="{tone}" style="width:{pct}%"></i></div>
                  <em>{pct}%</em>
                </div>
              </div>
              <span class="fp-hm-rank-stars">{stars}</span>
            </article>'''
    )

s074 = f'''  "s07_4-statistik-verlauf": () => `
      <div class="fp-screen fp-pr-screen fp-st-screen" data-node-id="136:9371">
        <div class="fp-pr-scroll">
          <header class="fp-pr-header">
            <a class="fp-pr-icon-btn" href="/fortschritt" data-page-link aria-label="Zurück">
              <img src="/static/figma/fp/fp-st-back.svg" width="20" height="20" alt="" />
            </a>
            <h2>Statistiken</h2>
            <button class="fp-pr-icon-btn" type="button" aria-label="Teilen">
              <img src="/static/figma/fp/fp-st-share.svg" width="20" height="20" alt="" />
            </button>
          </header>
          <div class="fp-st-body">
            <div class="fp-st-filters" role="tablist" aria-label="Zeitraum">
              <button type="button">Woche</button>
              <button type="button" class="active">Monat</button>
              <button type="button">Gesamt</button>
            </div>
            <article class="fp-st-card">
              <div class="fp-st-card-head">
                <span>Lernzeit</span>
                <strong class="blue">4h 20min diese Woche</strong>
              </div>
              <div class="fp-st-bars" aria-hidden="true">
                <div class="fp-st-bar"><i style="height:21px"></i><span>Mo</span></div>
                <div class="fp-st-bar"><i style="height:31px"></i><span>Di</span></div>
                <div class="fp-st-bar"><i style="height:56px"></i><span>Mi</span></div>
                <div class="fp-st-bar"><i style="height:14px"></i><span>Do</span></div>
                <div class="fp-st-bar"><i style="height:46px"></i><span>Fr</span></div>
                <div class="fp-st-bar"><i style="height:63px"></i><span>Sa</span></div>
                <div class="fp-st-bar"><i style="height:28px"></i><span>So</span></div>
              </div>
            </article>
            <article class="fp-st-card">
              <div class="fp-st-card-head">
                <span>XP-Verlauf</span>
                <strong class="amber">+2.150 XP gesamt</strong>
              </div>
              <img class="fp-st-spark" src="/static/figma/fp/fp-st-spark-xp.svg" width="318" height="80" alt="" />
            </article>
            <article class="fp-st-card">
              <div class="fp-st-card-head">
                <span>Fehlerquote Trend</span>
                <strong class="green fp-st-trend">23% → 18% <img src="/static/figma/fp/fp-st-trend-down.svg" width="16" height="16" alt="" /></strong>
              </div>
              <img class="fp-st-spark" src="/static/figma/fp/fp-st-spark-err.svg" width="318" height="80" alt="" />
            </article>
            <article class="fp-st-card">
              <p class="fp-st-card-title">Aktivität (Letzte 4 Wochen)</p>
              <div class="fp-st-heat">{"".join(heat_html)}</div>
              <div class="fp-st-legend">
                <span>Wenig</span>
                <div class="fp-st-legend-swatches"><i class="l0"></i><i class="l1"></i><i class="l2"></i><i class="l4"></i></div>
                <span>Viel</span>
              </div>
            </article>
          </div>
        </div>
        {tabs}
      </div>
    `,
'''

s075 = f'''  "s07_5-statistik-xp-und-streak": () => `
      <div class="fp-screen fp-xs-screen" data-node-id="136:9520">
        <div class="fp-xs-scroll">
          <header class="fp-xs-header">
            <div class="fp-xs-header-left">
              <a href="/fortschritt" data-page-link aria-label="Zurück">
                <img src="/static/figma/fp/fp-xs-back.svg" width="24" height="24" alt="" />
              </a>
              <h2>Deine Stats</h2>
            </div>
            <button type="button" aria-label="Mehr">
              <img src="/static/figma/fp/fp-xs-more.svg" width="24" height="24" alt="" />
            </button>
          </header>
          <div class="fp-xs-body">
            <div class="fp-xs-filters" role="tablist" aria-label="Zeitraum">
              <button type="button">Woche</button>
              <button type="button" class="active">Monat</button>
              <button type="button">Gesamt</button>
            </div>
            <article class="fp-xs-card">
              <div class="fp-xs-card-head">
                <strong>XP-Verlauf</strong>
                <em>+1.230 XP</em>
              </div>
              <div class="fp-xs-chart">
                <img class="fp-xs-chart-img" src="/static/figma/fp/fp-xs-chart.png" width="326" height="140" alt="" />
              </div>
              <div class="fp-xs-metrics">
                <div><span>Tägl. Schnitt</span><strong>41 XP</strong></div>
                <div><span>Bester Tag</span><strong>12. März (156 XP)</strong></div>
              </div>
            </article>
            <article class="fp-xs-card">
              <strong class="fp-xs-card-title">Streak-Kalender — März 2025</strong>
              <div class="fp-xs-streak">
              {streak_grid}
              </div>
              <div class="fp-xs-streak-meta">
                <div>
                  <span>Aktueller Streak</span>
                  <strong class="green"><span data-bind="streak">12</span> Tage 🔥</strong>
                </div>
                <div class="end">
                  <span>Längster Streak</span>
                  <strong>28 Tage</strong>
                </div>
              </div>
              <div class="fp-xs-hint">
                <span aria-hidden="true">🏆</span>
                <p>Noch 2 Tage bis zum 14-Tage Badge! 🔥</p>
              </div>
            </article>
            <div data-bind="gamification-live" hidden></div>
          </div>
        </div>
        <div class="fp-xs-home" aria-hidden="true"></div>
      </div>
    `,
'''

s076 = f'''  "s07_6-statistik-themen-heatmap": () => `
      <div class="fp-screen fp-hm-screen" data-node-id="136:9624">
        <div class="fp-hm-scroll">
          <header class="fp-xs-header">
            <div class="fp-xs-header-left">
              <a href="/fortschritt" data-page-link aria-label="Zurück">
                <img src="/static/figma/fp/fp-hm-back.svg" width="24" height="24" alt="" />
              </a>
              <h2>Themenanalyse</h2>
            </div>
            <button type="button" aria-label="Mehr">
              <img src="/static/figma/fp/fp-hm-more.svg" width="24" height="24" alt="" />
            </button>
          </header>
          <div class="fp-hm-body">
            <div class="fp-hm-radar-wrap">
              <img class="fp-hm-radar" src="/static/figma/fp/fp-hm-radar.png" width="240" height="240" alt="Themen-Radar" />
            </div>
            <article class="fp-hm-ai">
              <span class="fp-hm-ai-ico">
                <img src="/static/figma/fp/fp-hm-brain.svg" width="20" height="20" alt="" />
              </span>
              <p>KI-Empfehlung: Fokus auf Pneumatik und Hydraulik für die nächsten 2 Wochen.</p>
            </article>
            <div class="fp-hm-section">
              <h3>Themen-Ranking</h3>
              <div class="fp-hm-ranks">
{chr(10).join(rank_html)}
              </div>
            </div>
          </div>
        </div>
        <div class="fp-xs-home" aria-hidden="true"></div>
      </div>
    `,
'''

def replace_screen(src: str, key: str, new_block: str) -> str:
    pat = re.compile(
        rf'  "{re.escape(key)}": \(\) => `[\s\S]*?`,\n(?=  ")',
        re.M,
    )
    m = pat.search(src)
    if not m:
        raise SystemExit(f"screen not found: {key}")
    return src[: m.start()] + new_block + src[m.end() :]

text = replace_screen(text, "s07_4-statistik-verlauf", s074)
text = replace_screen(text, "s07_5-statistik-xp-und-streak", s075)
text = replace_screen(text, "s07_6-statistik-themen-heatmap", s076)
screens_path.write_text(text, encoding="utf-8")
print("screens.js updated")

css_block = r'''
/* --- 07.4 Statistik Verlauf --- */
.app-frame[data-chrome="fp"]:has(.fp-st-screen) { height: 971px; min-height: 971px; }
.fp-st-body {
  display: flex; flex-direction: column; gap: 18px;
  padding: 12px 20px 20px; box-sizing: border-box;
}
.fp-st-filters { display: flex; gap: 8px; width: 100%; }
.fp-st-filters button {
  flex: 1; margin: 0; border: 0; border-radius: 100px; padding: 8px 16px;
  background: #1e293b; color: #94a3b8; font-size: 13px; font-weight: 600; cursor: pointer;
}
.fp-st-filters button.active { background: #3b82f6; color: #f8fafc; }
.fp-st-card {
  display: flex; flex-direction: column; gap: 12px; padding: 16px;
  border-radius: 16px; background: #1e293b;
  box-shadow: 0 8px 8px rgba(0,0,0,0.25); box-sizing: border-box;
}
.fp-st-card-head {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
  font-size: 14px; white-space: nowrap;
}
.fp-st-card-head span { color: #94a3b8; font-weight: 600; }
.fp-st-card-head strong { font-weight: 700; }
.fp-st-card-head strong.blue { color: #3b82f6; }
.fp-st-card-head strong.amber { color: #f59e0b; }
.fp-st-card-head strong.green { color: #10b981; }
.fp-st-trend { display: inline-flex; align-items: center; gap: 4px; }
.fp-st-trend img { width: 16px; height: 16px; display: block; }
.fp-st-card-title { margin: 0; color: #94a3b8; font-size: 14px; font-weight: 600; }
.fp-st-bars {
  display: flex; gap: 12px; height: 100px; align-items: flex-end; justify-content: center;
}
.fp-st-bar {
  flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 6px;
}
.fp-st-bar > i {
  display: block; width: 16px; border-radius: 4px 4px 0 0; background: #3b82f6;
}
.fp-st-bar > span { color: #64748b; font-size: 11px; line-height: 1; }
.fp-st-spark { width: 100%; max-width: 318px; height: 80px; display: block; object-fit: fill; }
.fp-st-heat {
  display: flex; flex-wrap: wrap; gap: 6px; align-items: flex-start; width: 100%;
}
.fp-st-heat > i,
.fp-st-legend-swatches > i {
  display: block; border-radius: 4px; flex-shrink: 0;
}
.fp-st-heat > i { width: 30px; height: 30px; }
.fp-st-legend-swatches > i { width: 12px; height: 12px; border-radius: 2px; }
.fp-st-heat > i.l0, .fp-st-legend-swatches > i.l0 { background: #334155; }
.fp-st-heat > i.l1, .fp-st-legend-swatches > i.l1 { background: rgba(16,185,129,0.13); }
.fp-st-heat > i.l2, .fp-st-legend-swatches > i.l2 { background: rgba(16,185,129,0.31); }
.fp-st-heat > i.l3, .fp-st-legend-swatches > i.l3 { background: rgba(16,185,129,0.5); }
.fp-st-heat > i.l4, .fp-st-legend-swatches > i.l4 { background: #10b981; }
.fp-st-legend {
  display: flex; align-items: center; justify-content: space-between; width: 100%;
}
.fp-st-legend > span { color: #64748b; font-size: 11px; }
.fp-st-legend-swatches { display: flex; gap: 4px; align-items: flex-start; }

/* --- 07.5 XP & Streak (light) --- */
.app-frame[data-chrome="fp"]:has(.fp-xs-screen) {
  height: 844px; min-height: 844px; background: #fafaf9;
}
.app-frame[data-chrome="fp"]:has(.fp-xs-screen) .app-status { color: #1c1917; }
.app-frame[data-chrome="fp"]:has(.fp-xs-screen) .login-status-icon { filter: none; }
.app-frame[data-chrome="fp"]:has(.fp-xs-screen) .app-content { background: #fafaf9; }
.fp-xs-screen {
  background: #fafaf9; color: #1c1917; justify-content: space-between;
}
.fp-xs-scroll { flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; }
.fp-xs-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 8px 20px 16px; background: #fff; border-bottom: 1px solid #e7e5e4;
  box-sizing: border-box; flex-shrink: 0;
}
.fp-xs-header-left { display: flex; align-items: center; gap: 12px; }
.fp-xs-header h2 { margin: 0; font-size: 18px; font-weight: 700; color: #1c1917; }
.fp-xs-header a, .fp-xs-header button {
  display: grid; place-items: center; width: 24px; height: 24px;
  padding: 0; border: 0; background: transparent; cursor: pointer;
}
.fp-xs-header img { width: 24px; height: 24px; display: block; }
.fp-xs-body {
  display: flex; flex-direction: column; gap: 20px; padding: 16px; box-sizing: border-box;
}
.fp-xs-filters {
  display: flex; gap: 2px; padding: 4px; border-radius: 100px; background: #f5f5f4; width: 100%;
  box-sizing: border-box;
}
.fp-xs-filters button {
  flex: 1; margin: 0; border: 0; border-radius: 100px; padding: 8px 0;
  background: transparent; color: #78716c; font-size: 13px; font-weight: 500; cursor: pointer;
}
.fp-xs-filters button.active {
  background: #fff; color: #1c1917; font-weight: 700;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06);
}
.fp-xs-card {
  display: flex; flex-direction: column; gap: 16px; padding: 16px;
  border-radius: 16px; background: #fff; border: 1px solid #e7e5e4; box-sizing: border-box;
}
.fp-xs-card-head {
  display: flex; align-items: center; justify-content: space-between; gap: 8px;
}
.fp-xs-card-head strong { font-size: 15px; font-weight: 700; color: #1c1917; }
.fp-xs-card-head em { font-style: normal; font-size: 16px; font-weight: 700; color: #d97706; }
.fp-xs-card-title { font-size: 15px; font-weight: 700; color: #1c1917; }
.fp-xs-chart { width: 100%; height: 140px; position: relative; overflow: hidden; }
.fp-xs-chart-img { width: 100%; height: 140px; object-fit: contain; object-position: left center; display: block; }
.fp-xs-metrics { display: flex; gap: 12px; width: 100%; }
.fp-xs-metrics > div {
  flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px;
  padding: 10px; border-radius: 8px; background: #f5f5f4; box-sizing: border-box;
}
.fp-xs-metrics span { color: #78716c; font-size: 10px; }
.fp-xs-metrics strong {
  color: #1c1917; font-size: 15px; font-weight: 700;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.fp-xs-metrics > div:last-child strong { font-size: 12px; }
.fp-xs-streak { display: flex; flex-direction: column; gap: 6px; align-items: center; width: 100%; }
.fp-xs-streak-row { display: flex; gap: 6px; }
.fp-xs-streak-row > i {
  display: block; width: 34px; height: 34px; border-radius: 6px; flex-shrink: 0;
}
.fp-xs-streak-row > i.today {
  position: relative; background: transparent; padding: 0; overflow: hidden;
}
.fp-xs-streak-row > i.today img { width: 34px; height: 34px; display: block; }
.fp-xs-streak-meta {
  display: flex; align-items: center; justify-content: space-between; width: 100%;
}
.fp-xs-streak-meta > div { display: flex; flex-direction: column; gap: 2px; }
.fp-xs-streak-meta > div.end { align-items: flex-end; text-align: right; }
.fp-xs-streak-meta span { color: #78716c; font-size: 11px; }
.fp-xs-streak-meta strong { color: #1c1917; font-size: 14px; font-weight: 700; }
.fp-xs-streak-meta strong.green { color: #16a34a; font-size: 15px; }
.fp-xs-hint {
  display: flex; align-items: center; gap: 10px; padding: 12px;
  border-radius: 10px; background: #fef3c7; box-sizing: border-box; width: 100%;
}
.fp-xs-hint > span { font-size: 20px; line-height: 1; }
.fp-xs-hint p { margin: 0; flex: 1; color: #d97706; font-size: 13px; font-weight: 600; }
.fp-xs-home {
  height: 20px; display: flex; align-items: center; justify-content: center;
  padding: 12px 0 8px; flex-shrink: 0; box-sizing: content-box;
}
.fp-xs-home::after {
  content: ""; width: 134px; height: 5px; border-radius: 100px; background: #1c1917;
}

/* --- 07.6 Themen Heatmap (light) --- */
.app-frame[data-chrome="fp"]:has(.fp-hm-screen) {
  height: 1003px; min-height: 1003px; background: #fafaf9;
}
.app-frame[data-chrome="fp"]:has(.fp-hm-screen) .app-status { color: #1c1917; }
.app-frame[data-chrome="fp"]:has(.fp-hm-screen) .login-status-icon { filter: none; }
.app-frame[data-chrome="fp"]:has(.fp-hm-screen) .app-content { background: #fafaf9; }
.fp-hm-screen {
  background: #fafaf9; color: #1c1917; justify-content: space-between;
}
.fp-hm-scroll { flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; }
.fp-hm-body {
  display: flex; flex-direction: column; gap: 24px; padding: 16px; box-sizing: border-box;
}
.fp-hm-radar-wrap {
  display: flex; align-items: center; justify-content: center; padding: 10px 0; width: 100%;
}
.fp-hm-radar { width: 240px; height: 240px; display: block; object-fit: contain; }
.fp-hm-ai {
  display: flex; align-items: center; gap: 12px; padding: 14px;
  border-radius: 12px; background: #f0fdfa; border: 1px solid #0d9488; box-sizing: border-box;
}
.fp-hm-ai-ico {
  display: grid; place-items: center; width: 36px; height: 36px; border-radius: 18px;
  background: #fff; flex-shrink: 0;
}
.fp-hm-ai-ico img { width: 20px; height: 20px; display: block; }
.fp-hm-ai p {
  margin: 0; flex: 1; min-width: 0; color: #0f766e; font-size: 13px; font-weight: 600; line-height: 1.4;
}
.fp-hm-section { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.fp-hm-section h3 { margin: 0; color: #1c1917; font-size: 15px; font-weight: 700; }
.fp-hm-ranks { display: flex; flex-direction: column; gap: 4px; width: 100%; }
.fp-hm-rank {
  display: flex; align-items: center; gap: 12px; padding: 10px;
  border-radius: 8px; background: #fff; border: 1px solid #f5f5f4; box-sizing: border-box;
}
.fp-hm-rank-n {
  width: 18px; flex-shrink: 0; color: #78716c; font-size: 12px; font-weight: 700;
}
.fp-hm-rank-body { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 4px; }
.fp-hm-rank-body strong { color: #1c1917; font-size: 13px; font-weight: 600; }
.fp-hm-rank-bar-row { display: flex; align-items: center; gap: 8px; width: 100%; }
.fp-hm-rank-track {
  width: 160px; height: 6px; border-radius: 3px; background: #f5f5f4; overflow: hidden; flex-shrink: 0;
}
.fp-hm-rank-track > i { display: block; height: 100%; }
.fp-hm-rank-track > i.green { background: #16a34a; }
.fp-hm-rank-track > i.blue { background: #2563eb; }
.fp-hm-rank-track > i.orange { background: #d97706; }
.fp-hm-rank-track > i.red { background: #dc2626; }
.fp-hm-rank-track > i.muted { background: #a8a29e; }
.fp-hm-rank-bar-row em {
  font-style: normal; font-size: 11px; font-weight: 700; color: #1c1917; white-space: nowrap;
}
.fp-hm-rank-stars {
  flex-shrink: 0; font-size: 12px; color: #000; text-align: right; white-space: nowrap;
}
.fp-hm-rank.locked .fp-hm-rank-body strong,
.fp-hm-rank.locked .fp-hm-rank-bar-row em { color: #a8a29e; }
'''

css = css_path.read_text(encoding="utf-8")
marker = "/* --- 07.4 Statistik Verlauf --- */"
end_marker = ".fp-hm-rank.locked .fp-hm-rank-body strong,\n.fp-hm-rank.locked .fp-hm-rank-bar-row em { color: #a8a29e; }"
block = css_block.strip() + "\n"
if marker in css:
    start = css.find(marker)
    end = css.find(end_marker, start)
    if end != -1:
        end = end + len(end_marker)
        while end < len(css) and css[end] in "\r\n":
            end += 1
        css = css[:start] + block + css[end:]
    else:
        css = css[:start] + block
else:
    css = css.rstrip() + "\n\n" + block

css_path.write_text(css, encoding="utf-8")
print("ui.css updated")
