# -*- coding: utf-8 -*-
from pathlib import Path
import re

screens_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
css_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\ui.css")
text = screens_path.read_text(encoding="utf-8")

# set chrome bh for 08.2
text = text.replace(
    '"/berichtsheft/neu": { layout: "app", screen: "s08_2-berichtsheft-neuer-eintrag", title: "Berichtsheft — Neuer Eintrag", tab: "reports", num: "08.2" }',
    '"/berichtsheft/neu": { layout: "app", screen: "s08_2-berichtsheft-neuer-eintrag", title: "Berichtsheft — Neuer Eintrag", tab: "reports", num: "08.2", chrome: "bh" }',
)

s082 = '''  "s08_2-berichtsheft-neuer-eintrag": () => `
      <div class="bh-ne-screen" data-node-id="136:9912">
        <form class="bh-ne-form" data-action="create-report">
          <div class="bh-ne-scroll">
            <header class="bh-ne-header">
              <a class="bh-ne-back" href="/berichtsheft" data-page-link aria-label="Zurück">
                <img src="/static/figma/bh/bh-ne-back.svg" width="16" height="16" alt="" />
              </a>
              <div class="bh-ne-titles">
                <h2>Neuer Eintrag</h2>
                <p>Lücke füllen (KW 12)</p>
              </div>
            </header>
            <div class="bh-ne-fields">
              <label class="bh-ne-field">
                <span>Ausbildungszeitraum</span>
                <div class="bh-ne-select">
                  <select name="period" aria-label="Ausbildungszeitraum">
                    <option>KW 12 — 18.–22. März 2025</option>
                    <option>KW 11 — 11.–15. März 2025</option>
                    <option>KW 10 — 04.–08. März 2025</option>
                  </select>
                  <img src="/static/figma/bh/bh-ne-chevron.svg" width="16" height="16" alt="" />
                </div>
              </label>
              <label class="bh-ne-field">
                <span>Abteilung / Einsatzbereich</span>
                <div class="bh-ne-select">
                  <select name="department" aria-label="Abteilung">
                    <option>Fertigung</option>
                    <option>Montage</option>
                    <option>Qualitätssicherung</option>
                  </select>
                  <img src="/static/figma/bh/bh-ne-chevron.svg" width="16" height="16" alt="" />
                </div>
              </label>
            </div>
            <div class="bh-ne-days">
              <p class="bh-ne-section">Tägliche Tätigkeiten</p>
              <article class="bh-ne-day filled">
                <div class="bh-ne-day-head">
                  <div class="bh-ne-day-label"><i class="ok"></i><strong>Montag</strong></div>
                  <span>98/250</span>
                </div>
                <textarea name="mon" maxlength="250" rows="3">Drehmaschine einrichten, Werkstück spannen, Schnittdaten berechnen und Probedurchlauf durchgeführt.</textarea>
              </article>
              <article class="bh-ne-day filled">
                <div class="bh-ne-day-head">
                  <div class="bh-ne-day-label"><i class="ok"></i><strong>Dienstag</strong></div>
                  <span>81/250</span>
                </div>
                <textarea name="tue" maxlength="250" rows="3">Fräsarbeiten nach Zeichnung Nr. 8.2 ausgeführt. Kanten entgratet und Maße kontrolliert.</textarea>
              </article>
              <article class="bh-ne-day">
                <div class="bh-ne-day-head">
                  <div class="bh-ne-day-label"><i></i><strong>Mittwoch</strong></div>
                  <span>0/250</span>
                </div>
                <textarea name="wed" maxlength="250" rows="3" placeholder="Tätigkeiten am Mittwoch eintragen..."></textarea>
              </article>
              <article class="bh-ne-day">
                <div class="bh-ne-day-head">
                  <div class="bh-ne-day-label"><i></i><strong>Donnerstag</strong></div>
                  <span>0/250</span>
                </div>
                <textarea name="thu" maxlength="250" rows="3" placeholder="Tätigkeiten am Donnerstag eintragen..."></textarea>
              </article>
              <article class="bh-ne-day">
                <div class="bh-ne-day-head">
                  <div class="bh-ne-day-label"><i></i><strong>Freitag</strong></div>
                  <span>0/250</span>
                </div>
                <textarea name="fri" maxlength="250" rows="3" placeholder="Tätigkeiten am Freitag eintragen..."></textarea>
              </article>
            </div>
            <div class="bh-ne-hours">
              <span>Wochenstunden gesamt</span>
              <label class="bh-ne-hours-box">
                <input type="number" name="hours" min="1" max="60" step="0.5" value="39" required aria-label="Wochenstunden" />
                <em>h</em>
                <span>Soll: 39h</span>
              </label>
            </div>
            <input type="hidden" name="report_date" value="2025-03-18" />
            <textarea name="activities" hidden>Drehmaschine einrichten, Werkstück spannen, Schnittdaten berechnen und Probedurchlauf durchgeführt. Fräsarbeiten nach Zeichnung Nr. 8.2 ausgeführt. Kanten entgratet und Maße kontrolliert.</textarea>
          </div>
          <div class="bh-ne-actions">
            <button class="bh-ne-draft" type="button" data-action="toast" data-toast="Entwurf gespeichert">Als Entwurf speichern</button>
            <button class="bh-ne-submit" type="submit">Zur Prüfung einreichen</button>
            <p class="feedback" data-feedback hidden></p>
          </div>
        </form>
      </div>
    `,
'''

pat = re.compile(r'  "s08_2-berichtsheft-neuer-eintrag": \(\) => `[\s\S]*?`,\n(?=  ")')
if not pat.search(text):
    raise SystemExit("08.2 screen not found")
text = pat.sub(s082, text)
screens_path.write_text(text, encoding="utf-8")
print("screens.js updated")

css_block = r'''
/* --- 08.2 Berichtsheft Neuer Eintrag --- */
.app-frame[data-chrome="bh"]:has(.bh-ne-screen) { height: 1211px; min-height: 1211px; }
.bh-ne-screen {
  display: flex; flex-direction: column; flex: 1; min-height: 0;
  background: #0b0f19; color: #f8fafc;
}
.bh-ne-form { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.bh-ne-scroll { flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; }
.bh-ne-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 20px 12px; box-sizing: border-box; flex-shrink: 0;
}
.bh-ne-back {
  display: grid; place-items: center; width: 32px; height: 32px; border-radius: 8px;
  background: #161e2d; flex-shrink: 0;
}
.bh-ne-back img { width: 16px; height: 16px; display: block; }
.bh-ne-titles { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 2px; }
.bh-ne-titles h2 { margin: 0; font-size: 18px; font-weight: 700; color: #f8fafc; }
.bh-ne-titles p { margin: 0; font-size: 12px; color: #f59e0b; }
.bh-ne-fields {
  display: flex; flex-direction: column; gap: 12px; padding: 20px; box-sizing: border-box;
}
.bh-ne-field { display: flex; flex-direction: column; gap: 6px; width: 100%; }
.bh-ne-field > span { color: #94a3b8; font-size: 12px; font-weight: 600; }
.bh-ne-select {
  position: relative; display: flex; align-items: center;
  background: #161e2d; border: 1px solid #2e3a52; border-radius: 10px; padding: 14px; box-sizing: border-box;
}
.bh-ne-select select {
  flex: 1; min-width: 0; appearance: none; border: 0; background: transparent;
  color: #f8fafc; font-size: 14px; padding: 0; margin: 0; outline: none;
}
.bh-ne-select img { width: 16px; height: 16px; flex-shrink: 0; pointer-events: none; }
.bh-ne-days {
  display: flex; flex-direction: column; gap: 12px; padding: 0 20px 20px; box-sizing: border-box;
}
.bh-ne-section {
  margin: 0; color: #94a3b8; font-size: 14px; font-weight: 700; text-transform: uppercase;
}
.bh-ne-day {
  display: flex; flex-direction: column; gap: 10px; padding: 14px;
  border-radius: 12px; background: #161e2d; border: 1px solid #2e3a52; box-sizing: border-box;
}
.bh-ne-day-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.bh-ne-day-label { display: flex; align-items: center; gap: 8px; }
.bh-ne-day-label > i {
  display: grid; place-items: center; width: 12px; height: 12px; border-radius: 100px;
  background: #2e3a52; flex-shrink: 0;
}
.bh-ne-day-label > i.ok { background: #10b981; }
.bh-ne-day-label > i.ok::after {
  content: ""; width: 4px; height: 4px; border-radius: 100px; background: #0b0f19;
}
.bh-ne-day-label strong { color: #f8fafc; font-size: 15px; font-weight: 700; }
.bh-ne-day-head > span { color: #64748b; font-size: 11px; }
.bh-ne-day textarea {
  width: 100%; height: 64px; resize: none; box-sizing: border-box;
  padding: 12px; border-radius: 8px; border: 1px solid #2e3a52; background: #1e293b;
  color: #f8fafc; font-size: 13px; line-height: 1.4; outline: none;
}
.bh-ne-day textarea::placeholder { color: #64748b; }
.bh-ne-hours {
  display: flex; align-items: center; justify-content: space-between; gap: 12px;
  padding: 0 20px 24px; box-sizing: border-box;
}
.bh-ne-hours > span { color: #94a3b8; font-size: 14px; font-weight: 600; }
.bh-ne-hours-box {
  display: flex; align-items: center; gap: 8px; padding: 10px 16px;
  border-radius: 8px; background: #161e2d; border: 1px solid #2e3a52; box-sizing: border-box;
}
.bh-ne-hours-box input {
  width: 36px; border: 0; background: transparent; color: #3b82f6;
  font-size: 16px; font-weight: 700; padding: 0; outline: none;
}
.bh-ne-hours-box em { font-style: normal; color: #3b82f6; font-size: 16px; font-weight: 700; margin-left: -6px; }
.bh-ne-hours-box > span { color: #64748b; font-size: 12px; }
.bh-ne-actions {
  display: flex; flex-direction: column; gap: 12px; padding: 20px;
  background: #161e2d; border-top: 1px solid #2e3a52; box-sizing: border-box; flex-shrink: 0;
}
.bh-ne-draft, .bh-ne-submit {
  display: flex; align-items: center; justify-content: center; height: 48px; width: 100%;
  border-radius: 100px; font-size: 14px; cursor: pointer; box-sizing: border-box;
}
.bh-ne-draft {
  background: transparent; border: 1.5px solid #334155; color: #94a3b8; font-weight: 600;
}
.bh-ne-submit {
  background: #3b82f6; border: 0; color: #f8fafc; font-weight: 700;
}
'''

css = css_path.read_text(encoding="utf-8")
marker = "/* --- 08.2 Berichtsheft Neuer Eintrag --- */"
if marker in css:
    start = css.find(marker)
    end = css.find(".bh-ne-submit {\n  background: #3b82f6;", start)
    if end != -1:
        end = css.find("}", end) + 1
        css = css[:start] + css_block.strip() + "\n" + css[end:]
    else:
        css = css[:start] + css_block.strip() + "\n"
else:
    css = css.rstrip() + "\n\n" + css_block.strip() + "\n"
css_path.write_text(css, encoding="utf-8")
print("ui.css updated")
