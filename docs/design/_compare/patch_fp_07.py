# -*- coding: utf-8 -*-
from pathlib import Path

screens_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
css_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\ui.css")

text = screens_path.read_text(encoding="utf-8")

# set chrome fp for 07.2-07.6
for path in [
    '"/fortschritt/pruefungsreife"',
    '"/fortschritt/ausstehend"',
    '"/fortschritt/verlauf"',
    '"/fortschritt/xp"',
    '"/fortschritt/heatmap"',
]:
    # add chrome if missing
    import re
    pat = re.compile(rf'({re.escape(path)}: \{{[^}}]*num: "07\.\d")(\}})')
    def add_chrome(m):
        s = m.group(1)
        if 'chrome:' in s:
            return m.group(0)
        return s + ', chrome: "fp"' + m.group(2)
    text = pat.sub(add_chrome, text)

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

s072 = f'''  "s07_2-pruefungsreife-checkliste": () => `
      <div class="fp-screen fp-pr-screen fp-pr-check" data-node-id="136:9093">
        <div class="fp-pr-scroll">
          <header class="fp-pr-header">
            <a class="fp-pr-icon-btn" href="/fortschritt" data-page-link aria-label="Zurück">
              <img src="/static/figma/fp/fp-pr-back.svg" width="20" height="20" alt="" />
            </a>
            <h2>Prüfungsreife</h2>
            <button class="fp-pr-icon-btn" type="button" aria-label="Mehr">
              <img src="/static/figma/fp/fp-pr-more.svg" width="20" height="20" alt="" />
            </button>
          </header>
          <div class="fp-pr-body">
            <article class="fp-pr-score">
              <div class="fp-pr-ring">
                <img class="fp-pr-ring-track" src="/static/figma/fp/fp-pr-track.svg" width="80" height="80" alt="" />
                <img class="fp-pr-ring-fill" src="/static/figma/fp/fp-pr-progress-orange.svg" width="80" height="80" alt="" />
                <strong>67%</strong>
              </div>
              <div class="fp-pr-score-info">
                <span class="fp-pr-badge warn">Noch nicht prüfungsreif</span>
                <p>Ziel: <strong>80%</strong> für Empfehlung</p>
              </div>
            </article>
            <div class="fp-pr-section">
              <h3>Themen-Checkliste</h3>
              <div class="fp-pr-list">
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Grundlagen Metall</strong><em>100%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:100%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Werkstoffkunde</strong><em>85%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:85%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Arbeitssicherheit</strong><em>92%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:92%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item warn">
                  <img src="/static/figma/fp/fp-pr-alert.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Messtechnik</strong><em>60%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:60%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item warn">
                  <img src="/static/figma/fp/fp-pr-alert.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Pneumatik</strong><em>40%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:40%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item bad">
                  <img src="/static/figma/fp/fp-pr-x.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Hydraulik</strong><em>10%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:10%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item locked">
                  <img src="/static/figma/fp/fp-pr-lock.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Steuerungstechnik</strong><em>0%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:0%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item locked">
                  <img src="/static/figma/fp/fp-pr-lock.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Elektrotechnik</strong><em>0%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:0%"></i></div>
                  </div>
                </article>
              </div>
            </div>
            <a class="fp-pr-cta" href="/lernen" data-page-link>
              <img src="/static/figma/fp/fp-pr-zap.svg" width="18" height="18" alt="" />
              Schwächstes Thema üben
            </a>
          </div>
        </div>
        {tabs}
      </div>
    `,
'''

s073 = f'''  "s07_3-pruefungsreife-ausstehend": () => `
      <div class="fp-screen fp-pr-screen fp-pr-pending" data-node-id="136:9238">
        <div class="fp-pr-scroll">
          <header class="fp-pr-header">
            <a class="fp-pr-icon-btn" href="/fortschritt" data-page-link aria-label="Zurück">
              <img src="/static/figma/fp/fp-pr-back.svg" width="20" height="20" alt="" />
            </a>
            <h2>Prüfungsreife</h2>
            <button class="fp-pr-icon-btn" type="button" aria-label="Mehr">
              <img src="/static/figma/fp/fp-pr-more.svg" width="20" height="20" alt="" />
            </button>
          </header>
          <div class="fp-pr-body">
            <article class="fp-pr-score">
              <div class="fp-pr-ring">
                <img class="fp-pr-ring-track" src="/static/figma/fp/fp-pr-track.svg" width="80" height="80" alt="" />
                <img class="fp-pr-ring-fill" src="/static/figma/fp/fp-pr-progress-green.svg" width="80" height="80" alt="" />
                <strong>82%</strong>
              </div>
              <div class="fp-pr-score-info">
                <span class="fp-pr-badge info">Empfehlung ausstehend</span>
                <p class="plain">Ziel erreicht! Mindestens 80% überall.</p>
              </div>
            </article>
            <article class="fp-pr-trainer">
              <div class="fp-pr-trainer-top">
                <div class="fp-pr-trainer-title">
                  <img src="/static/figma/fp/fp-pr-user-check.svg" width="18" height="18" alt="" />
                  <strong>Ausbilder-Empfehlung</strong>
                </div>
                <img src="/static/figma/fp/fp-pr-dots.svg" width="26" height="6" alt="" />
              </div>
              <div class="fp-pr-trainer-div" aria-hidden="true"></div>
              <div class="fp-pr-trainer-rows">
                <div><span>Status:</span><em class="warn">Warte auf Bestätigung</em></div>
                <div><span>Ausbilder:</span><strong>Hr. Schmidt</strong></div>
                <div><span>Gesendet am:</span><span>15.03.2025</span></div>
              </div>
            </article>
            <p class="fp-pr-hint">Dein Ausbilder muss deine Prüfungsreife bestätigen, bevor du dich zur IHK-Prüfung anmelden kannst.</p>
            <div class="fp-pr-section">
              <h3>Qualifizierte Themen (5)</h3>
              <div class="fp-pr-list">
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Grundlagen Metall</strong><em>100%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:100%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Werkstoffkunde</strong><em>88%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:88%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Arbeitssicherheit</strong><em>95%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:95%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Messtechnik</strong><em>82%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:82%"></i></div>
                  </div>
                </article>
                <article class="fp-pr-item ok">
                  <img src="/static/figma/fp/fp-pr-check.svg" width="20" height="20" alt="" />
                  <div class="fp-pr-item-body">
                    <div class="fp-pr-item-top"><strong>Pneumatik</strong><em>80%</em></div>
                    <div class="fp-pr-item-bar"><i style="width:80%"></i></div>
                  </div>
                </article>
              </div>
            </div>
          </div>
        </div>
        {tabs}
      </div>
    `,
'''

start = text.index('  "s07_2-pruefungsreife-checkliste"')
end = text.index('  "s07_4-statistik-verlauf"')
text = text[:start] + s072 + s073 + text[end:]
screens_path.write_text(text, encoding="utf-8")
print("screens patched")

css = r'''
/* --- 07.2 / 07.3 Prüfungsreife --- */
.app-frame[data-chrome="fp"]:has(.fp-pr-check) { height: 947px; min-height: 947px; }
.app-frame[data-chrome="fp"]:has(.fp-pr-pending) { height: 895px; min-height: 895px; }
.fp-pr-screen { justify-content: space-between; background: #0b0f19; }
.fp-pr-scroll { flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; }
.fp-pr-header {
  display: flex; align-items: center; justify-content: space-between;
  height: 48px; padding: 0 20px; flex-shrink: 0; box-sizing: border-box;
}
.fp-pr-header h2 { margin: 0; color: #f8fafc; font-size: 17px; font-weight: 600; text-align: center; }
.fp-pr-icon-btn {
  display: grid; place-items: center; width: 40px; height: 40px; background: transparent; border: 0; padding: 0; cursor: pointer;
}
.fp-pr-icon-btn img { width: 20px; height: 20px; display: block; }
.fp-pr-body {
  display: flex; flex-direction: column; gap: 18px; padding: 12px 20px 20px; box-sizing: border-box;
}
.fp-pr-score {
  display: flex; align-items: center; gap: 16px; padding: 20px; border-radius: 18px;
  background: #1e293b; box-shadow: 0 8px 8px rgba(0,0,0,0.25); box-sizing: border-box;
}
.fp-pr-ring {
  position: relative; width: 80px; height: 80px; flex-shrink: 0;
  display: grid; place-items: center;
}
.fp-pr-ring-track, .fp-pr-ring-fill {
  position: absolute; inset: 0; width: 80px; height: 80px;
}
.fp-pr-ring strong {
  position: relative; z-index: 1; color: #f8fafc; font-size: 20px; font-weight: 800;
}
.fp-pr-score-info { flex: 1; display: flex; flex-direction: column; gap: 6px; min-width: 0; }
.fp-pr-badge {
  display: inline-flex; align-self: flex-start; padding: 4px 10px; border-radius: 6px;
  font-size: 11px; font-weight: 700; text-transform: uppercase; white-space: nowrap;
}
.fp-pr-badge.warn { background: rgba(249,115,22,0.08); color: #f97316; }
.fp-pr-badge.info { background: rgba(59,130,246,0.08); color: #3b82f6; }
.fp-pr-score-info p { margin: 0; color: #94a3b8; font-size: 13px; }
.fp-pr-score-info p strong { color: #10b981; font-weight: 700; }
.fp-pr-score-info p.plain { color: #94a3b8; }
.fp-pr-section { display: flex; flex-direction: column; gap: 12px; }
.fp-pr-section h3 { margin: 0; color: #f8fafc; font-size: 16px; font-weight: 600; }
.fp-pr-list { display: flex; flex-direction: column; gap: 10px; }
.fp-pr-item {
  display: flex; align-items: center; gap: 12px; padding: 14px; border-radius: 12px;
  background: #1e293b; box-sizing: border-box;
}
.fp-pr-item > img { width: 20px; height: 20px; flex-shrink: 0; display: block; }
.fp-pr-item-body { flex: 1; display: flex; flex-direction: column; gap: 4px; min-width: 0; }
.fp-pr-item-top { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.fp-pr-item-top strong { color: #f8fafc; font-size: 14px; font-weight: 600; }
.fp-pr-item-top em { font-style: normal; font-size: 13px; font-weight: 700; }
.fp-pr-item.ok .fp-pr-item-top em { color: #10b981; }
.fp-pr-item.warn .fp-pr-item-top em { color: #f59e0b; }
.fp-pr-item.bad .fp-pr-item-top em { color: #ef4444; }
.fp-pr-item.locked .fp-pr-item-top strong,
.fp-pr-item.locked .fp-pr-item-top em { color: #64748b; }
.fp-pr-item-bar {
  height: 6px; border-radius: 3px; background: #334155; overflow: hidden; width: 100%;
}
.fp-pr-item-bar > i { display: block; height: 100%; border-radius: 3px; }
.fp-pr-item.ok .fp-pr-item-bar > i { background: #10b981; }
.fp-pr-item.warn .fp-pr-item-bar > i { background: #f59e0b; }
.fp-pr-item.bad .fp-pr-item-bar > i { background: #ef4444; }
.fp-pr-item.locked .fp-pr-item-bar > i { background: #64748b; }
.fp-pr-cta {
  display: flex; align-items: center; justify-content: center; gap: 8px; height: 50px;
  border-radius: 12px; background: #3b82f6; color: #f8fafc; font-size: 15px; font-weight: 700;
  text-decoration: none; box-shadow: 0 8px 8px rgba(0,0,0,0.25); box-sizing: border-box;
}
.fp-pr-cta img { width: 18px; height: 18px; display: block; }
.fp-pr-trainer {
  display: flex; flex-direction: column; gap: 12px; padding: 16px; border-radius: 14px;
  background: rgba(59,130,246,0.06); border: 1px solid #3b82f6; box-sizing: border-box;
}
.fp-pr-trainer-top { display: flex; align-items: center; justify-content: space-between; }
.fp-pr-trainer-title { display: flex; align-items: center; gap: 8px; color: #f8fafc; }
.fp-pr-trainer-title img { width: 18px; height: 18px; }
.fp-pr-trainer-title strong { font-size: 15px; font-weight: 700; }
.fp-pr-trainer-div { height: 1px; width: 100%; background: rgba(59,130,246,0.19); }
.fp-pr-trainer-rows { display: flex; flex-direction: column; gap: 8px; font-size: 13px; }
.fp-pr-trainer-rows > div { display: flex; justify-content: space-between; gap: 12px; }
.fp-pr-trainer-rows span { color: #94a3b8; }
.fp-pr-trainer-rows strong { color: #f8fafc; font-weight: 600; }
.fp-pr-trainer-rows em { font-style: normal; font-weight: 700; }
.fp-pr-trainer-rows em.warn { color: #f59e0b; }
.fp-pr-hint { margin: 0; color: #94a3b8; font-size: 12px; line-height: 1.5; }
.fp-pr-tabs {
  display: flex; align-items: center; justify-content: space-between; height: 64px; padding: 0 24px;
  background: #1e293b; border-top: 1px solid #334155; flex-shrink: 0; box-sizing: border-box;
}
.fp-pr-tabs a {
  width: 50px; display: flex; flex-direction: column; align-items: center; gap: 4px;
  color: #64748b; font-size: 10px; font-weight: 600; text-decoration: none;
}
.fp-pr-tabs a.active { color: #3b82f6; }
.fp-pr-tabs img { width: 20px; height: 20px; display: block; }
.fp-pr-home {
  height: 20px; background: #1e293b; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.fp-pr-home::after {
  content: ""; width: 120px; height: 5px; border-radius: 100px; background: #64748b; display: block;
}
'''

css_text = css_path.read_text(encoding="utf-8")
marker = "/* --- 07.2 / 07.3 Prüfungsreife --- */"
if marker in css_text:
    css_text = css_text[: css_text.index(marker)]
css_path.write_text(css_text.rstrip() + "\n" + css + "\n", encoding="utf-8")
print("css patched")

# verify chrome
for line in screens_path.read_text(encoding="utf-8").splitlines():
    if "/fortschritt/" in line and "07." in line:
        print(line.strip())
