# Generate GX consistency screens + patch core files.
from pathlib import Path
import re

ROOT = Path(r"C:\dev\Repositories\Online-Lerncampus")
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

home = f'''
  "s19_1-home-dashboard": () => `
    <section class="gx-screen gx-home" data-node-id="159:13">
      <div class="gx-scroll">
        {status_bar()}
        <div class="gx-home-header">
          <div class="gx-profile-meta">
            <div class="gx-avatar-ring"><img class="gx-avatar" src="{GX}/avatar.png" width="44" height="44" alt="" /></div>
            <div class="gx-welcome">
              <p>Guten Morgen,</p>
              <strong data-bind="greeting-name">Hallo, Max!</strong>
            </div>
          </div>
          <span class="gx-level-pill"><span data-bind="level-label">Level 7</span></span>
        </div>
        <div class="gx-gamification-row">
          <div class="gx-stat-box">
            <span class="gx-emoji" aria-hidden="true">🔥</span>
            <div><strong data-bind="streak-days">12 Tage</strong><span>Lern-Streak</span></div>
          </div>
          <div class="gx-stat-box">
            <span class="gx-emoji" aria-hidden="true">⭐</span>
            <div><strong class="gx-xp" data-bind="xp">2.450 XP</strong><span>Gesamtpunkte</span></div>
          </div>
        </div>
        <div class="gx-body">
          <a class="gx-card gx-continue" href="/lernen" data-page-link>
            <div class="gx-card-head">
              <div>
                <p class="gx-kicker">AKTIVITÄT FORTSETZEN</p>
                <strong data-bind="continue-title">Pneumatik — Schaltpläne</strong>
              </div>
              <img src="{GX}/chevron-right.svg" width="20" height="20" alt="" />
            </div>
            <div class="gx-progress-block">
              <div class="gx-progress-meta"><span>Lerneinheit 3 von 5</span><strong data-bind="continue-progress">12 / 30 Fragen</strong></div>
              <div class="gx-bar"><i data-bind="continue-bar" style="width:42%"></i></div>
            </div>
          </a>
          <article class="gx-card gx-goal">
            <div class="gx-goal-row">
              <div class="gx-ring" aria-hidden="true">
                <img class="gx-ring-track" src="{GX}/ring-track.svg" width="56" height="56" alt="" />
                <img class="gx-ring-fill" src="{GX}/ring-fill.svg" width="56" height="56" alt="" />
                <span>60%</span>
              </div>
              <div>
                <strong data-bind="daily-goal">Tagesziel: 3 von 5 Lektionen</strong>
                <p data-bind="daily-remaining">Noch 2 Lektionen bis zum Tagesbonus (+50 XP)!</p>
              </div>
            </div>
          </article>
          <div class="gx-section">
            <p class="gx-section-label">SCHNELLSTARTER</p>
            <div class="gx-chips">
              <a class="gx-chip" href="/lernen/fragen" data-page-link><img src="{GX}/pencil.svg" width="14" height="14" alt="" />Fragen üben</a>
              <a class="gx-chip" href="/pruefungen" data-page-link><img src="{GX}/play.svg" width="14" height="14" alt="" />Prüfung simulieren</a>
              <a class="gx-chip" href="/berichtsheft" data-page-link><img src="{GX}/folder.svg" width="14" height="14" alt="" />Berichtsheft</a>
            </div>
          </div>
          <div class="gx-section">
            <p class="gx-section-label">AKTIVITÄT DIESE WOCHE</p>
            <div class="gx-week">
              <div class="gx-day done"><i></i><span>Mo</span></div>
              <div class="gx-day done"><i></i><span>Di</span></div>
              <div class="gx-day done"><i></i><span>Mi</span></div>
              <div class="gx-day"><i></i><span>Do</span></div>
              <div class="gx-day"><i></i><span>Fr</span></div>
              <div class="gx-day"><i></i><span>Sa</span></div>
              <div class="gx-day"><i></i><span>So</span></div>
            </div>
          </div>
        </div>
      </div>
      {bottom_nav("home")}
    </section>
  `,
'''

lernen = f'''
  "s19_2-lernen-journey": () => `
    <section class="gx-screen gx-lernen" data-node-id="159:129">
      <div class="gx-scroll">
        {status_bar()}
        <div class="gx-page-header">
          <div class="gx-page-title-row">
            <h2>Lernpfad</h2>
            <span class="gx-badge-green">42% abgeschlossen</span>
          </div>
          <p>Metall — Grundlagen</p>
        </div>
        <div class="gx-path">
          <div class="gx-path-row left">
            <div class="gx-node done"><img src="{GX}/check.svg" width="24" height="24" alt="" /></div>
            <div class="gx-node-text"><strong>Werkstoffkunde</strong><span class="ok">+30 XP</span></div>
          </div>
          <div class="gx-path-connector ok" aria-hidden="true"></div>
          <div class="gx-path-row right">
            <div class="gx-node-text end"><strong>Messtechnik</strong><span class="ok">+30 XP</span></div>
            <div class="gx-node done"><img src="{GX}/check.svg" width="24" height="24" alt="" /></div>
          </div>
          <div class="gx-path-connector ok" aria-hidden="true"></div>
          <div class="gx-path-row left">
            <div class="gx-node current"><img src="{GX}/target.svg" width="24" height="24" alt="" /></div>
            <div class="gx-node-text"><strong>Toleranzen</strong><span class="now">+40 XP</span></div>
          </div>
          <div class="gx-path-connector muted" aria-hidden="true"></div>
          <div class="gx-path-row right">
            <div class="gx-node-text end"><strong>Drehen</strong><span class="muted">+30 XP</span></div>
            <div class="gx-node locked"><img src="{GX}/lock.svg" width="22" height="22" alt="" /></div>
          </div>
          <div class="gx-path-connector muted" aria-hidden="true"></div>
          <div class="gx-path-row left">
            <div class="gx-node locked"><img src="{GX}/lock.svg" width="22" height="22" alt="" /></div>
            <div class="gx-node-text"><strong>Fräsen</strong><span class="muted">+30 XP</span></div>
          </div>
          <div class="gx-path-connector muted" aria-hidden="true"></div>
          <div class="gx-locked-topic">
            <img src="{GX}/lock-lg.svg" width="24" height="24" alt="" />
            <strong>Themengebiet 2: Pneumatik</strong>
            <span>Noch gesperrt</span>
          </div>
        </div>
        <div class="gx-recommend-wrap">
          <a class="gx-recommend" href="/lernen/frage" data-page-link>
            <img src="{GX}/compass.svg" width="24" height="24" alt="" />
            <div>
              <p class="gx-kicker">NÄCHSTE EMPFEHLUNG</p>
              <strong>Lernmodul: Toleranzen &amp; Passungen</strong>
            </div>
            <span class="gx-btn-start">Starten</span>
          </a>
        </div>
      </div>
      {bottom_nav("learn")}
    </section>
  `,
'''

pruefung = f'''
  "s19_3-pruefung-hub": () => `
    <section class="gx-screen gx-pruefung" data-node-id="159:229">
      <div class="gx-scroll">
        {status_bar()}
        <div class="gx-page-header">
          <h2>IHK-Prüfungsvorbereitung</h2>
          <p>Simuliere echte Prüfungsverfahren</p>
        </div>
        <div class="gx-body">
          <article class="gx-card gx-exam-hero">
            <div class="gx-exam-hero-top">
              <div>
                <p class="gx-kicker light">NÄCHSTE PRÜFUNG</p>
                <strong>IHK Zwischenprüfung</strong>
              </div>
              <span class="gx-pill-blue">In 47 Tagen</span>
            </div>
            <div class="gx-progress-block light">
              <div class="gx-progress-meta"><span>Deine IHK-Prüfungsreife</span><strong data-bind="readiness">67% bereit</strong></div>
              <div class="gx-bar dark"><i style="width:67%"></i></div>
            </div>
          </article>
          <div class="gx-section">
            <p class="gx-section-label">PRÜFUNG SIMULIEREN</p>
            <div class="gx-sim-grid">
              <a class="gx-card gx-sim" href="/pruefungen/frage" data-page-link data-action="exam-start-shortcut">
                <img src="{GX}/clock.svg" width="24" height="24" alt="" />
                <strong>Zwischenprüfung</strong>
                <span>45 Fragen • 60 Min</span>
                <em class="ok">Bestwert: 72%</em>
              </a>
              <a class="gx-card gx-sim" href="/pruefungen/frage" data-page-link data-action="exam-start-shortcut">
                <img src="{GX}/star.svg" width="24" height="24" alt="" />
                <strong>AP Teil 1</strong>
                <span>Gestreckt • 90 Min</span>
                <em>Noch kein Wert</em>
              </a>
            </div>
          </div>
          <div class="gx-section">
            <p class="gx-section-label">LETZTE ERGEBNISSE</p>
            <div class="gx-results">
              <a class="gx-card gx-result" href="/pruefungen/bestanden" data-page-link>
                <div><strong>Teilprüfung: Zwischenprüfung</strong><span>Gestern</span></div>
                <div class="gx-score ok">72%<i></i></div>
              </a>
              <a class="gx-card gx-result" href="/pruefungen/schwach" data-page-link>
                <div><strong>Themenprüfung: Pneumatik</strong><span>Vor 3 Tagen</span></div>
                <div class="gx-score warn">65%<i></i></div>
              </a>
              <a class="gx-card gx-result" href="/pruefungen/bestanden" data-page-link>
                <div><strong>Lernbereich: Arbeitssicherheit</strong><span>Vor 1 Woche</span></div>
                <div class="gx-score ok">88%<i></i></div>
              </a>
            </div>
          </div>
        </div>
      </div>
      {bottom_nav("exam")}
    </section>
  `,
'''

fortschritt = f'''
  "s19_4-fortschritt-stats": () => `
    <section class="gx-screen gx-fortschritt" data-node-id="159:320">
      <div class="gx-scroll">
        {status_bar()}
        <div class="gx-page-header">
          <h2>Fortschritt &amp; Erfolge</h2>
          <p>Deine IHK-Leistungsstatistik</p>
        </div>
        <div class="gx-body">
          <article class="gx-card gx-ready">
            <div class="gx-ready-top">
              <div class="gx-donut" aria-hidden="true">
                <img class="gx-ring-track" src="{GX}/donut-track.svg" width="64" height="64" alt="" />
                <img class="gx-ring-fill gx-donut-fill" src="{GX}/donut-fill.svg" width="64" height="64" alt="" />
                <span data-bind="readiness-pct">67%</span>
              </div>
              <div>
                <strong>IHK Prüfungsreife</strong>
                <p>Exzellente Woche! Du bist auf dem besten Weg zur IHK-Zertifizierung.</p>
              </div>
            </div>
            <img class="gx-divider" src="{GX}/divider.svg" alt="" />
            <div class="gx-progress-block">
              <div class="gx-progress-meta"><span>Nächstes Level (Level 8)</span><strong class="gx-xp" data-bind="xp-level">2.450 / 3.000 XP</strong></div>
              <div class="gx-bar"><i style="width:82%"></i></div>
            </div>
          </article>
          <div class="gx-section">
            <p class="gx-section-label">DEIN LERNPFAD</p>
            <div class="gx-card gx-path-list">
              <div class="gx-path-item"><img src="{GX}/check-circle.svg" width="18" height="18" alt="" /><div><strong>Metalltechnische Grundlagen</strong><span>Erledigt</span></div></div>
              <div class="gx-path-item"><img src="{GX}/fp-clock.svg" width="18" height="18" alt="" /><div><strong>Zwischenprüfungsvorbereitung</strong><span>In Arbeit (45%)</span></div></div>
              <div class="gx-path-item muted"><img src="{GX}/fp-lock.svg" width="18" height="18" alt="" /><div><strong>Vertiefungsmodule IHK</strong><span>Nicht gestartet</span></div></div>
            </div>
          </div>
          <div class="gx-section">
            <p class="gx-section-label">DEINE ERFOLGE</p>
            <div class="gx-card gx-badges">
              <div class="gx-badge-row">
                <div class="gx-badge on"><i>🚀</i><span>Pionier</span></div>
                <div class="gx-badge on"><i>🔥</i><span>Streak-Pro</span></div>
                <div class="gx-badge on"><i>💯</i><span>100% Perfekt</span></div>
                <div class="gx-badge on"><i>⚡</i><span>Speedy</span></div>
              </div>
              <div class="gx-badge-row">
                <div class="gx-badge off"><i>🛡️</i><span>Prüfer</span></div>
                <div class="gx-badge off"><i>⚙️</i><span>Zahnrad</span></div>
                <div class="gx-badge off"><i>📐</i><span>Mikrometer</span></div>
                <div class="gx-badge off"><i>🤖</i><span>KI-Assistent</span></div>
              </div>
            </div>
          </div>
          <div class="gx-section">
            <p class="gx-section-label">WOCHENSTATISTIK</p>
            <div class="gx-card gx-week-bars">
              <div class="gx-wbar"><i style="height:60px"></i><span>M</span></div>
              <div class="gx-wbar"><i style="height:80px"></i><span>D</span></div>
              <div class="gx-wbar"><i style="height:45px"></i><span>M</span></div>
              <div class="gx-wbar muted"><i style="height:20px"></i><span>D</span></div>
              <div class="gx-wbar muted"><i style="height:4px"></i><span>F</span></div>
              <div class="gx-wbar muted"><i style="height:4px"></i><span>S</span></div>
              <div class="gx-wbar muted"><i style="height:4px"></i><span>S</span></div>
            </div>
          </div>
        </div>
      </div>
      {bottom_nav("progress")}
    </section>
  `,
'''

profil = f'''
  "s19_5-profil-settings": () => `
    <section class="gx-screen gx-profil" data-node-id="159:456">
      <div class="gx-scroll">
        {status_bar()}
        <div class="gx-profil-header">
          <img class="gx-avatar-lg" src="{GX}/avatar-profil.png" width="72" height="72" alt="" />
          <strong data-bind="profile-name">Max Müller</strong>
          <p>Verfahrensmechaniker — 2. Lehrjahr</p>
          <span class="gx-level-pill soft">Level 7 Lehrling</span>
        </div>
        <div class="gx-stats-panel">
          <div class="gx-mini-stat"><strong class="blue" data-bind="xp-num">2.450</strong><span>Punkte (XP)</span></div>
          <div class="gx-mini-stat"><strong class="amber" data-bind="streak">12 Tage</strong><span>Streak</span></div>
          <div class="gx-mini-stat"><strong class="green">8</strong><span>Abzeichen</span></div>
        </div>
        <div class="gx-body">
          <a class="gx-card gx-alert" href="/berichtsheft" data-page-link>
            <div>
              <strong>Berichtsheft-Prüfung</strong>
              <p>Ausbildungsnachweis 12 von 24 Wochen gepflegt</p>
            </div>
            <span class="gx-pill-red">3 fehlen</span>
          </a>
          <a class="gx-card gx-coach" href="/mehr/coach" data-page-link>
            <span class="gx-emoji" aria-hidden="true">🤖</span>
            <div>
              <strong>Dein KI-Lerncoach</strong>
              <p>Frage den Assistenten zu IHK Prüfungsaufgaben.</p>
            </div>
            <img src="{GX}/arrow-right.svg" width="18" height="18" alt="" />
          </a>
          <div class="gx-section">
            <p class="gx-section-label sm">EINSTELLUNGEN</p>
            <div class="gx-settings">
              <a href="/mehr/benachrichtigungen" data-page-link><span><img src="{GX}/bell.svg" width="18" height="18" alt="" />Benachrichtigungen</span><img src="{GX}/chevron-sm.svg" width="16" height="16" alt="" /></a>
              <a href="/sprache" data-page-link><span><img src="{GX}/globe.svg" width="18" height="18" alt="" />Sprache</span><img src="{GX}/chevron-sm.svg" width="16" height="16" alt="" /></a>
              <a href="/dashboard/tagesziel" data-page-link><span><img src="{GX}/target.svg" width="18" height="18" alt="" />Tagesziel anpassen</span><img src="{GX}/chevron-sm.svg" width="16" height="16" alt="" /></a>
              <a href="/mehr/export" data-page-link><span><img src="{GX}/download.svg" width="18" height="18" alt="" />Datenexport (Berichtsheft)</span><img src="{GX}/chevron-sm.svg" width="16" height="16" alt="" /></a>
              <a href="/mehr/ausbilder-sicht" data-page-link><span><img src="{GX}/help.svg" width="18" height="18" alt="" />Hilfe &amp; Support</span><img src="{GX}/chevron-sm.svg" width="16" height="16" alt="" /></a>
            </div>
          </div>
          <a class="gx-logout" href="/mehr/logout" data-page-link>Abmelden</a>
        </div>
      </div>
      {bottom_nav("profile")}
    </section>
  `,
'''

# Patch screens.js routes
screens = (ROOT / "app/web/static/screens.js").read_text(encoding="utf-8")

replacements = {
    '"/dashboard": { layout: "app", screen: "s03_1-dashboard-default", title: "Dashboard - Default", tab: "dashboard", num: "03.1" },':
    '"/dashboard": { layout: "app", screen: "s19_1-home-dashboard", title: "Home Dashboard", tab: "dashboard", num: "19.1", chrome: "gx" },',
    '"/lernen": { layout: "app", screen: "s04_1-lernen-hub", title: "Lernen Hub", tab: "learn", num: "04.1" },':
    '"/lernen": { layout: "app", screen: "s19_2-lernen-journey", title: "Lernen Journey", tab: "learn", num: "19.2", chrome: "gx" },',
    '"/pruefungen": { layout: "app", screen: "s06_1-pruefungsliste", title: "Prüfungsliste", tab: "exam", num: "06.1", chrome: "exam" },':
    '"/pruefungen": { layout: "app", screen: "s19_3-pruefung-hub", title: "Prüfung Hub", tab: "exam", num: "19.3", chrome: "gx" },',
    '"/fortschritt": { layout: "app", screen: "s07_1-fortschritt-uebersicht", title: "Fortschritt — Übersicht", tab: "progress", num: "07.1", chrome: "fp" },':
    '"/fortschritt": { layout: "app", screen: "s19_4-fortschritt-stats", title: "Fortschritt Stats", tab: "progress", num: "19.4", chrome: "gx" },',
    '"/mehr": { layout: "app", screen: "s09_1-mehr-und-profil-uebersicht", title: "Mehr & Profil — Übersicht", tab: "profile", num: "09.1", chrome: "mehr" },':
    '"/mehr": { layout: "app", screen: "s19_5-profil-settings", title: "Profil Settings", tab: "profile", num: "19.5", chrome: "gx" },',
}
for old, new in replacements.items():
    if old not in screens:
        raise SystemExit(f"Route not found: {old[:80]}")
    screens = screens.replace(old, new, 1)

# Keep legacy hubs reachable
legacy = '''
  "/dashboard/legacy": { layout: "app", screen: "s03_1-dashboard-default", title: "Dashboard Legacy", tab: "dashboard", num: "03.1" },
  "/lernen/hub-legacy": { layout: "app", screen: "s04_1-lernen-hub", title: "Lernen Hub Legacy", tab: "learn", num: "04.1" },
  "/pruefungen/liste-legacy": { layout: "app", screen: "s06_1-pruefungsliste", title: "Prüfungsliste Legacy", tab: "exam", num: "06.1", chrome: "exam" },
  "/fortschritt/uebersicht-legacy": { layout: "app", screen: "s07_1-fortschritt-uebersicht", title: "Fortschritt Legacy", tab: "progress", num: "07.1", chrome: "fp" },
  "/mehr/hub-legacy": { layout: "app", screen: "s09_1-mehr-und-profil-uebersicht", title: "Mehr Hub Legacy", tab: "profile", num: "09.1", chrome: "mehr" },
'''
if '"/dashboard/legacy"' not in screens:
    screens = screens.replace(
        '"/dashboard/tagesziel":',
        legacy + '  "/dashboard/tagesziel":',
        1,
    )

# Insert screen templates before closing of OLC_SCREENS object
marker = '  "s03_1-dashboard-default":'
if '"s19_1-home-dashboard"' not in screens:
    screens = screens.replace(marker, home + lernen + pruefung + fortschritt + profil + marker, 1)

(ROOT / "app/web/static/screens.js").write_text(screens, encoding="utf-8")
print("screens.js patched")

# Update allowed_pages.json if present
ap = ROOT / "app/web/allowed_pages.json"
if ap.exists():
    import json
    pages = json.loads(ap.read_text(encoding="utf-8"))
    for p in [
        "/dashboard/legacy",
        "/lernen/hub-legacy",
        "/pruefungen/liste-legacy",
        "/fortschritt/uebersicht-legacy",
        "/mehr/hub-legacy",
    ]:
        if p not in pages:
            pages.append(p)
    ap.write_text(json.dumps(sorted(pages), indent=2) + "\n", encoding="utf-8")
    print("allowed_pages updated", len(pages))
