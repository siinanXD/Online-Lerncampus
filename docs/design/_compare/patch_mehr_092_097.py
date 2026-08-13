# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(r"C:\dev\Repositories\Online-Lerncampus")
SCREENS = ROOT / "app/web/static/screens.js"
CSS = ROOT / "app/web/static/ui.css"
APP = ROOT / "app/web/static/app.js"

js = SCREENS.read_text(encoding="utf-8")
js = js.replace(
    '"/mehr/ausbilder-sicht": { layout: "app", screen: "s09_2-was-sieht-der-ausbilder", title: "Was sieht der Ausbilder", tab: "profile", num: "09.2" }',
    '"/mehr/ausbilder-sicht": { layout: "app", screen: "s09_2-was-sieht-der-ausbilder", title: "Was sieht der Ausbilder", tab: "profile", num: "09.2", chrome: "mehr" }',
)
js = js.replace(
    '"/mehr/logout": { layout: "app", screen: "s09_7-logout-bestaetigung", title: "Logout Bestätigung", tab: "profile", num: "09.7" }',
    '"/mehr/logout": { layout: "app", screen: "s09_7-logout-bestaetigung", title: "Logout Bestätigung", tab: "profile", num: "09.7", chrome: "mehr" }',
)

s092 = r'''  "s09_2-was-sieht-der-ausbilder": () => `
      <div class="tr-screen" data-node-id="136:11038">
        <div class="tr-main">
          <header class="tr-header">
            <a class="tr-back" href="/mehr" data-page-link aria-label="Zurück">
              <img src="/static/figma/mehr/tr-back.svg" width="20" height="20" alt="" />
            </a>
            <h2>Transparenz</h2>
            <span class="tr-badge">BZE Safe</span>
          </header>
          <div class="tr-scroll">
            <article class="tr-hero">
              <div class="tr-hero-top">
                <span class="tr-hero-ico"><img src="/static/figma/mehr/tr-eye.svg" width="16" height="16" alt="" /></span>
                <strong>Was sieht dein Ausbilder?</strong>
              </div>
              <p>Hier siehst du genau, welche Daten für deinen Ausbilder sichtbar sind. Wir schützen deine Privatsphäre.</p>
            </article>
            <section class="tr-section">
              <p class="tr-label ok">Sichtbar für Ausbilder</p>
              <div class="tr-list">
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Gesamtfortschritt (%)</span></div><em>Dein Ausbilder sieht: 67%</em></div>
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Prüfungsreife (%)</span></div><em data-bind="readiness">67%</em></div>
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Lernzeit (gesamt)</span></div><em>42h</em></div>
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Berichtsheft-Einträge</span></div><em>Status und Inhalt</em></div>
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Prüfungsergebnisse</span></div><em>Note und Datum</em></div>
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Letzte Aktivität</span></div><em>vor 2 Stunden</em></div>
                <div class="tr-row"><div><img src="/static/figma/mehr/tr-check.svg" width="16" height="16" alt="" /><span>Schwache Themen</span></div><em>Top 3</em></div>
              </div>
            </section>
            <section class="tr-section">
              <p class="tr-label danger">Nicht sichtbar (Privat)</p>
              <div class="tr-list">
                <div class="tr-row stack"><div><img src="/static/figma/mehr/tr-x.svg" width="16" height="16" alt="" /><div><span>Einzelne Antworten</span><small>Nur du siehst deine Fehler im Detail</small></div></div></div>
                <div class="tr-row stack"><div><img src="/static/figma/mehr/tr-x.svg" width="16" height="16" alt="" /><div><span>Lernzeit pro Tag</span><small>Nur Gesamt sichtbar</small></div></div></div>
                <div class="tr-row stack"><div><img src="/static/figma/mehr/tr-x.svg" width="16" height="16" alt="" /><div><span>Chat mit KI-Coach</span><small>Deine Gespräche sind privat</small></div></div></div>
                <div class="tr-row stack"><div><img src="/static/figma/mehr/tr-x.svg" width="16" height="16" alt="" /><div><span>Merklisten &amp; Notizen</span><small>Nur für dich</small></div></div></div>
                <div class="tr-row stack"><div><img src="/static/figma/mehr/tr-x.svg" width="16" height="16" alt="" /><div><span>Streak-Details</span><small>Nur du siehst deinen Streak</small></div></div></div>
              </div>
            </section>
            <article class="tr-note">
              <img src="/static/figma/mehr/tr-info.svg" width="18" height="18" alt="" />
              <p>Dein Ausbilder kann dich nicht überwachen. Er sieht nur zusammengefasste Daten, um dich besser zu unterstützen.</p>
            </article>
          </div>
        </div>
        <nav class="tr-tabs" aria-label="Navigation">
          <a href="/lernen" data-page-link><img src="/static/figma/mehr/tr-book.svg" width="20" height="20" alt="" /><span>Lernen</span></a>
          <a href="/fortschritt" data-page-link><img src="/static/figma/mehr/tr-chart.svg" width="20" height="20" alt="" /><span>Statistik</span></a>
          <a href="/dashboard" data-page-link><img src="/static/figma/mehr/tr-award.svg" width="20" height="20" alt="" /><span>Campus</span></a>
          <a href="/mehr" data-page-link class="active"><img src="/static/figma/mehr/tr-menu.svg" width="20" height="20" alt="" /><span>Mehr</span></a>
        </nav>
        <div class="tr-home" aria-hidden="true"><i></i></div>
      </div>
    `,'''

s097 = r'''  "s09_7-logout-bestaetigung": () => `
      <div class="lo-screen" data-node-id="136:11535">
        <div class="lo-dim">
          <div class="lo-spacer"></div>
          <div class="lo-modal" role="dialog" aria-labelledby="lo-title">
            <div class="lo-ico"><img src="/static/figma/mehr/lo-hand.svg" width="40" height="40" alt="" /></div>
            <h2 id="lo-title">Wirklich abmelden?</h2>
            <p>Dein Streak von 14 Tagen bleibt erhalten, wenn du morgen wiederkommst!</p>
            <div class="lo-streak"><img src="/static/figma/mehr/lo-flame.svg" width="16" height="16" alt="" /><span>🔥 14 Tage</span></div>
            <div class="lo-actions">
              <button class="lo-yes" type="button" data-action="logout">Abmelden</button>
              <a class="lo-no" href="/mehr" data-page-link>Doch nicht</a>
            </div>
          </div>
          <nav class="lo-tabs" aria-label="Hauptnavigation">
            <a href="/dashboard" data-page-link><img src="/static/figma/mehr/lo-house.svg" width="22" height="22" alt="" /><span>Start</span></a>
            <a href="/lernen" data-page-link><img src="/static/figma/mehr/lo-book.svg" width="22" height="22" alt="" /><span>Lernen</span></a>
            <a href="/fortschritt" data-page-link><img src="/static/figma/mehr/lo-trend.svg" width="22" height="22" alt="" /><span>Fortschritt</span></a>
            <a href="/berichtsheft" data-page-link><img src="/static/figma/mehr/lo-file.svg" width="22" height="22" alt="" /><span>Bericht</span></a>
            <a href="/mehr" data-page-link class="active"><img src="/static/figma/mehr/lo-menu.svg" width="22" height="22" alt="" /><span>Mehr</span></a>
          </nav>
        </div>
      </div>
    `,'''

for key, block in [
    ("s09_2-was-sieht-der-ausbilder", s092),
    ("s09_7-logout-bestaetigung", s097),
]:
    pat = re.compile(rf'  "{key}": \(\) => `[\s\S]*?`,\n(?=  ")')
    if not pat.search(js):
        raise SystemExit(f"missing {key}")
    js = pat.sub(block + "\n", js, count=1)
SCREENS.write_text(js, encoding="utf-8")
print("screens ok")

css_extra = r'''
/* --- 09.2 Transparenz --- */
.app-frame[data-chrome="mehr"]:has(.tr-screen) { background: #0b132b; }
.app-frame[data-chrome="mehr"]:has(.tr-screen) .app-content { background: #0b132b; }
.tr-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #0b132b; color: #fff;
}
.tr-main { flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.tr-header {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  height: 56px; padding: 0 20px; border-bottom: 1px solid rgba(255,255,255,0.08); box-sizing: border-box;
}
.tr-back { display: grid; place-items: center; width: 20px; height: 20px; flex-shrink: 0; }
.tr-back img { width: 20px; height: 20px; display: block; }
.tr-header h2 { margin: 0; flex: 1; font-size: 18px; font-weight: 700; color: #fff; }
.tr-badge {
  padding: 4px 10px; border-radius: 12px; background: rgba(6,214,160,0.1);
  color: #06d6a0; font-size: 11px; font-weight: 700;
}
.tr-scroll {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 20px;
  padding: 20px; box-sizing: border-box;
}
.tr-hero {
  display: flex; flex-direction: column; gap: 12px; padding: 16px;
  border-radius: 16px; background: rgba(6,214,160,0.1); border: 1px solid #06d6a0; box-sizing: border-box;
}
.tr-hero-top { display: flex; align-items: center; gap: 10px; }
.tr-hero-ico {
  display: grid; place-items: center; width: 32px; height: 32px; border-radius: 16px; background: #06d6a0;
}
.tr-hero-ico img { width: 16px; height: 16px; display: block; filter: brightness(0); }
.tr-hero strong { color: #fff; font-size: 16px; font-weight: 700; }
.tr-hero p { margin: 0; color: #8d99ae; font-size: 13px; line-height: 1.4; }
.tr-section { display: flex; flex-direction: column; gap: 10px; width: 100%; }
.tr-label { margin: 0; font-size: 12px; font-weight: 700; text-transform: uppercase; }
.tr-label.ok { color: #06d6a0; }
.tr-label.danger { color: #ef4444; }
.tr-list { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.tr-row {
  display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 12px;
  border-radius: 10px; background: #1c2541; border: 1px solid rgba(255,255,255,0.08); box-sizing: border-box;
}
.tr-row > div { display: flex; align-items: center; gap: 10px; min-width: 0; }
.tr-row img { width: 16px; height: 16px; display: block; flex-shrink: 0; }
.tr-row span { color: #fff; font-size: 13px; font-weight: 600; }
.tr-row em { font-style: normal; color: #8d99ae; font-size: 12px; font-weight: 700; flex-shrink: 0; }
.tr-row.stack > div > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.tr-row small { color: #8d99ae; font-size: 11px; }
.tr-note {
  display: flex; gap: 12px; align-items: flex-start; padding: 14px;
  border-radius: 12px; background: #1c2541; border: 1px solid rgba(255,255,255,0.08); box-sizing: border-box;
}
.tr-note img { width: 18px; height: 18px; display: block; flex-shrink: 0; }
.tr-note p { margin: 0; color: #8d99ae; font-size: 12px; line-height: 1.4; }
.tr-tabs {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 12px 16px 8px; background: #1c2541; border-top: 1px solid rgba(255,255,255,0.08);
  box-sizing: border-box; flex-shrink: 0;
}
.tr-tabs a {
  display: flex; flex-direction: column; align-items: center; gap: 4px; width: 64px;
  color: #8d99ae; font-size: 10px; font-weight: 500; text-decoration: none;
}
.tr-tabs a.active { color: #3a86ff; font-weight: 700; }
.tr-tabs a.active img { filter: invert(42%) sepia(98%) saturate(1800%) hue-rotate(198deg) brightness(100%) contrast(95%); }
.tr-tabs img { width: 20px; height: 20px; display: block; }
.tr-home { display: flex; align-items: center; justify-content: center; padding: 21px 0 8px; flex-shrink: 0; }
.tr-home i { display: block; width: 134px; height: 5px; border-radius: 100px; background: #fff; }

/* --- 09.7 Logout Bestätigung --- */
.app-frame[data-chrome="mehr"]:has(.lo-screen) { background: #f8fafc; }
.app-frame[data-chrome="mehr"]:has(.lo-screen) .app-status { color: #fff; }
.app-frame[data-chrome="mehr"]:has(.lo-screen) .login-status-icon { filter: brightness(0) invert(1); }
.app-frame[data-chrome="mehr"]:has(.lo-screen) .app-content { background: #0f172a; }
.lo-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #f8fafc; position: relative;
}
.lo-dim {
  display: flex; flex-direction: column; flex: 1; min-height: 0; justify-content: space-between; align-items: center;
  background: rgba(15,23,42,0.6);
}
.lo-spacer { flex: 1; min-height: 0; }
.lo-modal {
  display: flex; flex-direction: column; align-items: center; gap: 20px; width: 320px;
  padding: 24px; border-radius: 24px; background: #fff;
  box-shadow: 0 12px 32px rgba(15,23,42,0.15); box-sizing: border-box; text-align: center;
}
.lo-ico {
  display: grid; place-items: center; width: 72px; height: 72px; border-radius: 36px; background: #f1f5f9;
}
.lo-ico img { width: 40px; height: 40px; display: block; }
.lo-modal h2 { margin: 0; color: #1e293b; font-size: 20px; font-weight: 700; width: 100%; }
.lo-modal > p { margin: 0; color: #64748b; font-size: 13px; line-height: 1.4; width: 100%; }
.lo-streak {
  display: inline-flex; align-items: center; gap: 6px; padding: 8px 14px; border-radius: 100px; background: #fef3c7;
}
.lo-streak img { width: 16px; height: 16px; display: block; }
.lo-streak span { color: #f59e0b; font-size: 14px; font-weight: 700; }
.lo-actions { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.lo-yes {
  width: 100%; padding: 12px 16px; border: 0; border-radius: 12px; background: #ef4444;
  color: #fff; font-size: 15px; font-weight: 600; cursor: pointer;
}
.lo-no {
  display: flex; align-items: center; justify-content: center; width: 100%; padding: 12px 16px;
  border-radius: 12px; color: #64748b; font-size: 15px; font-weight: 600; text-decoration: none;
}
.lo-tabs {
  display: flex; align-items: center; justify-content: space-between; width: 100%;
  height: 72px; padding: 0 0 8px; background: #fff; border-top: 1px solid #e2e8f0;
  box-sizing: border-box; flex-shrink: 0;
}
.lo-tabs a {
  display: flex; flex-direction: column; align-items: center; gap: 4px; width: 70px;
  color: #64748b; font-size: 11px; font-weight: 500; text-decoration: none;
}
.lo-tabs a.active { color: #2563eb; font-weight: 600; }
.lo-tabs a.active img {
  filter: invert(32%) sepia(98%) saturate(1800%) hue-rotate(204deg) brightness(95%) contrast(96%);
}
.lo-tabs img { width: 22px; height: 22px; display: block; }
'''

css = CSS.read_text(encoding="utf-8")
if "/* --- 09.2 Transparenz --- */" in css:
    css = css.split("/* --- 09.2 Transparenz --- */")[0].rstrip() + "\n" + css_extra
else:
    css = css.rstrip() + "\n" + css_extra
CSS.write_text(css, encoding="utf-8")
print("css ok")
