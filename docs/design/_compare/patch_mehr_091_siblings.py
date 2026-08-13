# -*- coding: utf-8 -*-
"""Patch 09.1 sibling phones: Profil / Darstellung / Benachrichtigungen."""
from pathlib import Path
import re

ROOT = Path(r"C:\dev\Repositories\Online-Lerncampus")
SCREENS = ROOT / "app/web/static/screens.js"
CSS = ROOT / "app/web/static/ui.css"

js = SCREENS.read_text(encoding="utf-8")

# routes after /mehr
route_block = '''  "/mehr": { layout: "app", screen: "s09_1-mehr-und-profil-uebersicht", title: "Mehr & Profil — Übersicht", tab: "profile", num: "09.1", chrome: "mehr" },
  "/mehr/profil": { layout: "app", screen: "s09_1b-mein-profil", title: "Mein Profil", tab: "profile", num: "09.1b", chrome: "mehr" },
  "/mehr/darstellung": { layout: "app", screen: "s09_1c-darstellung", title: "Darstellung", tab: "profile", num: "09.1c", chrome: "mehr" },
  "/mehr/benachrichtigungen": { layout: "app", screen: "s09_1d-benachrichtigungen", title: "Benachrichtigungen", tab: "profile", num: "09.1d", chrome: "mehr" },
'''
js = js.replace(
    '  "/mehr": { layout: "app", screen: "s09_1-mehr-und-profil-uebersicht", title: "Mehr & Profil — Übersicht", tab: "profile", num: "09.1", chrome: "mehr" },\n',
    route_block,
    1,
)

# hub links
js = js.replace(
    '<a class="mehr2-profile" href="/passwort" data-page-link>',
    '<a class="mehr2-profile" href="/mehr/profil" data-page-link>',
    1,
)
js = js.replace(
    '<a href="/passwort" data-page-link><span class="mehr2-ico"><img src="/static/figma/mehr/mehr-user.svg" width="16" height="16" alt="" /></span><span>Profil</span>',
    '<a href="/mehr/profil" data-page-link><span class="mehr2-ico"><img src="/static/figma/mehr/mehr-user.svg" width="16" height="16" alt="" /></span><span>Profil</span>',
    1,
)
js = js.replace(
    '<a href="/sprache" data-page-link><span class="mehr2-ico"><img src="/static/figma/mehr/mehr-eye.svg" width="16" height="16" alt="" /></span><span>Darstellung</span>',
    '<a href="/mehr/darstellung" data-page-link><span class="mehr2-ico"><img src="/static/figma/mehr/mehr-eye.svg" width="16" height="16" alt="" /></span><span>Darstellung</span>',
    1,
)
js = js.replace(
    '<a href="/mehr" data-page-link data-action="toast" data-toast="Benachrichtigungen folgen in einer späteren Version"><span class="mehr2-ico"><img src="/static/figma/mehr/mehr-bell.svg" width="16" height="16" alt="" /></span><span>Benachrichtigungen</span>',
    '<a href="/mehr/benachrichtigungen" data-page-link><span class="mehr2-ico"><img src="/static/figma/mehr/mehr-bell.svg" width="16" height="16" alt="" /></span><span>Benachrichtigungen</span>',
    1,
)

tabs = '''        <nav class="mp-tabs" aria-label="Navigation">
          <a href="/lernen" data-page-link><img src="/static/figma/mehr/{book}" width="22" height="22" alt="" /><span>Lernen</span></a>
          <a href="/dashboard" data-page-link><img src="/static/figma/mehr/{grad}" width="22" height="22" alt="" /><span>Campus</span></a>
          <a href="/fortschritt" data-page-link><img src="/static/figma/mehr/{trophy}" width="22" height="22" alt="" /><span>Bestenliste</span></a>
          <a href="/mehr" data-page-link class="active"><img src="/static/figma/mehr/{more}" width="22" height="22" alt="" /><span>Mehr</span></a>
        </nav>
        <div class="mp-home" aria-hidden="true"><i></i></div>'''

s_profil = r'''  "s09_1b-mein-profil": () => `
      <div class="mp-screen" data-node-id="136:10674">
        <div class="mp-main">
          <header class="mp-header">
            <a class="mp-back" href="/mehr" data-page-link aria-label="Zurück"><img src="/static/figma/mehr/pr-back.svg" width="18" height="18" alt="" /></a>
            <h2>Mein Profil</h2>
            <span class="mp-spacer" aria-hidden="true"></span>
          </header>
          <div class="mp-scroll">
            <div class="mp-hero">
              <div class="mp-avatar-wrap">
                <img class="mp-avatar" src="/static/figma/mehr/pr-avatar.png" width="96" height="96" alt="" />
                <span class="mp-edit"><img src="/static/figma/mehr/pr-pencil.svg" width="14" height="14" alt="" /></span>
              </div>
              <strong data-bind="profile-summary">Max Mustermann</strong>
              <p>Maschinen- und Anlagenführer (Metall)</p>
              <em>Kohorte 2024-A</em>
            </div>
            <div class="mp-stats">
              <article><img src="/static/figma/mehr/pr-shield.svg" width="16" height="16" alt="" /><b data-bind="level">7</b><span>Level</span></article>
              <article><img src="/static/figma/mehr/pr-sparkles.svg" width="16" height="16" alt="" /><b><span data-bind="xp">2450</span></b><span>XP</span></article>
              <article><img src="/static/figma/mehr/pr-fire.svg" width="16" height="16" alt="" /><b>12 Tage</b><span>Streak</span></article>
              <article><img src="/static/figma/mehr/pr-check.svg" width="16" height="16" alt="" /><b>156 beh.</b><span>Karten</span></article>
            </div>
            <section class="mp-section">
              <div class="mp-sec-head"><span>Meine Abzeichen (8)</span><a href="/fortschritt" data-page-link>Alle ansehen</a></div>
              <div class="mp-badges">
                <div><span class="on"><img src="/static/figma/mehr/pr-award.svg" width="20" height="20" alt="" /></span><em>Pionier</em></div>
                <div><span><img src="/static/figma/mehr/pr-zap.svg" width="20" height="20" alt="" /></span><em>Fleißig</em></div>
                <div><span><img src="/static/figma/mehr/pr-grad.svg" width="20" height="20" alt="" /></span><em>Schlau</em></div>
                <div><span><img src="/static/figma/mehr/pr-trophy.svg" width="20" height="20" alt="" /></span><em>Meister</em></div>
                <div><span><img src="/static/figma/mehr/pr-fire2.svg" width="20" height="20" alt="" /></span><em>Streaker</em></div>
              </div>
            </section>
            <article class="mp-card">
              <div class="mp-kv"><span>E-Mail</span><strong>max@firma.de</strong></div>
              <div class="mp-kv"><span>Ausbilder</span><strong>Hr. Schmidt</strong></div>
              <div class="mp-kv"><span>Träger</span><strong>BZE Düsseldorf</strong></div>
              <div class="mp-kv"><span>Beginn</span><strong>01.09.2024</strong></div>
              <hr />
              <div class="mp-prog"><div><span>Prüfungsreife</span><b data-bind="readiness">67%</b></div><div class="mp-bar"><i style="width:67%"></i></div></div>
            </article>
            <a class="mp-cta" href="/passwort" data-page-link>Profil bearbeiten</a>
          </div>
        </div>
''' + tabs.format(book="pr-book.svg", grad="pr-grad-tab.svg", trophy="pr-trophy-tab.svg", more="pr-more.svg") + '''
      </div>
    `,'''

s_darst = r'''  "s09_1c-darstellung": () => `
      <div class="mp-screen da-screen" data-node-id="136:10816">
        <div class="mp-main">
          <header class="mp-header">
            <a class="mp-back" href="/mehr" data-page-link aria-label="Zurück"><img src="/static/figma/mehr/da-back.svg" width="18" height="18" alt="" /></a>
            <h2>Darstellung</h2>
            <span class="mp-spacer" aria-hidden="true"></span>
          </header>
          <div class="mp-scroll">
            <section class="mp-section">
              <p class="mp-label">Design</p>
              <div class="da-themes">
                <button type="button" class="da-theme" data-action="toast" data-toast="Hell (Demo)">
                  <img src="/static/figma/mehr/da-sun.svg" width="20" height="20" alt="" />
                  <span>Hell</span>
                  <div class="da-mock light"><i></i><b></b><em></em></div>
                </button>
                <button type="button" class="da-theme on" data-action="toast" data-toast="Dunkel aktiv">
                  <img src="/static/figma/mehr/da-moon.svg" width="20" height="20" alt="" />
                  <span>Dunkel</span>
                  <div class="da-mock dark"><i></i><b></b><em></em></div>
                </button>
                <button type="button" class="da-theme" data-action="toast" data-toast="System (Demo)">
                  <img src="/static/figma/mehr/da-settings.svg" width="20" height="20" alt="" />
                  <span>System</span>
                  <div class="da-mock sys"><i></i><b></b><em></em></div>
                </button>
              </div>
            </section>
            <section class="mp-section">
              <div class="mp-sec-head"><span>Schriftgröße</span><em>Normal</em></div>
              <div class="da-font-card">
                <div class="da-slider"><span>Aa</span><div class="da-track"><i></i><img src="/static/figma/mehr/da-thumb.svg" width="16" height="16" alt="" /></div><strong>Aa</strong></div>
                <div class="da-preview"><p>So sieht die aktuelle Schriftgröße aus. Sie kann jederzeit angepasst werden.</p></div>
              </div>
            </section>
            <div class="da-toggles">
              <div class="da-row">
                <img src="/static/figma/mehr/da-sun2.svg" width="20" height="20" alt="" />
                <span>Hoher Kontrast</span>
                <button class="mp-toggle" type="button" aria-pressed="false" data-action="toast" data-toast="Kontrast (Demo)"></button>
              </div>
              <div class="da-row">
                <img src="/static/figma/mehr/da-film.svg" width="20" height="20" alt="" />
                <div><strong>Animationen reduzieren</strong><small>Deaktiviert Konfetti, Level-Up und andere Animationen</small></div>
                <button class="mp-toggle" type="button" aria-pressed="false" data-action="toast" data-toast="Animationen (Demo)"></button>
              </div>
            </div>
          </div>
        </div>
''' + tabs.format(book="da-book.svg", grad="da-grad.svg", trophy="da-trophy.svg", more="da-more.svg") + '''
      </div>
    `,'''

def bn_row(title, sub, on=True, time=None):
    tog = "on" if on else ""
    src = "bn-toggle-on.svg" if on else "bn-toggle-off.svg"
    time_html = f'<em class="bn-time">{time}</em>' if time else ""
    return f'''              <div class="bn-row">
                <div><strong>{title}</strong><small>{sub}</small></div>
                {time_html}
                <button class="mp-toggle {tog}" type="button" aria-pressed="{"true" if on else "false"}" data-action="toast" data-toast="{title} (Demo)"><img src="/static/figma/mehr/{src}" width="44" height="24" alt="" /></button>
              </div>'''

s_bn = r'''  "s09_1d-benachrichtigungen": () => `
      <div class="mp-screen bn-screen" data-node-id="136:10920">
        <div class="mp-main">
          <header class="mp-header">
            <a class="mp-back" href="/mehr" data-page-link aria-label="Zurück"><img src="/static/figma/mehr/bn-back.svg" width="18" height="18" alt="" /></a>
            <h2>Benachrichtigungen</h2>
            <span class="mp-spacer" aria-hidden="true"></span>
          </header>
          <div class="mp-scroll">
            <section class="mp-section">
              <p class="mp-label">Lernerinnerungen</p>
              <div class="bn-card">
''' + bn_row("Tägliche Erinnerung", "Erinnere mich an mein tägliches Lernen", True, "09:00") + "\n" + bn_row("Streak in Gefahr", "Warnung vor dem Verlust der täglichen Serie") + "\n" + bn_row("Tagesziel nicht erreicht", "Kurz vor Ende des Tages erinnern") + r'''
              </div>
            </section>
            <section class="mp-section">
              <p class="mp-label">Fortschritt</p>
              <div class="bn-card">
''' + bn_row("Level-Up", "Gratulation bei Erreichen eines neuen Levels") + "\n" + bn_row("Neue Badges", "Erfolgreiche Freischaltung von Abzeichen") + "\n" + bn_row("Prüfungsreife erreicht", "Benachrichtigung bei 100% Reife") + r'''
              </div>
            </section>
            <section class="mp-section">
              <p class="mp-label">Berichtsheft</p>
              <div class="bn-card">
''' + bn_row("Fehlende Einträge", "Erinnerung am Ende der Woche") + "\n" + bn_row("Freigabe erhalten", "Feedback vom Ausbilder liegt vor") + r'''
              </div>
            </section>
            <section class="mp-section">
              <p class="mp-label">System</p>
              <div class="bn-card">
''' + bn_row("Neue Inhalte verfügbar", "Neue Lernkarten und Module für deinen Kurs", False) + "\n" + bn_row("Wartungsarbeiten", "Geplante Ausfallzeiten des BZE Campus") + r'''
              </div>
            </section>
          </div>
        </div>
''' + tabs.format(book="bn-book.svg", grad="bn-grad.svg", trophy="bn-trophy.svg", more="bn-more.svg") + '''
      </div>
    `,'''

# insert screens before s09_2
anchor = '  "s09_2-was-sieht-der-ausbilder":'
if anchor not in js:
    raise SystemExit("missing s09_2 anchor")
js = js.replace(anchor, s_profil + "\n" + s_darst + "\n" + s_bn + "\n" + anchor, 1)

# ALLOWED_PAGES
for page in ["mehr/profil", "mehr/darstellung", "mehr/benachrichtigungen"]:
    if f'"{page}"' not in js:
        js = js.replace('"mehr",', f'"mehr", "{page}",', 1)

SCREENS.write_text(js, encoding="utf-8")
print("screens ok")

css_extra = r'''
/* --- 09.1 sibling phones: Profil / Darstellung / Benachrichtigungen --- */
.mp-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #0b0f19; color: #f8fafc;
}
.mp-main { flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.mp-header {
  display: flex; align-items: center; gap: 12px; height: 56px; padding: 0 16px;
  box-sizing: border-box; flex-shrink: 0;
}
.mp-back {
  display: grid; place-items: center; width: 36px; height: 36px; border-radius: 18px;
  background: #161d30; flex-shrink: 0;
}
.mp-back img { width: 18px; height: 18px; display: block; }
.mp-header h2 { margin: 0; flex: 1; text-align: center; font-size: 18px; font-weight: 700; color: #f8fafc; }
.mp-spacer { width: 36px; flex-shrink: 0; }
.mp-scroll {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 16px;
  padding: 0 16px 20px; box-sizing: border-box;
}
.mp-hero { display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 16px 0; }
.mp-avatar-wrap { position: relative; width: 96px; height: 96px; }
.mp-avatar { width: 96px; height: 96px; border-radius: 48px; object-fit: cover; display: block; }
.mp-edit {
  position: absolute; right: 0; bottom: 0; display: grid; place-items: center;
  width: 28px; height: 28px; border-radius: 14px; background: #3b82f6;
}
.mp-edit img { width: 14px; height: 14px; display: block; }
.mp-hero strong { color: #f8fafc; font-size: 20px; font-weight: 700; text-align: center; }
.mp-hero p { margin: 0; color: #94a3b8; font-size: 13px; text-align: center; }
.mp-hero em { font-style: normal; color: #64748b; font-size: 11px; font-weight: 600; text-transform: uppercase; }
.mp-stats { display: flex; gap: 8px; width: 100%; overflow: auto; }
.mp-stats article {
  display: flex; flex-direction: column; align-items: center; gap: 6px; width: 84px; padding: 10px;
  border-radius: 12px; background: #161d30; border: 1px solid #24314b; box-sizing: border-box; flex-shrink: 0;
}
.mp-stats img { width: 16px; height: 16px; display: block; }
.mp-stats b { color: #f8fafc; font-size: 15px; font-weight: 700; }
.mp-stats span { color: #94a3b8; font-size: 10px; }
.mp-section { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.mp-label { margin: 0; color: #94a3b8; font-size: 12px; font-weight: 700; text-transform: uppercase; }
.mp-sec-head { display: flex; justify-content: space-between; align-items: center; width: 100%; }
.mp-sec-head span { color: #94a3b8; font-size: 12px; font-weight: 700; text-transform: uppercase; }
.mp-sec-head a, .mp-sec-head em { color: #3b82f6; font-size: 12px; font-weight: 600; text-decoration: none; font-style: normal; }
.mp-badges {
  display: flex; gap: 10px; padding: 12px; border-radius: 16px; background: #161d30;
  border: 1px solid #24314b; box-sizing: border-box; width: 100%;
}
.mp-badges > div { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 0; }
.mp-badges span {
  display: grid; place-items: center; width: 40px; height: 40px; border-radius: 20px; background: #24314b;
}
.mp-badges span.on { background: rgba(245,158,11,0.12); }
.mp-badges img { width: 20px; height: 20px; display: block; }
.mp-badges em {
  font-style: normal; color: #94a3b8; font-size: 10px; text-align: center;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; width: 100%;
}
.mp-card {
  display: flex; flex-direction: column; gap: 12px; padding: 16px; border-radius: 16px;
  background: #161d30; border: 1px solid #24314b; box-sizing: border-box; width: 100%;
}
.mp-kv { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; }
.mp-kv span { color: #94a3b8; }
.mp-kv strong { color: #f8fafc; font-weight: 600; }
.mp-card hr { width: 100%; border: 0; border-top: 1px solid #24314b; margin: 0; }
.mp-prog { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.mp-prog > div:first-child { display: flex; justify-content: space-between; font-size: 13px; }
.mp-prog span { color: #94a3b8; }
.mp-prog b { color: #10b981; font-weight: 700; }
.mp-bar { height: 8px; border-radius: 4px; background: #24314b; overflow: hidden; }
.mp-bar i { display: block; height: 100%; background: #10b981; }
.mp-cta {
  display: flex; align-items: center; justify-content: center; width: 100%; height: 48px;
  border-radius: 12px; background: #3b82f6; color: #fff; font-size: 14px; font-weight: 700;
  text-decoration: none; box-sizing: border-box;
}
.mp-tabs {
  display: flex; align-items: center; justify-content: space-between;
  height: 72px; padding: 12px 16px 4px; background: #161d30; border-top: 1px solid #24314b;
  box-sizing: border-box; flex-shrink: 0;
}
.mp-tabs a {
  display: flex; flex-direction: column; align-items: center; gap: 4px; width: 64px;
  color: #64748b; font-size: 11px; font-weight: 500; text-decoration: none;
}
.mp-tabs a.active { color: #3b82f6; font-weight: 700; }
.mp-tabs a.active img {
  filter: invert(42%) sepia(93%) saturate(1800%) hue-rotate(202deg) brightness(98%) contrast(92%);
}
.mp-tabs img { width: 22px; height: 22px; display: block; }
.mp-home {
  display: flex; align-items: flex-end; justify-content: center; height: 24px; padding-bottom: 8px; flex-shrink: 0;
}
.mp-home i { display: block; width: 134px; height: 5px; border-radius: 100px; background: #94a3b8; }

.da-themes { display: flex; gap: 10px; width: 100%; }
.da-theme {
  flex: 1; min-width: 0; display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 10px; border-radius: 12px; background: #161d30; border: 1px solid #24314b;
  color: #94a3b8; cursor: pointer; box-sizing: border-box;
}
.da-theme.on { border: 2px solid #3b82f6; background: #1e2640; color: #3b82f6; }
.da-theme span { font-size: 12px; font-weight: 600; }
.da-theme.on span { font-weight: 700; }
.da-theme img { width: 20px; height: 20px; display: block; }
.da-mock {
  width: 72px; height: 40px; border-radius: 4px; padding: 4px; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 2px;
}
.da-mock.light { background: #f1f5f9; }
.da-mock.dark { background: #0b0f19; border: 1px solid #24314b; }
.da-mock.sys { background: #475569; }
.da-mock i, .da-mock b, .da-mock em { display: block; border-radius: 2px; }
.da-mock i { height: 4px; width: 32px; }
.da-mock b { height: 12px; width: 48px; }
.da-mock em { height: 4px; width: 20px; }
.da-mock.light i { background: #cbd5e1; }
.da-mock.light b { background: #e2e8f0; }
.da-mock.light em { background: #94a3b8; }
.da-mock.dark i { background: #24314b; }
.da-mock.dark b { background: #161d30; }
.da-mock.dark em { background: #94a3b8; }
.da-mock.sys i { background: #64748b; }
.da-mock.sys b { background: #334155; }
.da-mock.sys em { background: #94a3b8; }
.da-font-card {
  display: flex; flex-direction: column; gap: 16px; padding: 16px; border-radius: 16px;
  background: #161d30; border: 1px solid #24314b; box-sizing: border-box;
}
.da-slider { display: flex; align-items: center; gap: 12px; width: 100%; }
.da-slider > span { color: #94a3b8; font-size: 12px; font-weight: 500; }
.da-slider > strong { color: #f8fafc; font-size: 18px; font-weight: 700; }
.da-track {
  flex: 1; height: 4px; background: #24314b; display: flex; align-items: center; position: relative;
}
.da-track i { display: block; width: 120px; height: 100%; background: #3b82f6; }
.da-track img { width: 16px; height: 16px; display: block; margin-left: -8px; }
.da-preview { padding: 12px; border-radius: 8px; background: #0b0f19; }
.da-preview p { margin: 0; color: #f8fafc; font-size: 13px; line-height: 1.4; }
.da-toggles {
  display: flex; flex-direction: column; padding: 0 14px; border-radius: 16px;
  background: #161d30; border: 1px solid #24314b; box-sizing: border-box; width: 100%;
}
.da-row {
  display: flex; align-items: center; gap: 12px; padding: 14px 0;
  border-bottom: 1px solid #24314b;
}
.da-toggles .da-row:last-child { border-bottom: 0; }
.da-row > img { width: 20px; height: 20px; display: block; flex-shrink: 0; }
.da-row > span { flex: 1; color: #f8fafc; font-size: 14px; font-weight: 500; }
.da-row > div { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.da-row strong { color: #f8fafc; font-size: 14px; font-weight: 500; }
.da-row small { color: #94a3b8; font-size: 11px; }
.mp-toggle {
  width: 44px; height: 24px; border-radius: 12px; border: 0; background: #24314b;
  position: relative; flex-shrink: 0; cursor: pointer; padding: 0;
}
.mp-toggle::after {
  content: ""; position: absolute; top: 2px; left: 2px; width: 20px; height: 20px;
  border-radius: 10px; background: #fff;
}
.mp-toggle.on { background: #3b82f6; }
.mp-toggle.on::after { left: 22px; }
.mp-toggle img { width: 44px; height: 24px; display: block; }
.bn-card {
  display: flex; flex-direction: column; padding: 0 14px; border-radius: 16px;
  background: #161d30; border: 1px solid #24314b; box-sizing: border-box; width: 100%;
}
.bn-row {
  display: flex; align-items: center; gap: 12px; padding: 12px 0;
  border-bottom: 1px solid #24314b;
}
.bn-card .bn-row:last-child { border-bottom: 0; }
.bn-row > div { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.bn-row strong { color: #f8fafc; font-size: 14px; font-weight: 500; }
.bn-row small { color: #94a3b8; font-size: 11px; }
.bn-time {
  font-style: normal; padding: 4px 8px; border-radius: 6px; background: #24314b;
  color: #3b82f6; font-size: 13px; font-weight: 600; flex-shrink: 0;
}
.bn-row .mp-toggle { background: transparent; }
.bn-row .mp-toggle::after { display: none; }
'''

css = CSS.read_text(encoding="utf-8")
marker = "/* --- 09.1 sibling phones:"
if marker in css:
    css = css.split(marker)[0].rstrip() + "\n" + css_extra
else:
    css = css.rstrip() + "\n" + css_extra
CSS.write_text(css, encoding="utf-8")
print("css ok")
