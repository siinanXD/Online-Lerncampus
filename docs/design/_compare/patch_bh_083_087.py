# -*- coding: utf-8 -*-
"""Pixel rebuild Bericht 08.3–08.7 from Figma 136:9998…10462."""
from pathlib import Path
import re

ROOT = Path(r"C:\dev\Repositories\Online-Lerncampus")
SCREENS = ROOT / "app" / "web" / "static" / "screens.js"
CSS = ROOT / "app" / "web" / "static" / "ui.css"

# --- route chrome ---
js = SCREENS.read_text(encoding="utf-8")
replacements = [
    (
        '"/berichtsheft/ki": { layout: "app", screen: "s08_3-berichtsheft-ki-assistent", title: "Berichtsheft — KI-Assistent", tab: "reports", num: "08.3" }',
        '"/berichtsheft/ki": { layout: "app", screen: "s08_3-berichtsheft-ki-assistent", title: "Berichtsheft — KI-Assistent", tab: "reports", num: "08.3", chrome: "bh" }',
    ),
    (
        '"/berichtsheft/unterschrift": { layout: "app", screen: "s08_4-berichtsheft-unterschrift", title: "Berichtsheft — Unterschrift", tab: "reports", num: "08.4" }',
        '"/berichtsheft/unterschrift": { layout: "app", screen: "s08_4-berichtsheft-unterschrift", title: "Berichtsheft — Unterschrift", tab: "reports", num: "08.4", chrome: "bh" }',
    ),
    (
        '"/berichtsheft/kalender": { layout: "app", screen: "s08_5-berichtsheft-kalenderansicht", title: "Berichtsheft — Kalenderansicht", tab: "reports", num: "08.5" }',
        '"/berichtsheft/kalender": { layout: "app", screen: "s08_5-berichtsheft-kalenderansicht", title: "Berichtsheft — Kalenderansicht", tab: "reports", num: "08.5", chrome: "bh" }',
    ),
    (
        '"/berichtsheft/export": { layout: "app", screen: "s08_6-pdf-export", title: "PDF-Export", tab: "reports", num: "08.6" }',
        '"/berichtsheft/export": { layout: "app", screen: "s08_6-pdf-export", title: "PDF-Export", tab: "reports", num: "08.6", chrome: "bh" }',
    ),
    (
        '"/berichtsheft/leer": { layout: "app", screen: "s08_7-berichtsheft-leerzustand", title: "Berichtsheft — Leerzustand", tab: "reports", num: "08.7" }',
        '"/berichtsheft/leer": { layout: "app", screen: "s08_7-berichtsheft-leerzustand", title: "Berichtsheft — Leerzustand", tab: "reports", num: "08.7", chrome: "bh" }',
    ),
]
for old, new in replacements:
    if old not in js:
        raise SystemExit(f"route missing: {old[:80]}")
    js = js.replace(old, new)

s083 = r'''  "s08_3-berichtsheft-ki-assistent": () => `
      <div class="bh-ki-screen" data-node-id="136:9998">
        <div class="bh-ki-body">
          <header class="bh-ki-header">
            <a class="bh-ki-back" href="/berichtsheft/neu" data-page-link aria-label="Zurück">
              <img src="/static/figma/bh/bh-ki-back.svg" width="16" height="16" alt="" />
            </a>
            <div class="bh-ki-titles">
              <h2>Eintrag bearbeiten</h2>
              <p>KW 12 — Fertigung</p>
            </div>
          </header>
          <div class="bh-ki-days">
            <article class="bh-ki-day active">
              <div class="bh-ki-day-head">
                <div class="bh-ki-day-label"><i class="ok"></i><strong>Montag</strong></div>
                <span>25/250</span>
              </div>
              <div class="bh-ki-textarea active">
                <span>drehmaschine eingerichtet</span><i class="caret" aria-hidden="true"></i>
              </div>
            </article>
            <article class="bh-ki-day">
              <div class="bh-ki-day-head">
                <div class="bh-ki-day-label"><i class="ok"></i><strong>Dienstag</strong></div>
                <span>81/250</span>
              </div>
              <div class="bh-ki-textarea">Fräsarbeiten nach Zeichnung Nr. 8.2 ausgeführt. Kanten entgratet und Maße kontrolliert.</div>
            </article>
            <article class="bh-ki-day">
              <div class="bh-ki-day-head">
                <div class="bh-ki-day-label"><i></i><strong>Mittwoch</strong></div>
                <span>0/250</span>
              </div>
              <div class="bh-ki-textarea empty"></div>
            </article>
          </div>
        </div>
        <aside class="bh-ki-sheet" aria-label="KI-Formulierungshilfe">
          <div class="bh-ki-sheet-head">
            <span class="bh-ki-badge"><img src="/static/figma/bh/bh-ki-sparkles.svg" width="14" height="14" alt="" />KI-Formulierungshilfe</span>
            <a class="bh-ki-close" href="/berichtsheft/neu" data-page-link aria-label="Schließen">
              <img src="/static/figma/bh/bh-ki-x.svg" width="16" height="16" alt="" />
            </a>
          </div>
          <div class="bh-ki-suggest">
            <p class="bh-ki-suggest-label">Besserer Formulierungsvorschlag:</p>
            <div class="bh-ki-suggest-box">Konventionelle Drehmaschine für Außenrunddrehen eingerichtet. Werkstück nach Zeichnung Nr. 4.2 im Dreibackenfutter gespannt und auf Rundlauf geprüft.</div>
            <p class="bh-ki-suggest-meta">💡 Basierend auf deinem Ausbildungsrahmenplan KW 12</p>
          </div>
          <div class="bh-ki-actions">
            <button class="bh-ki-ghost" type="button" data-action="toast" data-toast="Vorschlag verworfen">Verwerfen</button>
            <button class="bh-ki-primary" type="button" data-action="toast" data-toast="Vorschlag übernommen">Übernehmen</button>
          </div>
          <div class="bh-ki-tip">
            <span aria-hidden="true">💡</span>
            <p><strong>Tipp:</strong> Beschreibe immer kurz WAS du getan hast, WOMIT und WARUM (Zweck/Ziel).</p>
          </div>
        </aside>
      </div>
    `,'''

s084 = r'''  "s08_4-berichtsheft-unterschrift": () => `
      <div class="bh-sig-screen" data-node-id="136:10069">
        <div class="bh-sig-scroll">
          <header class="bh-sig-header">
            <a class="bh-sig-back" href="/berichtsheft" data-page-link aria-label="Zurück">
              <img src="/static/figma/bh/bh-sig-back.svg" width="16" height="16" alt="" />
            </a>
            <h2>Bericht freigeben</h2>
          </header>
          <div class="bh-sig-preview">
            <article class="bh-sig-card">
              <div class="bh-sig-card-head">
                <div>
                  <strong>Berichtswoche KW 12</strong>
                  <span>Abteilung: Fertigung</span>
                </div>
                <em>39 Stunden</em>
              </div>
              <hr class="bh-sig-rule" />
              <div class="bh-sig-days">
                <div><b>Mo</b><span>Konventionelle Drehmaschine eingerichtet &amp; Werkstück gespannt.</span></div>
                <div><b>Di</b><span>Fräsarbeiten nach Zeichnung Nr. 8.2 ausgeführt.</span></div>
                <div><b>Mi</b><span>Schaltungen für Pneumatik-Übung verkabelt &amp; getestet.</span></div>
                <div><b>Do</b><span>Arbeitsschutz-Unterweisung im Betriebsbereich 2.</span></div>
                <div><b>Fr</b><span>Wochenbericht gepflegt und Werkzeuge gereinigt.</span></div>
              </div>
            </article>
          </div>
          <div class="bh-sig-tracker">
            <p class="bh-sig-label">Unterschriften-Status</p>
            <div class="bh-sig-row ok">
              <img src="/static/figma/bh/bh-sig-check-circle.svg" width="18" height="18" alt="" />
              <div><strong>Azubi unterschrieben</strong><span>Digital bestätigt am 08/01/2026</span></div>
            </div>
            <div class="bh-sig-row warn">
              <img src="/static/figma/bh/bh-sig-clock.svg" width="18" height="18" alt="" />
              <div><strong>Ausbilder-Freigabe ausstehend</strong><span>Wird nach deiner Signatur benachrichtigt</span></div>
            </div>
          </div>
          <div class="bh-sig-pad-section">
            <p class="bh-sig-label">Signieren &amp; Bestätigen</p>
            <div class="bh-sig-pad" aria-label="Unterschriftsfeld">
              <img src="/static/figma/bh/bh-sig-edit.svg" width="64" height="40" alt="" />
              <span>Oder hier handschriftlich zeichnen</span>
            </div>
            <label class="bh-sig-check">
              <span class="bh-sig-box" aria-hidden="true"><img src="/static/figma/bh/bh-sig-check.svg" width="12" height="12" alt="" /></span>
              <input type="checkbox" checked hidden />
              Ich bestätige die Richtigkeit der Angaben digital.
            </label>
          </div>
          <div class="visually-hidden" data-bind="reports-live" aria-hidden="true"></div>
        </div>
        <div class="bh-sig-actions">
          <button class="bh-sig-submit" type="button" data-action="toast" data-toast="Zur Unterschrift eingereicht">Unterschreiben &amp; Einreichen</button>
        </div>
      </div>
    `,'''

def day_cell(num, kind="muted", tag=None, green=False):
    """kind: muted|normal|selected; tag: B|S|K|None; green: green dot"""
    wrap_cls = "bh-cal-num"
    if kind == "selected":
        wrap_cls += " selected"
    text_cls = ""
    if kind == "muted":
        text_cls = " muted"
    elif kind == "selected":
        text_cls = " on"
    ind = ""
    if tag == "B":
        ind = '<span class="bh-cal-tag b">B</span>'
    elif tag == "S":
        ind = '<span class="bh-cal-tag s">S</span>'
    elif tag == "K":
        ind = '<span class="bh-cal-tag k">K</span>'
    elif green:
        ind = '<img class="bh-cal-dot" src="/static/figma/bh/bh-cal-dot-green.svg" width="4" height="4" alt="" />'
    else:
        ind = '<img class="bh-cal-dot" src="/static/figma/bh/bh-cal-dot.svg" width="4" height="4" alt="" />'
    return f'<div class="bh-cal-cell"><div class="{wrap_cls}"><span class="{text_cls.strip()}">{num}</span></div><div class="bh-cal-ind">{ind}</div></div>'

# Calendar grid from Figma: 3 weeks Jul 27–Aug 16
week0 = "".join([
    day_cell(27), day_cell(28), day_cell(29), day_cell(30), day_cell(31),
    day_cell(1, "selected", "B"), day_cell(2, "normal"),
])
week1 = "".join([
    day_cell(3, "normal", "S"), day_cell(4, "normal", "S"), day_cell(5, "normal", "B"),
    day_cell(6, "normal"), day_cell(7, "normal", "K"), day_cell(8, "normal"), day_cell(9, "normal"),
])
week2 = "".join([
    day_cell(10, "normal", green=True), day_cell(11, "normal", green=True),
    day_cell(12, "normal"), day_cell(13, "normal"), day_cell(14, "normal"),
    day_cell(15, "normal"), day_cell(16, "normal"),
])

s085 = f'''  "s08_5-berichtsheft-kalenderansicht": () => `
      <div class="bh-cal-screen" data-node-id="136:10142">
        <div class="bh-cal-main">
          <div class="bh-cal-top">
            <div class="bh-cal-title-row">
              <h2>Berichtsheft</h2>
              <a href="/berichtsheft/neu" data-page-link aria-label="Neuer Eintrag">
                <img src="/static/figma/bh/bh-cal-calendar.svg" width="24" height="24" alt="" />
              </a>
            </div>
            <div class="bh-cal-nav-row">
              <div class="bh-cal-month">
                <button type="button" aria-label="Vorheriger Monat"><img src="/static/figma/bh/bh-cal-chevron-left.svg" width="16" height="16" alt="" /></button>
                <strong>August 2026</strong>
                <button type="button" aria-label="Nächster Monat"><img src="/static/figma/bh/bh-cal-chevron-right.svg" width="16" height="16" alt="" /></button>
              </div>
              <div class="bh-cal-toggle" role="tablist" aria-label="Ansicht">
                <a class="bh-cal-tog" href="/berichtsheft" data-page-link>Liste</a>
                <span class="bh-cal-tog active">Kalender</span>
              </div>
            </div>
          </div>
          <div class="bh-cal-card">
            <div class="bh-cal-weekdays"><span>Mo</span><span>Di</span><span>Mi</span><span>Do</span><span>Fr</span><span>Sa</span><span>So</span></div>
            <div class="bh-cal-weeks">
              <div class="bh-cal-week">{week0}</div>
              <div class="bh-cal-week">{week1}</div>
              <div class="bh-cal-week">{week2}</div>
            </div>
          </div>
          <div class="bh-cal-preview">
            <p class="bh-cal-preview-label">Vorschau Heutiger Eintrag</p>
            <article class="bh-cal-entry">
              <div class="bh-cal-entry-head">
                <div>
                  <strong>Fr, 01. August 2026</strong>
                  <span>Betrieblicher Tag</span>
                </div>
                <em>Eingereicht</em>
              </div>
              <p>Hydraulikzylinder gewartet, Dichtungen getauscht</p>
              <hr />
              <div class="bh-cal-entry-foot">
                <span><img src="/static/figma/bh/bh-cal-clock.svg" width="16" height="16" alt="" />8 Std</span>
                <a href="/berichtsheft/neu" data-page-link><img src="/static/figma/bh/bh-cal-pen.svg" width="14" height="14" alt="" />Bearbeiten</a>
              </div>
            </article>
          </div>
          <div class="bh-cal-stats">
            <div class="bh-cal-stats-row"><strong>KW 31</strong><span>4/5 Tage erfasst</span></div>
            <div class="bh-cal-bar"><i style="width:280px"></i></div>
          </div>
        </div>
        <nav class="bh-cal-tabs" aria-label="Hauptnavigation">
          <a href="/dashboard" data-page-link><img src="/static/figma/bh/bh-cal-house.svg" width="22" height="22" alt="" /><span>Start</span></a>
          <a href="/lernen" data-page-link><img src="/static/figma/bh/bh-cal-book.svg" width="22" height="22" alt="" /><span>Lernen</span></a>
          <a href="/fortschritt" data-page-link><img src="/static/figma/bh/bh-cal-trending.svg" width="22" height="22" alt="" /><span>Fortschritt</span></a>
          <a href="/berichtsheft" data-page-link class="active"><img src="/static/figma/bh/bh-cal-file.svg" width="22" height="22" alt="" /><span>Bericht</span></a>
          <a href="/mehr" data-page-link><img src="/static/figma/bh/bh-cal-menu.svg" width="22" height="22" alt="" /><span>Mehr</span></a>
        </nav>
      </div>
    `,'''

s086 = r'''  "s08_6-pdf-export": () => `
      <div class="bh-pdf-screen" data-node-id="136:10353">
        <div class="bh-pdf-dim">
          <div class="bh-pdf-bg-head">
            <h2>Berichtsheft</h2>
            <img src="/static/figma/bh/bh-pdf-calendar.svg" width="24" height="24" alt="" />
          </div>
          <div class="bh-pdf-sheet">
            <div class="bh-pdf-handle" aria-hidden="true"></div>
            <div class="bh-pdf-title-row">
              <h3>PDF Export</h3>
              <a class="bh-pdf-close" href="/berichtsheft" data-page-link aria-label="Schließen">
                <img src="/static/figma/bh/bh-pdf-x.svg" width="14" height="14" alt="" />
              </a>
            </div>
            <div class="bh-pdf-section">
              <p class="bh-pdf-label">Zeitraum</p>
              <div class="bh-pdf-dates">
                <label class="bh-pdf-date"><span>Von</span><strong>01.07.2026</strong></label>
                <label class="bh-pdf-date"><span>Bis</span><strong>31.07.2026</strong></label>
              </div>
            </div>
            <div class="bh-pdf-pills">
              <button type="button">Letzte Woche</button>
              <button type="button" class="active">Letzter Monat</button>
              <button type="button">Quartal</button>
              <button type="button">Alles</button>
            </div>
            <div class="bh-pdf-section">
              <p class="bh-pdf-label">Berichtsheft-Format</p>
              <div class="bh-pdf-formats">
                <label class="bh-pdf-fmt active">
                  <img src="/static/figma/bh/bh-pdf-radio-on.svg" width="12" height="12" alt="" />
                  <span>IHK-Standard</span>
                  <input type="radio" name="export-fmt" value="ihk" checked hidden />
                </label>
                <label class="bh-pdf-fmt">
                  <img src="/static/figma/bh/bh-pdf-radio-off.svg" width="12" height="12" alt="" />
                  <span>Kompakt</span>
                  <input type="radio" name="export-fmt" value="compact" hidden />
                </label>
              </div>
            </div>
            <div class="bh-pdf-toggles">
              <div class="bh-pdf-tog"><span>Unterschriften einblenden</span><img src="/static/figma/bh/bh-pdf-toggle-on.svg" width="44" height="24" alt="" /></div>
              <div class="bh-pdf-tog"><span>Kommentare des Ausbilders</span><img src="/static/figma/bh/bh-pdf-toggle-on.svg" width="44" height="24" alt="" /></div>
              <div class="bh-pdf-tog"><span>Abwesenheiten markieren</span><img src="/static/figma/bh/bh-pdf-toggle-off.svg" width="44" height="24" alt="" /></div>
            </div>
            <div class="bh-pdf-cta-row">
              <div class="bh-pdf-thumb" aria-hidden="true">
                <i></i><i></i><i></i>
                <div><b></b><div><i></i><i></i></div></div>
              </div>
              <div class="bh-pdf-cta">
                <button type="button" data-action="toast" data-toast="PDF wird vorbereitet…">PDF erstellen</button>
                <p>Geschätzte Größe: ~12 Seiten</p>
              </div>
            </div>
          </div>
          <nav class="bh-pdf-tabs" aria-label="Hauptnavigation">
            <a href="/dashboard" data-page-link><img src="/static/figma/bh/bh-pdf-house.svg" width="22" height="22" alt="" /><span>Start</span></a>
            <a href="/lernen" data-page-link><img src="/static/figma/bh/bh-pdf-book.svg" width="22" height="22" alt="" /><span>Lernen</span></a>
            <a href="/fortschritt" data-page-link><img src="/static/figma/bh/bh-pdf-trending.svg" width="22" height="22" alt="" /><span>Fortschritt</span></a>
            <a href="/berichtsheft" data-page-link class="active"><img src="/static/figma/bh/bh-pdf-file.svg" width="22" height="22" alt="" /><span>Bericht</span></a>
            <a href="/mehr" data-page-link><img src="/static/figma/bh/bh-pdf-menu.svg" width="22" height="22" alt="" /><span>Mehr</span></a>
          </nav>
        </div>
      </div>
    `,'''

s087 = r'''  "s08_7-berichtsheft-leerzustand": () => `
      <div class="bh-empty-screen" data-node-id="136:10462">
        <div class="bh-empty-main">
          <header class="bh-empty-header"><h2>Berichtsheft</h2></header>
          <div class="bh-empty-body">
            <div class="bh-empty-hero">
              <div class="bh-empty-illo">
                <img src="/static/figma/bh/bh-empty-clipboard.svg" width="56" height="56" alt="" />
              </div>
              <h3>Noch keine Einträge</h3>
              <p>Dein digitales Berichtsheft ist bereit! Dokumentiere hier deine täglichen Tätigkeiten.</p>
            </div>
            <article class="bh-empty-tip">
              <span class="bh-empty-tip-ico"><img src="/static/figma/bh/bh-empty-bulb.svg" width="18" height="18" alt="" /></span>
              <div>
                <strong>TIPP</strong>
                <p>Trage am besten jeden Tag ein, was du gemacht hast. Das macht die wöchentliche Zusammenfassung einfacher!</p>
              </div>
            </article>
            <div class="bh-empty-actions">
              <a class="bh-empty-cta" href="/berichtsheft/neu" data-page-link>
                <img src="/static/figma/bh/bh-empty-plus.svg" width="18" height="18" alt="" />
                Ersten Eintrag erstellen
              </a>
              <button class="bh-empty-help" type="button" data-action="toast" data-toast="Hilfe: Wöchentlich eintragen, dann zur Unterschrift">Wie funktioniert es?</button>
            </div>
          </div>
        </div>
        <nav class="bh-empty-tabs" aria-label="Navigation">
          <a href="/lernen" data-page-link><img src="/static/figma/bh/bh-empty-book.svg" width="22" height="22" alt="" /><span>Lernen</span></a>
          <a href="/berichtsheft" data-page-link class="active"><img src="/static/figma/bh/bh-empty-clipboard-tab.svg" width="22" height="22" alt="" /><span>Bericht</span></a>
          <a href="/mehr" data-page-link><img src="/static/figma/bh/bh-empty-user.svg" width="22" height="22" alt="" /><span>Mehr</span></a>
        </nav>
        <div class="bh-empty-home" aria-hidden="true"><i></i></div>
      </div>
    `,'''

for key, block in [
    ("s08_3-berichtsheft-ki-assistent", s083),
    ("s08_4-berichtsheft-unterschrift", s084),
    ("s08_5-berichtsheft-kalenderansicht", s085),
    ("s08_6-pdf-export", s086),
    ("s08_7-berichtsheft-leerzustand", s087),
]:
    pat = re.compile(rf'  "{key}": \(\) => `[\s\S]*?`,\n(?=  ")')
    if not pat.search(js):
        raise SystemExit(f"screen block not found: {key}")
    js = pat.sub(block + "\n", js, count=1)

SCREENS.write_text(js, encoding="utf-8")
print("screens.js updated")

css_block = r'''
/* --- 08.3 Berichtsheft KI-Assistent --- */
.app-frame[data-chrome="bh"]:has(.bh-ki-screen) { height: 897px; min-height: 897px; }
.bh-ki-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #0b0f19; color: #f8fafc; justify-content: space-between;
}
.bh-ki-body { display: flex; flex-direction: column; flex-shrink: 0; width: 100%; }
.bh-ki-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 20px 12px; box-sizing: border-box;
}
.bh-ki-back {
  display: grid; place-items: center; width: 32px; height: 32px; border-radius: 8px;
  background: #161e2d; flex-shrink: 0;
}
.bh-ki-back img { width: 16px; height: 16px; display: block; }
.bh-ki-titles { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.bh-ki-titles h2 { margin: 0; font-size: 18px; font-weight: 700; color: #f8fafc; }
.bh-ki-titles p { margin: 0; font-size: 12px; color: #f59e0b; }
.bh-ki-days {
  display: flex; flex-direction: column; gap: 16px;
  padding: 10px 20px 20px; box-sizing: border-box;
}
.bh-ki-day {
  display: flex; flex-direction: column; gap: 10px; padding: 14px;
  border-radius: 12px; background: #161e2d; border: 1px solid #2e3a52; box-sizing: border-box;
}
.bh-ki-day.active { border-color: #14b8a6; }
.bh-ki-day-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.bh-ki-day-label { display: flex; align-items: center; gap: 8px; }
.bh-ki-day-label > i {
  display: grid; place-items: center; width: 12px; height: 12px; border-radius: 100px;
  background: #2e3a52; flex-shrink: 0;
}
.bh-ki-day-label > i.ok { background: #10b981; }
.bh-ki-day-label > i.ok::after {
  content: ""; width: 4px; height: 4px; border-radius: 100px; background: #0b0f19;
}
.bh-ki-day-label strong { color: #f8fafc; font-size: 15px; font-weight: 700; }
.bh-ki-day-head > span { color: #64748b; font-size: 11px; }
.bh-ki-textarea {
  display: flex; align-items: flex-start; gap: 4px;
  width: 100%; height: 64px; box-sizing: border-box; padding: 12px;
  border-radius: 8px; border: 1px solid #2e3a52; background: #1e293b;
  color: #f8fafc; font-size: 13px; line-height: 1.4; overflow: hidden;
}
.bh-ki-textarea.active { border-color: rgba(20,184,166,0.25); }
.bh-ki-textarea.empty { color: transparent; }
.bh-ki-textarea .caret {
  display: block; width: 2px; height: 16px; background: #14b8a6; flex-shrink: 0; margin-top: 1px;
}
.bh-ki-sheet {
  display: flex; flex-direction: column; gap: 16px; padding: 20px;
  background: #1e293b; border-top: 1px solid rgba(20,184,166,0.25);
  border-radius: 24px 24px 0 0; box-shadow: 0 -8px 24px rgba(0,0,0,0.5);
  box-sizing: border-box; flex-shrink: 0;
}
.bh-ki-sheet-head { display: flex; align-items: center; justify-content: space-between; }
.bh-ki-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 6px 10px; border-radius: 100px;
  background: rgba(20,184,166,0.1); border: 1px solid rgba(20,184,166,0.25);
  color: #14b8a6; font-size: 11px; font-weight: 700; text-transform: uppercase;
}
.bh-ki-badge img { width: 14px; height: 14px; display: block; }
.bh-ki-close { display: grid; place-items: center; width: 16px; height: 16px; }
.bh-ki-close img { width: 16px; height: 16px; display: block; }
.bh-ki-suggest { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.bh-ki-suggest-label { margin: 0; color: #94a3b8; font-size: 12px; font-weight: 600; }
.bh-ki-suggest-box {
  padding: 14px; border-radius: 12px; background: #161e2d;
  border: 1px solid rgba(20,184,166,0.13); color: #f8fafc; font-size: 13px; line-height: 1.5;
  box-sizing: border-box;
}
.bh-ki-suggest-meta { margin: 0; color: #64748b; font-size: 11px; }
.bh-ki-actions { display: flex; gap: 10px; width: 100%; }
.bh-ki-ghost, .bh-ki-primary {
  flex: 1; display: flex; align-items: center; justify-content: center;
  height: 40px; border-radius: 100px; border: 0; cursor: pointer; font-size: 13px;
}
.bh-ki-ghost { background: #2e3a52; color: #94a3b8; font-weight: 600; }
.bh-ki-primary { background: #14b8a6; color: #0b0f19; font-weight: 700; }
.bh-ki-tip {
  display: flex; gap: 10px; align-items: center; padding: 12px;
  border-radius: 10px; background: #161e2d; border: 1px solid #2e3a52; box-sizing: border-box;
}
.bh-ki-tip > span { font-size: 20px; line-height: 1; flex-shrink: 0; }
.bh-ki-tip p { margin: 0; color: #94a3b8; font-size: 11px; line-height: 1.4; }
.bh-ki-tip strong { color: #f8fafc; font-weight: 700; }

/* --- 08.4 Berichtsheft Unterschrift --- */
.app-frame[data-chrome="bh"]:has(.bh-sig-screen) { height: 844px; min-height: 844px; }
.bh-sig-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #0b0f19; color: #f8fafc;
}
.bh-sig-scroll { flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; }
.bh-sig-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 20px 12px; box-sizing: border-box;
}
.bh-sig-back {
  display: grid; place-items: center; width: 32px; height: 32px; border-radius: 8px;
  background: #161e2d; flex-shrink: 0;
}
.bh-sig-back img { width: 16px; height: 16px; display: block; }
.bh-sig-header h2 { margin: 0; font-size: 18px; font-weight: 700; color: #f8fafc; }
.bh-sig-preview { padding: 20px; box-sizing: border-box; }
.bh-sig-card {
  display: flex; flex-direction: column; gap: 12px; padding: 16px;
  border-radius: 16px; background: #161e2d; border: 1px solid #2e3a52; box-sizing: border-box;
}
.bh-sig-card-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.bh-sig-card-head > div { display: flex; flex-direction: column; gap: 2px; }
.bh-sig-card-head strong { color: #f8fafc; font-size: 16px; font-weight: 700; }
.bh-sig-card-head span { color: #64748b; font-size: 12px; }
.bh-sig-card-head em {
  font-style: normal; padding: 6px 10px; border-radius: 6px;
  background: rgba(59,130,246,0.11); color: #3b82f6; font-size: 14px; font-weight: 700;
}
.bh-sig-rule { border: 0; border-top: 1px solid #2e3a52; margin: 0; width: 100%; }
.bh-sig-days { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.bh-sig-days > div { display: flex; gap: 10px; align-items: flex-start; width: 100%; }
.bh-sig-days b { color: #3b82f6; font-size: 12px; font-weight: 700; width: 24px; flex-shrink: 0; }
.bh-sig-days span {
  flex: 1; min-width: 0; color: #94a3b8; font-size: 12px; line-height: 1.4;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.bh-sig-tracker {
  display: flex; flex-direction: column; gap: 8px;
  padding: 0 20px 20px; box-sizing: border-box;
}
.bh-sig-label {
  margin: 0 0 4px; color: #94a3b8; font-size: 14px; font-weight: 700; text-transform: uppercase;
}
.bh-sig-row {
  display: flex; align-items: center; gap: 12px; padding: 12px;
  border-radius: 10px; box-sizing: border-box; width: 100%;
}
.bh-sig-row img { width: 18px; height: 18px; display: block; flex-shrink: 0; }
.bh-sig-row > div { display: flex; flex-direction: column; gap: 2px; }
.bh-sig-row strong { font-size: 13px; font-weight: 600; }
.bh-sig-row span { color: #94a3b8; font-size: 11px; }
.bh-sig-row.ok { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.13); }
.bh-sig-row.ok strong { color: #10b981; }
.bh-sig-row.warn { background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.13); }
.bh-sig-row.warn strong { color: #f59e0b; }
.bh-sig-pad-section {
  display: flex; flex-direction: column; gap: 10px;
  padding: 0 20px 24px; box-sizing: border-box;
}
.bh-sig-pad {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  height: 100px; border-radius: 12px; background: #161e2d;
  border: 1.5px dashed #2e3a52; box-sizing: border-box;
}
.bh-sig-pad img { width: 64px; height: 40px; display: block; }
.bh-sig-pad span { color: #64748b; font-size: 13px; }
.bh-sig-check {
  display: flex; align-items: center; gap: 10px; color: #f8fafc; font-size: 13px; cursor: pointer;
}
.bh-sig-box {
  display: grid; place-items: center; width: 20px; height: 20px; border-radius: 4px;
  background: #3b82f6; flex-shrink: 0;
}
.bh-sig-box img { width: 12px; height: 12px; display: block; }
.bh-sig-actions {
  padding: 20px; background: #161e2d; border-top: 1px solid #2e3a52; box-sizing: border-box; flex-shrink: 0;
}
.bh-sig-submit {
  display: flex; align-items: center; justify-content: center; width: 100%; height: 48px;
  border: 0; border-radius: 100px; background: #3b82f6; color: #f8fafc;
  font-size: 14px; font-weight: 700; cursor: pointer;
}

/* --- 08.5 Berichtsheft Kalender (light) --- */
.app-frame[data-chrome="bh"]:has(.bh-cal-screen),
.app-frame[data-chrome="bh"]:has(.bh-pdf-screen),
.app-frame[data-chrome="bh"]:has(.bh-empty-screen) {
  height: 844px; min-height: 844px; background: #f8fafc;
}
.app-frame[data-chrome="bh"]:has(.bh-cal-screen) .app-status,
.app-frame[data-chrome="bh"]:has(.bh-pdf-screen) .app-status,
.app-frame[data-chrome="bh"]:has(.bh-empty-screen) .app-status {
  color: #1e293b;
}
.app-frame[data-chrome="bh"]:has(.bh-cal-screen) .login-status-icon,
.app-frame[data-chrome="bh"]:has(.bh-empty-screen) .login-status-icon {
  filter: none;
}
.app-frame[data-chrome="bh"]:has(.bh-pdf-screen) .app-status { color: #fff; }
.app-frame[data-chrome="bh"]:has(.bh-pdf-screen) .login-status-icon { filter: brightness(0) invert(1); }
.app-frame[data-chrome="bh"]:has(.bh-cal-screen) .app-content,
.app-frame[data-chrome="bh"]:has(.bh-pdf-screen) .app-content,
.app-frame[data-chrome="bh"]:has(.bh-empty-screen) .app-content {
  background: #f8fafc;
}
.app-frame[data-chrome="bh"]:has(.bh-pdf-screen) .app-content { background: #0f172a; }
.app-frame[data-chrome="bh"]:has(.bh-empty-screen) .app-content { background: #f9fafc; }

.bh-cal-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #f8fafc; color: #1e293b;
}
.bh-cal-main { flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; }
.bh-cal-top {
  display: flex; flex-direction: column; gap: 16px;
  padding: 8px 20px 12px; box-sizing: border-box;
}
.bh-cal-title-row { display: flex; align-items: center; justify-content: space-between; }
.bh-cal-title-row h2 { margin: 0; font-size: 22px; font-weight: 700; color: #1e293b; }
.bh-cal-title-row img { width: 24px; height: 24px; display: block; }
.bh-cal-nav-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.bh-cal-month { display: flex; align-items: center; gap: 12px; }
.bh-cal-month button {
  display: grid; place-items: center; width: 16px; height: 16px;
  padding: 0; border: 0; background: transparent; cursor: pointer;
}
.bh-cal-month img { width: 16px; height: 16px; display: block; }
.bh-cal-month strong { font-size: 16px; font-weight: 600; color: #1e293b; }
.bh-cal-toggle {
  display: flex; gap: 4px; padding: 3px; border-radius: 100px; background: #f1f5f9;
}
.bh-cal-tog {
  padding: 6px 12px; border-radius: 100px; font-size: 13px; color: #64748b; font-weight: 500;
  text-decoration: none;
}
.bh-cal-tog.active {
  background: #fff; color: #2563eb; font-weight: 600;
  box-shadow: 0 4px 6px rgba(15,23,42,0.04);
}
.bh-cal-card {
  background: #fff; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;
  border-radius: 0 0 20px 20px; padding: 16px 20px; box-sizing: border-box;
}
.bh-cal-weekdays {
  display: flex; justify-content: space-between; padding-bottom: 12px;
  color: #94a3b8; font-size: 12px; font-weight: 600; text-align: center;
}
.bh-cal-weekdays span { width: 40px; }
.bh-cal-weeks { display: flex; flex-direction: column; gap: 8px; }
.bh-cal-week { display: flex; justify-content: space-between; width: 100%; }
.bh-cal-cell {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  width: 40px; height: 52px;
}
.bh-cal-num {
  display: grid; place-items: center; width: 26px; height: 26px; border-radius: 13px;
}
.bh-cal-num.selected { background: #2563eb; }
.bh-cal-num span { font-size: 13px; font-weight: 600; color: #1e293b; }
.bh-cal-num span.muted { color: #94a3b8; font-weight: 400; }
.bh-cal-num span.on { color: #fff; font-weight: 600; }
.bh-cal-ind { display: flex; justify-content: center; width: 100%; min-height: 14px; }
.bh-cal-dot { width: 4px; height: 4px; display: block; margin-top: 4px; }
.bh-cal-tag {
  display: inline-flex; padding: 1px 4px; border-radius: 4px;
  font-size: 10px; font-weight: 700; line-height: 1.2;
}
.bh-cal-tag.b { background: #eff6ff; color: #2563eb; }
.bh-cal-tag.s { background: #faf5ff; color: #7e22ce; }
.bh-cal-tag.k { background: #f1f5f9; color: #64748b; }
.bh-cal-preview {
  display: flex; flex-direction: column; gap: 12px;
  padding: 16px 20px 8px; box-sizing: border-box;
}
.bh-cal-preview-label { margin: 0; color: #64748b; font-size: 14px; font-weight: 600; }
.bh-cal-entry {
  display: flex; flex-direction: column; gap: 12px; padding: 16px;
  border-radius: 16px; background: #fff; border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px rgba(15,23,42,0.04); box-sizing: border-box;
}
.bh-cal-entry-head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.bh-cal-entry-head > div { display: flex; flex-direction: column; gap: 2px; }
.bh-cal-entry-head strong { color: #1e293b; font-size: 15px; font-weight: 700; }
.bh-cal-entry-head span { color: #2563eb; font-size: 12px; font-weight: 500; }
.bh-cal-entry-head em {
  font-style: normal; padding: 4px 8px; border-radius: 6px;
  background: #ecfdf5; color: #10b981; font-size: 11px; font-weight: 600;
}
.bh-cal-entry > p { margin: 0; color: #1e293b; font-size: 13px; line-height: 1.4; }
.bh-cal-entry hr { border: 0; border-top: 1px solid #e2e8f0; margin: 0; width: 100%; }
.bh-cal-entry-foot { display: flex; align-items: center; justify-content: space-between; }
.bh-cal-entry-foot span, .bh-cal-entry-foot a {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 13px; font-weight: 600; text-decoration: none;
}
.bh-cal-entry-foot span { color: #64748b; }
.bh-cal-entry-foot a { color: #2563eb; }
.bh-cal-entry-foot img { display: block; }
.bh-cal-stats {
  display: flex; flex-direction: column; gap: 8px;
  padding: 12px 20px; box-sizing: border-box;
}
.bh-cal-stats-row { display: flex; justify-content: space-between; font-size: 13px; }
.bh-cal-stats-row strong { color: #1e293b; font-weight: 600; }
.bh-cal-stats-row span { color: #64748b; font-weight: 500; }
.bh-cal-bar { height: 8px; border-radius: 4px; background: #e2e8f0; overflow: hidden; }
.bh-cal-bar i { display: block; height: 100%; background: #2563eb; border-radius: 4px; }
.bh-cal-tabs {
  display: flex; align-items: center; justify-content: space-between;
  height: 72px; padding: 0 0 8px; background: #fff;
  border-top: 1px solid #e2e8f0; box-sizing: border-box; flex-shrink: 0;
}
.bh-cal-tabs a {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  width: 70px; color: #64748b; font-size: 11px; font-weight: 500; text-decoration: none;
}
.bh-cal-tabs a.active { color: #2563eb; font-weight: 600; }
.bh-cal-tabs img { width: 22px; height: 22px; display: block; }

/* --- 08.6 PDF Export --- */
.bh-pdf-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: rgba(15,23,42,0.6); color: #1e293b; position: relative;
}
.bh-pdf-dim {
  display: flex; flex-direction: column; flex: 1; min-height: 0; justify-content: space-between;
}
.bh-pdf-bg-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px; box-sizing: border-box;
}
.bh-pdf-bg-head h2 { margin: 0; font-size: 22px; font-weight: 700; color: #fff; }
.bh-pdf-bg-head img { width: 24px; height: 24px; display: block; filter: brightness(0) invert(1); }
.bh-pdf-sheet {
  display: flex; flex-direction: column; gap: 20px;
  padding: 12px 20px 20px; background: #fff;
  border-radius: 24px 24px 0 0; box-shadow: 0 -10px 24px rgba(15,23,42,0.1);
  box-sizing: border-box; flex-shrink: 0;
}
.bh-pdf-handle {
  width: 40px; height: 4px; border-radius: 2px; background: #e2e8f0; margin: 0 auto;
}
.bh-pdf-title-row { display: flex; align-items: center; justify-content: space-between; }
.bh-pdf-title-row h3 { margin: 0; font-size: 18px; font-weight: 700; color: #1e293b; }
.bh-pdf-close {
  display: grid; place-items: center; width: 30px; height: 30px; border-radius: 15px;
  background: #f1f5f9;
}
.bh-pdf-close img { width: 14px; height: 14px; display: block; }
.bh-pdf-section { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.bh-pdf-label { margin: 0; color: #64748b; font-size: 13px; font-weight: 600; }
.bh-pdf-dates { display: flex; gap: 12px; width: 100%; }
.bh-pdf-date {
  flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 12px;
  border: 1px solid #e2e8f0; border-radius: 8px; box-sizing: border-box;
}
.bh-pdf-date span { color: #64748b; font-size: 11px; }
.bh-pdf-date strong { color: #1e293b; font-size: 13px; font-weight: 500; }
.bh-pdf-pills { display: flex; flex-wrap: wrap; gap: 6px; }
.bh-pdf-pills button {
  padding: 6px 10px; border-radius: 100px; border: 1px solid #e2e8f0;
  background: transparent; color: #64748b; font-size: 11px; font-weight: 500; cursor: pointer;
}
.bh-pdf-pills button.active {
  background: #eff6ff; border-color: #2563eb; color: #2563eb; font-weight: 600;
}
.bh-pdf-formats { display: flex; gap: 8px; width: 100%; }
.bh-pdf-fmt {
  flex: 1; display: flex; align-items: center; gap: 8px; padding: 12px;
  border: 1px solid #e2e8f0; border-radius: 8px; box-sizing: border-box; cursor: pointer;
  color: #64748b; font-size: 12px; font-weight: 500;
}
.bh-pdf-fmt.active {
  background: #eff6ff; border-color: #2563eb; color: #2563eb; font-weight: 600;
}
.bh-pdf-fmt img { width: 12px; height: 12px; display: block; flex-shrink: 0; }
.bh-pdf-toggles { display: flex; flex-direction: column; gap: 12px; width: 100%; }
.bh-pdf-tog { display: flex; align-items: center; justify-content: space-between; }
.bh-pdf-tog span { color: #1e293b; font-size: 13px; font-weight: 500; }
.bh-pdf-tog img { width: 44px; height: 24px; display: block; }
.bh-pdf-cta-row { display: flex; align-items: center; gap: 16px; width: 100%; }
.bh-pdf-thumb {
  width: 56px; height: 76px; padding: 6px; border-radius: 6px;
  background: #f1f5f9; border: 1px solid #e2e8f0; box-sizing: border-box;
  display: flex; flex-direction: column; gap: 4px; flex-shrink: 0;
}
.bh-pdf-thumb > i:nth-child(1) { height: 4px; border-radius: 2px; background: #94a3b8; }
.bh-pdf-thumb > i:nth-child(2),
.bh-pdf-thumb > i:nth-child(3) { height: 2px; border-radius: 1px; background: #94a3b8; opacity: 0.5; }
.bh-pdf-thumb > div { display: flex; gap: 2px; align-items: flex-start; }
.bh-pdf-thumb > div > b {
  width: 8px; height: 8px; border-radius: 2px; background: #2563eb; opacity: 0.2; flex-shrink: 0;
  font-style: normal; display: block;
}
.bh-pdf-thumb > div > div { flex: 1; display: flex; flex-direction: column; gap: 2px; }
.bh-pdf-thumb > div > div > i { height: 2px; border-radius: 1px; background: #94a3b8; opacity: 0.5; display: block; }
.bh-pdf-cta { flex: 1; display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.bh-pdf-cta button {
  width: 100%; padding: 12px 16px; border: 0; border-radius: 12px;
  background: #2563eb; color: #fff; font-size: 15px; font-weight: 600; cursor: pointer;
}
.bh-pdf-cta p { margin: 0; text-align: center; color: #64748b; font-size: 11px; }
.bh-pdf-tabs {
  display: flex; align-items: center; justify-content: space-between;
  height: 72px; padding: 0 0 8px; background: #fff;
  border-top: 1px solid #e2e8f0; box-sizing: border-box; flex-shrink: 0;
}
.bh-pdf-tabs a {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  width: 70px; color: #64748b; font-size: 11px; font-weight: 500; text-decoration: none;
}
.bh-pdf-tabs a.active { color: #2563eb; font-weight: 600; }
.bh-pdf-tabs img { width: 22px; height: 22px; display: block; }

/* --- 08.7 Berichtsheft Leerzustand --- */
.bh-empty-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #f9fafc; color: #1f2937;
}
.bh-empty-main { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.bh-empty-header {
  display: flex; align-items: center; height: 56px; padding: 0 20px;
  background: #fff; border-bottom: 1px solid #e5e7eb; box-sizing: border-box;
}
.bh-empty-header h2 { margin: 0; font-size: 18px; font-weight: 800; color: #1f2937; }
.bh-empty-body {
  display: flex; flex-direction: column; gap: 24px; padding: 20px; box-sizing: border-box;
}
.bh-empty-hero {
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  padding: 24px 0 16px; text-align: center;
}
.bh-empty-illo {
  display: grid; place-items: center; width: 120px; height: 120px; border-radius: 60px;
  background: #eff6ff;
}
.bh-empty-illo img { width: 56px; height: 56px; display: block; }
.bh-empty-hero h3 { margin: 0; font-size: 20px; font-weight: 800; color: #1f2937; }
.bh-empty-hero p {
  margin: 0; max-width: 280px; color: #4b5563; font-size: 14px; font-weight: 500; line-height: 1.4;
}
.bh-empty-tip {
  display: flex; gap: 12px; align-items: flex-start; padding: 16px;
  border-radius: 16px; background: #eff6ff; border: 1px solid #dbeafe; box-sizing: border-box;
}
.bh-empty-tip-ico {
  display: grid; place-items: center; width: 36px; height: 36px; border-radius: 18px;
  background: #dbeafe; flex-shrink: 0;
}
.bh-empty-tip-ico img { width: 18px; height: 18px; display: block; }
.bh-empty-tip strong { display: block; color: #1e3a8a; font-size: 13px; font-weight: 700; }
.bh-empty-tip p { margin: 2px 0 0; color: #4b5563; font-size: 13px; font-weight: 500; line-height: 1.4; }
.bh-empty-actions { display: flex; flex-direction: column; align-items: center; gap: 16px; width: 100%; }
.bh-empty-cta {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  width: 100%; height: 48px; border-radius: 100px; background: #1e3a8a; color: #fff;
  font-size: 15px; font-weight: 700; text-decoration: none;
  box-shadow: 0 4px 8px rgba(30,58,138,0.14);
}
.bh-empty-cta img { width: 18px; height: 18px; display: block; }
.bh-empty-help {
  border: 0; background: transparent; color: #1e3a8a; font-size: 14px; font-weight: 600;
  text-decoration: underline; cursor: pointer; padding: 0;
}
.bh-empty-tabs {
  display: flex; align-items: center; justify-content: space-between;
  height: 64px; padding: 0 16px; background: #fff;
  border-top: 1px solid #e5e7eb; box-sizing: border-box; flex-shrink: 0;
}
.bh-empty-tabs a {
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
  width: 72px; color: #9ca3af; font-size: 11px; font-weight: 500; text-decoration: none;
}
.bh-empty-tabs a.active { color: #1e3a8a; font-weight: 600; }
.bh-empty-tabs img { width: 22px; height: 22px; display: block; }
.bh-empty-home {
  display: flex; align-items: center; justify-content: center; height: 34px; flex-shrink: 0;
}
.bh-empty-home i {
  display: block; width: 134px; height: 5px; border-radius: 100px; background: #1f2937;
}
'''

css = CSS.read_text(encoding="utf-8")
marker = "/* --- 08.3 Berichtsheft KI-Assistent --- */"
if marker in css:
    # replace from marker to end-of-file or next major section after our block
    start = css.find(marker)
    # keep anything after our previous append if re-run: cut from marker
    css = css[:start].rstrip() + "\n" + css_block
else:
    # append after 08.2 styles
    anchor = ".bh-ne-submit {\n  background: #3b82f6; border: 0; color: #f8fafc; font-weight: 700;\n}"
    idx = css.find(anchor)
    if idx < 0:
        raise SystemExit("CSS anchor for 08.2 not found")
    end = idx + len(anchor)
    css = css[:end] + "\n" + css_block + css[end:]

CSS.write_text(css, encoding="utf-8")
print("ui.css updated")
print("done")
