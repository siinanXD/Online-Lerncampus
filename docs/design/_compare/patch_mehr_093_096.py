# -*- coding: utf-8 -*-
from pathlib import Path
import re

ROOT = Path(r"C:\dev\Repositories\Online-Lerncampus")
SCREENS = ROOT / "app/web/static/screens.js"
CSS = ROOT / "app/web/static/ui.css"

js = SCREENS.read_text(encoding="utf-8")

# chrome flags for full-bleed Figma phones
for path, old, new in [
    (
        "/mehr/coach",
        '"/mehr/coach": { layout: "app", screen: "s09_3-ki-coach-chat", title: "KI-Coach — Chat", tab: "profile", num: "09.3" }',
        '"/mehr/coach": { layout: "app", screen: "s09_3-ki-coach-chat", title: "KI-Coach — Chat", tab: "profile", num: "09.3", chrome: "mehr" }',
    ),
    (
        "/mehr/lernplan",
        '"/mehr/lernplan": { layout: "app", screen: "s09_4-ki-coach-lernplan", title: "KI-Coach — Lernplan", tab: "profile", num: "09.4" }',
        '"/mehr/lernplan": { layout: "app", screen: "s09_4-ki-coach-lernplan", title: "KI-Coach — Lernplan", tab: "profile", num: "09.4", chrome: "mehr" }',
    ),
    (
        "/mehr/export",
        '"/mehr/export": { layout: "app", screen: "s09_5-datenexport", title: "Datenexport", tab: "profile", num: "09.5" }',
        '"/mehr/export": { layout: "app", screen: "s09_5-datenexport", title: "Datenexport", tab: "profile", num: "09.5", chrome: "mehr" }',
    ),
    (
        "/mehr/loeschen",
        '"/mehr/loeschen": { layout: "app", screen: "s09_6-konto-loeschen", title: "Konto löschen", tab: "profile", num: "09.6" }',
        '"/mehr/loeschen": { layout: "app", screen: "s09_6-konto-loeschen", title: "Konto löschen", tab: "profile", num: "09.6", chrome: "mehr" }',
    ),
]:
    if old in js:
        js = js.replace(old, new)
    elif new not in js:
        raise SystemExit(f"route missing for {path}")

s093 = r'''  "s09_3-ki-coach-chat": () => `
      <div class="kc-screen" data-node-id="136:11173">
        <div class="kc-main">
          <header class="kc-header">
            <div class="kc-top">
              <div class="kc-left">
                <a class="kc-back" href="/mehr" data-page-link aria-label="Zurück">
                  <img src="/static/figma/mehr/kc-back.svg" width="24" height="24" alt="" />
                </a>
                <span class="kc-avatar"><img src="/static/figma/mehr/kc-bot.svg" width="20" height="20" alt="" /></span>
                <div class="kc-title"><strong>KI-Coach</strong><img src="/static/figma/mehr/kc-online.svg" width="8" height="8" alt="" /></div>
              </div>
              <button class="kc-more" type="button" aria-label="Mehr" data-action="toast" data-toast="Menü (Demo)">
                <img src="/static/figma/mehr/kc-more.svg" width="24" height="24" alt="" />
              </button>
            </div>
          </header>
          <div class="kc-chat">
            <div class="kc-msg ai">
              <div class="kc-bubble">Hallo Max! Wie kann ich dir helfen? Ich kann Fragen erklären, Formeln ableiten oder deinen Lernplan optimieren.</div>
              <time>14:23</time>
            </div>
            <div class="kc-msg me">
              <div class="kc-bubble">Ich verstehe die Formel für Kolbenkraft nicht. Kannst du das erklären?</div>
              <time>14:24</time>
            </div>
            <div class="kc-msg ai">
              <div class="kc-bubble rich">
                <p>Klar! Die Kolbenkraft berechnet sich so:</p>
                <div class="kc-formula">F = p × A</div>
                <ul class="kc-vars">
                  <li><i>•</i><span>F = Kraft in Newton [N]</span></li>
                  <li><i>•</i><span>p = Druck in Pascal oder bar</span></li>
                  <li><i>•</i><span>A = Kolbenfläche in m² oder cm²</span></li>
                </ul>
                <div class="kc-ex">
                  <strong>Beispiel</strong>
                  <p>Bei p = 6 bar und A = 20 cm²</p>
                  <em>F = 6 × 20 = 120 N</em>
                </div>
                <p>Möchtest du eine Übungsaufgabe dazu?</p>
              </div>
              <time>14:25</time>
            </div>
            <div class="kc-chips">
              <button type="button" data-action="toast" data-toast="Übung gestartet (Demo)">Ja, Übung 🔥</button>
              <button type="button" data-action="toast" data-toast="Andere Frage (Demo)">Andere Frage</button>
              <button type="button" data-action="toast" data-toast="Alles klar (Demo)">Danke, alles klar!</button>
            </div>
            <div data-bind="coach-live" hidden></div>
          </div>
          <div class="kc-input-wrap">
            <div class="kc-input-bar">
              <button class="kc-attach" type="button" aria-label="Anhang" data-action="toast" data-toast="Anhang (Demo)">
                <img src="/static/figma/mehr/kc-clip.svg" width="20" height="20" alt="" />
              </button>
              <div class="kc-field"><input type="text" placeholder="Nachricht eingeben..." aria-label="Nachricht" /></div>
              <button class="kc-send" type="button" data-action="toast" data-toast="Nachricht gesendet (Demo)" aria-label="Senden">
                <img src="/static/figma/mehr/kc-send.svg" width="20" height="20" alt="" />
              </button>
            </div>
            <div class="kc-home" aria-hidden="true"><i></i></div>
          </div>
        </div>
      </div>
    `,'''

s094 = r'''  "s09_4-ki-coach-lernplan": () => `
      <div class="lp-screen" data-node-id="136:11249">
        <header class="lp-header">
          <div class="lp-top">
            <div class="lp-left">
              <a class="lp-back" href="/mehr/coach" data-page-link aria-label="Zurück">
                <img src="/static/figma/mehr/lp-back.svg" width="24" height="24" alt="" />
              </a>
              <strong>Dein Lernplan</strong>
            </div>
            <a class="lp-bot" href="/mehr/coach" data-page-link aria-label="KI-Coach">
              <img src="/static/figma/mehr/lp-bot.svg" width="24" height="24" alt="" />
            </a>
          </div>
          <p>Erstellt von deinem KI-Coach basierend auf deinem Fortschritt</p>
        </header>
        <div class="lp-scroll">
          <article class="lp-goal">
            <div class="lp-goal-head">
              <div>
                <strong>Ziel: Zwischenprüfung bestehen</strong>
                <span>Termin: 15. März 2025 — In 14 Tagen</span>
              </div>
              <em>Note 3+</em>
            </div>
            <hr class="lp-rule" />
            <div class="lp-rings">
              <div class="lp-ring">
                <div class="lp-ring-vis">
                  <img class="bg" src="/static/figma/mehr/lp-ring-bg.svg" width="40" height="40" alt="" />
                  <img class="fg" src="/static/figma/mehr/lp-ring-67.svg" width="40" height="40" alt="" />
                  <b>67%</b>
                </div>
                <div><strong>Prüfungsreife</strong><span>Aktuell</span></div>
              </div>
              <div class="lp-ring">
                <div class="lp-ring-vis">
                  <img class="bg" src="/static/figma/mehr/lp-ring-bg.svg" width="40" height="40" alt="" />
                  <img class="fg" src="/static/figma/mehr/lp-ring-80.svg" width="40" height="40" alt="" />
                  <b class="ok">80%</b>
                </div>
                <div><strong>80%+</strong><span>Ziel</span></div>
              </div>
            </div>
          </article>
          <section class="lp-week">
            <h3>Diese Woche</h3>
            <div class="lp-week-card">
              <div class="lp-day">
                <span class="lp-check"></span>
                <div><strong>Pneumatik — Schaltpläne</strong><span>Mo • 30 Min</span></div>
              </div>
              <div class="lp-day done">
                <span class="lp-check on"><img src="/static/figma/mehr/lp-check.svg" width="16" height="16" alt="" /></span>
                <div><strong>Hydraulik — Druckberechnung</strong><span>Di • 25 Min</span></div>
              </div>
              <div class="lp-day done">
                <span class="lp-check on"><img src="/static/figma/mehr/lp-check.svg" width="16" height="16" alt="" /></span>
                <div><strong>Wiederholung: Fehler letzte Woche</strong><span>Mi • 20 Min</span></div>
              </div>
              <div class="lp-day">
                <span class="lp-check"></span>
                <div><strong>Steuerungstechnik — Grundlagen</strong><span>Do • 30 Min</span></div>
              </div>
              <div class="lp-day">
                <span class="lp-check"></span>
                <div><strong>Prüfungssimulation</strong><span>Fr • 60 Min</span></div>
              </div>
              <hr class="lp-rule soft" />
              <div class="lp-prog">
                <div class="lp-prog-lab"><span>Fortschritt</span><strong>2/5 diese Woche</strong></div>
                <div class="lp-prog-track"><i style="width:40%"></i></div>
              </div>
            </div>
          </section>
          <article class="lp-next">
            <div><strong>Nächste Woche</strong><span>Fokus: Steuerungstechnik + Arbeitssicherheit</span></div>
            <img src="/static/figma/mehr/lp-chev.svg" width="20" height="20" alt="" />
          </article>
          <div class="lp-actions">
            <button type="button" class="lp-adjust" data-action="toast" data-toast="Plan anpassen (Demo)">Plan anpassen</button>
            <a class="lp-ask" href="/mehr/coach" data-page-link>
              <img src="/static/figma/mehr/lp-bot-btn.svg" width="16" height="16" alt="" />
              <span>KI fragen</span>
            </a>
          </div>
          <div data-bind="coach-live" hidden></div>
          <div data-bind="journey-live" hidden></div>
        </div>
        <div class="lp-home" aria-hidden="true"><i></i></div>
      </div>
    `,'''

s095 = r'''  "s09_5-datenexport": () => `
      <div class="de-screen" data-node-id="136:11353">
        <div class="de-main">
          <header class="de-header">
            <a class="de-back" href="/mehr" data-page-link>
              <img src="/static/figma/mehr/de-back.svg" width="16" height="16" alt="" />
              <span>Zurück</span>
            </a>
            <h2>Datenexport</h2>
            <span class="de-spacer" aria-hidden="true"></span>
          </header>
          <div class="de-body">
            <div class="de-hero">
              <span class="de-hero-ico"><img src="/static/figma/mehr/de-cloud.svg" width="32" height="32" alt="" /></span>
              <p>Du kannst all deine Daten herunterladen. Der Export enthält deine Lernhistorie, Berichtshefte und persönlichen Einstellungen.</p>
            </div>
            <div class="de-opts">
              <label class="de-opt on"><span class="de-box"><img src="/static/figma/mehr/de-check.svg" width="12" height="12" alt="" /></span><div><strong>Lernfortschritt &amp; XP-Historie</strong><span>Alle Antworten, Level, Streaks</span></div><input type="checkbox" checked hidden /></label>
              <label class="de-opt on"><span class="de-box"><img src="/static/figma/mehr/de-check.svg" width="12" height="12" alt="" /></span><div><strong>Berichtsheft</strong><span>Alle Einträge als PDF + Rohdaten</span></div><input type="checkbox" checked hidden /></label>
              <label class="de-opt"><span class="de-box"></span><div><strong>Persönliche Daten</strong><span>Profil, E-Mail, Einstellungen</span></div><input type="checkbox" hidden /></label>
              <label class="de-opt"><span class="de-box"></span><div><strong>Statistiken</strong><span>Detaillierte Auswertungen</span></div><input type="checkbox" hidden /></label>
            </div>
            <div class="de-fmt">
              <p>Exportformat</p>
              <div class="de-tabs" role="tablist">
                <button type="button" data-fmt="json">JSON</button>
                <button type="button" data-fmt="csv">CSV</button>
                <button type="button" class="on" data-fmt="pdf">PDF</button>
              </div>
            </div>
            <div class="de-info">
              <img src="/static/figma/mehr/de-info.svg" width="18" height="18" alt="" />
              <p>Der Export kann einige Minuten dauern. Du erhältst eine E-Mail wenn er bereit ist.</p>
            </div>
            <div class="de-cta">
              <button class="de-start" type="button" data-action="export-data">Export starten</button>
              <p>Letzter Export: 15.06.2026</p>
            </div>
            <pre class="export-pre" data-bind="export-pre" hidden></pre>
          </div>
        </div>
        <nav class="de-tabs-nav" aria-label="Hauptnavigation">
          <a href="/dashboard" data-page-link><img src="/static/figma/mehr/de-house.svg" width="22" height="22" alt="" /><span>Start</span></a>
          <a href="/lernen" data-page-link><img src="/static/figma/mehr/de-book.svg" width="22" height="22" alt="" /><span>Lernen</span></a>
          <a href="/fortschritt" data-page-link><img src="/static/figma/mehr/de-trend.svg" width="22" height="22" alt="" /><span>Fortschritt</span></a>
          <a href="/berichtsheft" data-page-link><img src="/static/figma/mehr/de-file.svg" width="22" height="22" alt="" /><span>Bericht</span></a>
          <a href="/mehr" data-page-link class="active"><img src="/static/figma/mehr/de-menu.svg" width="22" height="22" alt="" /><span>Mehr</span></a>
        </nav>
      </div>
    `,'''

s096 = r'''  "s09_6-konto-loeschen": () => `
      <div class="dl-screen" data-node-id="136:11453">
        <div class="dl-main">
          <header class="dl-header">
            <a class="dl-back" href="/mehr" data-page-link aria-label="Zurück">
              <img src="/static/figma/mehr/dl-back.svg" width="20" height="20" alt="" />
            </a>
            <h2>Konto löschen</h2>
          </header>
          <div class="dl-body">
            <article class="dl-warn">
              <div class="dl-warn-top">
                <img src="/static/figma/mehr/dl-alert.svg" width="32" height="32" alt="" />
                <strong>Achtung: Diese Aktion ist unwiderruflich!</strong>
              </div>
              <p>Wenn du dein Konto löschst, werden folgende Daten dauerhaft entfernt:</p>
            </article>
            <ul class="dl-loss">
              <li><img src="/static/figma/mehr/dl-x.svg" width="16" height="16" alt="" /><span>Lernfortschritt &amp; XP (Level 6, 4.230 XP)</span></li>
              <li><img src="/static/figma/mehr/dl-x.svg" width="16" height="16" alt="" /><span>Alle Berichtshefte (23 Einträge)</span></li>
              <li><img src="/static/figma/mehr/dl-x.svg" width="16" height="16" alt="" /><span>Badges &amp; Achievements (8 Abzeichen)</span></li>
              <li><img src="/static/figma/mehr/dl-x.svg" width="16" height="16" alt="" /><span>Streak-Historie (max: 34 Tage)</span></li>
              <li><img src="/static/figma/mehr/dl-x.svg" width="16" height="16" alt="" /><span>Persönliche Einstellungen</span></li>
            </ul>
            <label class="dl-confirm">
              <input type="checkbox" id="dl-ack" />
              <span class="dl-box"></span>
              <span>Ich verstehe, dass alle Daten unwiderruflich gelöscht werden</span>
            </label>
            <label class="dl-type">
              <span>Bitte gib LÖSCHEN ein zur Bestätigung</span>
              <input type="text" id="dl-phrase" placeholder="Bestätigungstext..." aria-label="Bestätigung" autocomplete="off" />
            </label>
            <div class="dl-actions">
              <button class="dl-delete" type="button" data-action="delete-account" disabled>Konto endgültig löschen</button>
              <a class="dl-cancel" href="/mehr" data-page-link>Abbrechen</a>
            </div>
            <pre class="export-pre" data-bind="export-pre" hidden></pre>
          </div>
        </div>
        <nav class="dl-tabs" aria-label="Navigation">
          <a href="/lernen" data-page-link><img src="/static/figma/mehr/dl-book.svg" width="22" height="22" alt="" /><span>Lernen</span></a>
          <a href="/berichtsheft" data-page-link><img src="/static/figma/mehr/dl-clip.svg" width="22" height="22" alt="" /><span>Bericht</span></a>
          <a href="/mehr" data-page-link class="active"><img src="/static/figma/mehr/dl-user.svg" width="22" height="22" alt="" /><span>Mehr</span></a>
        </nav>
        <div class="dl-home" aria-hidden="true"><i></i></div>
      </div>
    `,'''

for key, block in [
    ("s09_3-ki-coach-chat", s093),
    ("s09_4-ki-coach-lernplan", s094),
    ("s09_5-datenexport", s095),
    ("s09_6-konto-loeschen", s096),
]:
    pat = re.compile(rf'  "{key}": \(\) => `[\s\S]*?`,\n(?=  ")')
    if not pat.search(js):
        raise SystemExit(f"missing {key}")
    js = pat.sub(block + "\n", js, count=1)

SCREENS.write_text(js, encoding="utf-8")
print("screens ok")

css_extra = r'''
/* --- 09.3 KI-Coach Chat --- */
.app-frame[data-chrome="mehr"]:has(.kc-screen),
.app-frame[data-chrome="mehr"]:has(.lp-screen) {
  background: #fafaf9;
}
.app-frame[data-chrome="mehr"]:has(.kc-screen) .app-content,
.app-frame[data-chrome="mehr"]:has(.lp-screen) .app-content {
  background: #fafaf9;
}
.app-frame[data-chrome="mehr"]:has(.kc-screen) .app-status,
.app-frame[data-chrome="mehr"]:has(.lp-screen) .app-status,
.app-frame[data-chrome="mehr"]:has(.de-screen) .app-status,
.app-frame[data-chrome="mehr"]:has(.dl-screen) .app-status {
  color: #1c1917;
}
.app-frame[data-chrome="mehr"]:has(.kc-screen) .login-status-icon,
.app-frame[data-chrome="mehr"]:has(.lp-screen) .login-status-icon,
.app-frame[data-chrome="mehr"]:has(.de-screen) .login-status-icon,
.app-frame[data-chrome="mehr"]:has(.dl-screen) .login-status-icon {
  filter: none;
}
.app-frame[data-chrome="mehr"]:has(.de-screen) { background: #f8fafc; }
.app-frame[data-chrome="mehr"]:has(.de-screen) .app-content { background: #f8fafc; }
.app-frame[data-chrome="mehr"]:has(.dl-screen) { background: #f9fafc; }
.app-frame[data-chrome="mehr"]:has(.dl-screen) .app-content { background: #f9fafc; }

.kc-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #fafaf9; color: #1c1917;
}
.kc-main { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.kc-header {
  background: #fff; border-bottom: 1px solid #e7e5e4;
  padding: 8px 20px 16px; box-sizing: border-box; flex-shrink: 0;
}
.kc-top { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.kc-left { display: flex; align-items: center; gap: 12px; min-width: 0; }
.kc-back, .kc-more {
  display: grid; place-items: center; width: 24px; height: 24px;
  padding: 0; border: 0; background: transparent; cursor: pointer; flex-shrink: 0;
}
.kc-back img, .kc-more img { width: 24px; height: 24px; display: block; }
.kc-avatar {
  display: grid; place-items: center; width: 32px; height: 32px; border-radius: 16px;
  background: #0d9488; flex-shrink: 0;
}
.kc-avatar img { width: 20px; height: 20px; display: block; }
.kc-title { display: flex; align-items: center; gap: 6px; }
.kc-title strong { font-size: 18px; font-weight: 700; color: #1c1917; }
.kc-title img { width: 8px; height: 8px; display: block; }
.kc-chat {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 16px;
  padding: 16px; background: #fafaf9; box-sizing: border-box;
}
.kc-msg { display: flex; flex-direction: column; gap: 4px; width: 100%; }
.kc-msg.ai { align-items: flex-start; }
.kc-msg.me { align-items: flex-end; }
.kc-bubble {
  padding: 12px; border-radius: 12px 12px 12px 4px; box-sizing: border-box;
  font-size: 14px; line-height: 1.4; color: #1c1917; width: 300px;
  background: #f0fdfa; border: 1px solid #0d9488;
}
.kc-msg.me .kc-bubble {
  width: 280px; background: #2563eb; border: 0; color: #fff;
  border-radius: 12px 12px 4px 12px;
}
.kc-bubble.rich { width: 310px; display: flex; flex-direction: column; gap: 12px; }
.kc-bubble.rich > p { margin: 0; }
.kc-msg time { color: #a8a29e; font-size: 11px; }
.kc-formula {
  display: flex; align-items: center; justify-content: center; width: 100%;
  padding: 10px; border-radius: 8px; background: #fff; border: 1px solid #e7e5e4;
  color: #0f766e; font-size: 20px; font-weight: 700; box-sizing: border-box;
}
.kc-vars { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 4px; width: 100%; }
.kc-vars li { display: flex; gap: 6px; align-items: flex-start; font-size: 12px; color: #1c1917; }
.kc-vars i { font-style: normal; color: #0f766e; flex-shrink: 0; }
.kc-ex {
  display: flex; flex-direction: column; gap: 4px; width: 100%; padding: 10px;
  border-radius: 8px; background: #fef3c7; border: 1px solid #d97706; box-sizing: border-box;
}
.kc-ex strong { color: #d97706; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.kc-ex p { margin: 0; color: #1c1917; font-size: 12px; line-height: 1.4; }
.kc-ex em { font-style: normal; color: #1c1917; font-size: 13px; font-weight: 700; }
.kc-chips { display: flex; flex-wrap: wrap; gap: 8px; width: 100%; }
.kc-chips button {
  padding: 8px 12px; border-radius: 100px; border: 1px solid #e7e5e4; background: #fff;
  color: #0f766e; font-size: 13px; font-weight: 600; cursor: pointer;
}
.kc-input-wrap { flex-shrink: 0; background: #fff; }
.kc-input-bar {
  display: flex; align-items: center; gap: 12px; padding: 12px;
  border-top: 1px solid #e7e5e4; box-sizing: border-box;
}
.kc-attach, .kc-send {
  display: grid; place-items: center; width: 40px; height: 40px; border-radius: 20px;
  border: 0; cursor: pointer; flex-shrink: 0; padding: 0;
}
.kc-attach { background: #f5f5f4; }
.kc-send { background: #0d9488; }
.kc-attach img, .kc-send img { width: 20px; height: 20px; display: block; }
.kc-field {
  flex: 1; min-width: 0; height: 44px; display: flex; align-items: center;
  padding: 0 16px; border-radius: 22px; background: #f5f5f4; border: 1px solid #e7e5e4;
  box-sizing: border-box;
}
.kc-field input {
  width: 100%; border: 0; background: transparent; outline: none;
  font-size: 14px; color: #1c1917;
}
.kc-field input::placeholder { color: #a8a29e; }
.kc-home {
  display: flex; align-items: center; justify-content: center; padding: 12px 0 8px;
}
.kc-home i { display: block; width: 134px; height: 5px; border-radius: 100px; background: #1c1917; }

/* --- 09.4 Lernplan --- */
.lp-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #fafaf9; color: #1c1917;
}
.lp-header {
  background: #fff; border-bottom: 1px solid #e7e5e4;
  padding: 8px 20px 16px; display: flex; flex-direction: column; gap: 12px;
  box-sizing: border-box; flex-shrink: 0;
}
.lp-top { display: flex; align-items: center; justify-content: space-between; width: 100%; }
.lp-left { display: flex; align-items: center; gap: 12px; }
.lp-back, .lp-bot {
  display: grid; place-items: center; width: 24px; height: 24px; flex-shrink: 0;
}
.lp-back img, .lp-bot img { width: 24px; height: 24px; display: block; }
.lp-left strong { font-size: 18px; font-weight: 700; color: #1c1917; }
.lp-header > p { margin: 0; color: #78716c; font-size: 13px; line-height: 1.4; }
.lp-scroll {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 20px;
  padding: 16px; box-sizing: border-box;
}
.lp-goal {
  display: flex; flex-direction: column; gap: 16px; padding: 16px;
  border-radius: 16px; background: #fff; border: 1px solid #2563eb; border-top: 4px solid #2563eb;
  box-sizing: border-box;
}
.lp-goal-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; width: 100%; }
.lp-goal-head > div { display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.lp-goal-head strong { color: #1c1917; font-size: 15px; font-weight: 700; }
.lp-goal-head span { color: #78716c; font-size: 12px; }
.lp-goal-head em {
  font-style: normal; padding: 4px 8px; border-radius: 6px; background: #eff6ff;
  color: #2563eb; font-size: 12px; font-weight: 700; flex-shrink: 0;
}
.lp-rule { width: 100%; height: 0; border: 0; border-top: 1px solid #e7e5e4; margin: 0; }
.lp-rule.soft { border-top-color: #e7e5e4; }
.lp-rings { display: flex; gap: 16px; align-items: center; width: 100%; }
.lp-ring { display: flex; align-items: center; gap: 8px; }
.lp-ring-vis { position: relative; width: 40px; height: 40px; flex-shrink: 0; }
.lp-ring-vis img { position: absolute; inset: 0; width: 40px; height: 40px; display: block; }
.lp-ring-vis .fg { inset: 0; }
.lp-ring-vis b {
  position: absolute; inset: 0; display: grid; place-items: center;
  color: #2563eb; font-size: 10px; font-weight: 700;
}
.lp-ring-vis b.ok { color: #16a34a; }
.lp-ring > div:last-child { display: flex; flex-direction: column; gap: 2px; }
.lp-ring strong { color: #1c1917; font-size: 12px; font-weight: 700; }
.lp-ring span { color: #78716c; font-size: 10px; }
.lp-week { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.lp-week h3 { margin: 0; color: #1c1917; font-size: 15px; font-weight: 700; }
.lp-week-card {
  display: flex; flex-direction: column; gap: 12px; padding: 12px;
  border-radius: 16px; background: #fff; border: 1px solid #e7e5e4; box-sizing: border-box;
}
.lp-day { display: flex; align-items: center; gap: 12px; width: 100%; }
.lp-check {
  width: 24px; height: 24px; border-radius: 6px; border: 2px solid #e7e5e4;
  background: #fff; box-sizing: border-box; flex-shrink: 0;
}
.lp-check.on {
  display: grid; place-items: center; border-color: #16a34a; background: #16a34a;
}
.lp-check.on img { width: 16px; height: 16px; display: block; }
.lp-day > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.lp-day strong {
  color: #1c1917; font-size: 13px; font-weight: 700;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lp-day span { color: #78716c; font-size: 11px; }
.lp-day.done strong { color: #78716c; text-decoration: line-through; }
.lp-day.done span { color: #78716c; }
.lp-prog { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.lp-prog-lab { display: flex; justify-content: space-between; font-size: 12px; }
.lp-prog-lab span { color: #78716c; }
.lp-prog-lab strong { color: #2563eb; font-weight: 700; }
.lp-prog-track {
  width: 100%; height: 8px; border-radius: 4px; background: #f5f5f4; overflow: hidden;
}
.lp-prog-track i { display: block; height: 100%; background: #2563eb; border-radius: 4px; }
.lp-next {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 16px; border-radius: 16px; background: #fff; border: 1px solid #e7e5e4;
  box-sizing: border-box;
}
.lp-next > div { display: flex; flex-direction: column; gap: 4px; min-width: 0; flex: 1; }
.lp-next strong { color: #1c1917; font-size: 14px; font-weight: 700; }
.lp-next span {
  color: #78716c; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lp-next img { width: 20px; height: 20px; display: block; flex-shrink: 0; }
.lp-actions { display: flex; gap: 12px; width: 100%; }
.lp-adjust, .lp-ask {
  flex: 1; min-width: 0; display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 12px 16px; border-radius: 100px; font-size: 14px; font-weight: 600;
  text-decoration: none; cursor: pointer; box-sizing: border-box;
}
.lp-adjust { border: 1px solid #78716c; background: transparent; color: #1c1917; }
.lp-ask { border: 0; background: #0d9488; color: #fff; }
.lp-ask img { width: 16px; height: 16px; display: block; }
.lp-home {
  display: flex; align-items: center; justify-content: center; padding: 12px 0 8px; flex-shrink: 0;
}
.lp-home i { display: block; width: 134px; height: 5px; border-radius: 100px; background: #1c1917; }

/* --- 09.5 Datenexport --- */
.de-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #f8fafc; color: #1e293b;
}
.de-main { flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.de-header {
  display: flex; align-items: center; gap: 16px; height: 48px; padding: 0 20px;
  background: #fff; border-bottom: 1px solid #e2e8f0; box-sizing: border-box; flex-shrink: 0;
}
.de-back {
  display: flex; align-items: center; gap: 4px; color: #2563eb; font-size: 14px;
  font-weight: 500; text-decoration: none; flex-shrink: 0;
}
.de-back img { width: 16px; height: 16px; display: block; }
.de-header h2 {
  margin: 0; width: 194px; text-align: center; font-size: 16px; font-weight: 700; color: #1e293b;
}
.de-spacer { width: 48px; flex-shrink: 0; }
.de-body {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 20px;
  padding: 20px; box-sizing: border-box;
}
.de-hero { display: flex; flex-direction: column; align-items: center; gap: 12px; width: 100%; }
.de-hero-ico {
  display: grid; place-items: center; width: 64px; height: 64px; border-radius: 32px; background: #eff6ff;
}
.de-hero-ico img { width: 32px; height: 32px; display: block; }
.de-hero p {
  margin: 0; text-align: center; color: #64748b; font-size: 13px; line-height: 1.4; width: 100%;
}
.de-opts { display: flex; flex-direction: column; gap: 10px; width: 100%; }
.de-opt {
  display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 12px;
  background: #fff; border: 1px solid #e2e8f0; box-sizing: border-box; cursor: pointer;
}
.de-opt.on { border-color: #2563eb; }
.de-box {
  width: 20px; height: 20px; border-radius: 4px; border: 1px solid #e2e8f0;
  background: transparent; box-sizing: border-box; flex-shrink: 0;
  display: grid; place-items: center;
}
.de-opt.on .de-box { background: #2563eb; border-color: #2563eb; }
.de-box img { width: 12px; height: 12px; display: block; }
.de-opt > div { display: flex; flex-direction: column; gap: 2px; min-width: 0; flex: 1; }
.de-opt strong { color: #1e293b; font-size: 13px; font-weight: 600; }
.de-opt span { color: #64748b; font-size: 11px; }
.de-fmt { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.de-fmt > p { margin: 0; color: #64748b; font-size: 13px; font-weight: 600; }
.de-tabs {
  display: flex; gap: 2px; padding: 3px; border-radius: 100px; background: #f1f5f9; width: 100%;
  box-sizing: border-box;
}
.de-tabs button {
  flex: 1; min-width: 0; border: 0; background: transparent; border-radius: 100px;
  padding: 8px 0; color: #64748b; font-size: 12px; font-weight: 500; cursor: pointer;
}
.de-tabs button.on {
  background: #fff; color: #2563eb; font-weight: 600;
  box-shadow: 0 4px 6px rgba(15,23,42,0.04);
}
.de-info {
  display: flex; gap: 10px; align-items: flex-start; padding: 12px;
  border-radius: 12px; background: #eff6ff; box-sizing: border-box;
}
.de-info img { width: 18px; height: 18px; display: block; flex-shrink: 0; }
.de-info p { margin: 0; color: #1d4ed8; font-size: 12px; line-height: 1.4; flex: 1; }
.de-cta { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.de-start {
  width: 100%; padding: 12px 16px; border: 0; border-radius: 12px; background: #2563eb;
  color: #fff; font-size: 15px; font-weight: 600; cursor: pointer;
}
.de-cta > p { margin: 0; text-align: center; color: #64748b; font-size: 11px; }
.de-tabs-nav {
  display: flex; align-items: center; justify-content: space-between;
  height: 72px; padding: 0 0 8px; background: #fff; border-top: 1px solid #e2e8f0;
  box-sizing: border-box; flex-shrink: 0;
}
.de-tabs-nav a {
  display: flex; flex-direction: column; align-items: center; gap: 4px; width: 70px;
  color: #64748b; font-size: 11px; font-weight: 500; text-decoration: none;
}
.de-tabs-nav a.active { color: #2563eb; font-weight: 600; }
.de-tabs-nav a.active img {
  filter: invert(32%) sepia(98%) saturate(1800%) hue-rotate(204deg) brightness(95%) contrast(96%);
}
.de-tabs-nav img { width: 22px; height: 22px; display: block; }

/* --- 09.6 Konto löschen --- */
.dl-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #f9fafc; color: #1f2937;
}
.dl-main { flex: 1; min-height: 0; display: flex; flex-direction: column; overflow: hidden; }
.dl-header {
  display: flex; align-items: center; gap: 16px; height: 56px; padding: 0 20px;
  background: #fff; border: 1px solid #e5e7eb; border-left: 0; border-right: 0;
  box-sizing: border-box; flex-shrink: 0;
}
.dl-back { display: grid; place-items: center; width: 20px; height: 20px; flex-shrink: 0; }
.dl-back img { width: 20px; height: 20px; display: block; }
.dl-header h2 { margin: 0; flex: 1; font-size: 16px; font-weight: 700; color: #1f2937; }
.dl-body {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 20px;
  padding: 20px; box-sizing: border-box;
}
.dl-warn {
  display: flex; flex-direction: column; gap: 12px; padding: 16px;
  border-radius: 16px; background: #fef2f2; border: 1px solid #ef4444; box-sizing: border-box;
}
.dl-warn-top { display: flex; align-items: center; gap: 12px; width: 100%; }
.dl-warn-top img { width: 32px; height: 32px; display: block; flex-shrink: 0; }
.dl-warn-top strong { flex: 1; color: #ef4444; font-size: 16px; font-weight: 800; }
.dl-warn > p { margin: 0; color: #4b5563; font-size: 13px; font-weight: 500; }
.dl-loss {
  margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 12px; width: 100%;
}
.dl-loss li { display: flex; align-items: center; gap: 10px; }
.dl-loss img { width: 16px; height: 16px; display: block; flex-shrink: 0; }
.dl-loss span { color: #4b5563; font-size: 13px; font-weight: 500; }
.dl-confirm {
  display: flex; align-items: flex-start; gap: 12px; padding-top: 8px; width: 100%;
  cursor: pointer; position: relative;
}
.dl-confirm input { position: absolute; opacity: 0; pointer-events: none; }
.dl-box {
  width: 20px; height: 20px; border-radius: 4px; border: 1px solid #e5e7eb;
  background: #fff; box-sizing: border-box; flex-shrink: 0; margin-top: 1px;
}
.dl-confirm:has(input:checked) .dl-box {
  background: #2563eb; border-color: #2563eb;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 12'%3E%3Cpath d='M2.5 6.2 4.8 8.5 9.5 3.5' fill='none' stroke='%23fff' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat; background-position: center; background-size: 12px 12px;
}
.dl-confirm > span:last-child { color: #1f2937; font-size: 13px; font-weight: 500; flex: 1; }
.dl-type { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.dl-type > span { color: #4b5563; font-size: 13px; font-weight: 600; }
.dl-type input {
  width: 100%; height: 44px; padding: 0 12px; border-radius: 8px; border: 1px solid #e5e7eb;
  background: #fff; font-size: 14px; color: #1f2937; box-sizing: border-box; outline: none;
}
.dl-type input::placeholder { color: #9ca3af; }
.dl-actions { display: flex; flex-direction: column; gap: 10px; width: 100%; }
.dl-delete {
  width: 100%; height: 48px; border: 0; border-radius: 100px; background: #ef4444;
  color: #fff; font-size: 15px; font-weight: 700; cursor: pointer; opacity: 0.4;
}
.dl-delete:not(:disabled) { opacity: 1; cursor: pointer; }
.dl-delete:disabled { cursor: not-allowed; }
.dl-cancel {
  display: flex; align-items: center; justify-content: center; width: 100%; height: 48px;
  border-radius: 100px; border: 1px solid #e5e7eb; color: #4b5563; font-size: 15px;
  font-weight: 600; text-decoration: none; box-sizing: border-box;
}
.dl-tabs {
  display: flex; align-items: center; justify-content: space-between;
  height: 64px; padding: 0 16px; background: #fff; border-top: 1px solid #e5e7eb;
  box-sizing: border-box; flex-shrink: 0;
}
.dl-tabs a {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  width: 72px; color: #9ca3af; font-size: 11px; font-weight: 500; text-decoration: none;
}
.dl-tabs a.active { color: #1e3a8a; font-weight: 600; }
.dl-tabs a.active img {
  filter: invert(14%) sepia(45%) saturate(2500%) hue-rotate(212deg) brightness(90%) contrast(105%);
}
.dl-tabs img { width: 22px; height: 22px; display: block; }
.dl-home {
  display: flex; align-items: center; justify-content: center; height: 34px; flex-shrink: 0;
}
.dl-home i { display: block; width: 134px; height: 5px; border-radius: 100px; background: #1f2937; }
'''

css = CSS.read_text(encoding="utf-8")
marker = "/* --- 09.3 KI-Coach Chat --- */"
if marker in css:
    # keep 09.2/09.7, replace from 09.3 onward if re-run
    head = css.split(marker)[0].rstrip()
    # also strip trailing leftover if any after 09.7 block ended previously without 09.3
    css = head + "\n" + css_extra
else:
    css = css.rstrip() + "\n" + css_extra
CSS.write_text(css, encoding="utf-8")
print("css ok")
