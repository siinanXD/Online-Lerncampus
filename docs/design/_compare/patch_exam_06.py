# -*- coding: utf-8 -*-
from pathlib import Path

screens_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
css_path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\ui.css")

# --- build 06.3 grid ---
cells = []
for i in range(1, 46):
    if i <= 8:
        cls = "ex-ov-cell answered"
    elif i == 9:
        cls = "ex-ov-cell current"
    else:
        cls = "ex-ov-cell open"
    marked = i in (3, 6)
    if marked:
        cls += " marked"
    dot = '<i aria-hidden="true"></i>' if marked else ""
    cells.append(
        f'<a class="{cls}" href="/pruefungen/frage" data-page-link>{i}{dot}</a>'
    )
grid_html = "\n            ".join(cells)

# --- calendar days for 06.9 ---
# March 2025 starts Saturday: empty Mon-Fri, then 1-31
# Row0: empty x5, 1, 2
# Row1: 3(selected), 4-9
# Row2: 10-16 (15 has blue dot)
# Row3: 17-23
# Row4: 24-30 (28 has orange dot)
# Row5: 31 + empty x6

def day_cell(n, special=""):
    if n is None:
        return '<span class="ex-cal-empty" aria-hidden="true"></span>'
    cls = "ex-cal-day"
    extra = ""
    if special == "sel":
        cls += " selected"
    elif special == "dot-b":
        cls += " has-dot"
        extra = '<img class="ex-cal-dot" src="/static/figma/exam/ex-cal-dot-b.svg" width="4" height="4" alt="" />'
    elif special == "dot-o":
        cls += " has-dot"
        extra = '<img class="ex-cal-dot" src="/static/figma/exam/ex-cal-dot-o.svg" width="4" height="4" alt="" />'
    return f'<button type="button" class="{cls}">{n}{extra}</button>'

cal_days = []
# row 0
row0 = [None, None, None, None, None, 1, 2]
# row 1
row1 = [(3, "sel"), 4, 5, 6, 7, 8, 9]
# row 2
row2 = [10, 11, 12, 13, 14, (15, "dot-b"), 16]
# row 3
row3 = [17, 18, 19, 20, 21, 22, 23]
# row 4
row4 = [24, 25, 26, 27, (28, "dot-o"), 29, 30]
# row 5
row5 = [31, None, None, None, None, None, None]

def render_row(row):
    parts = []
    for d in row:
        if d is None:
            parts.append(day_cell(None))
        elif isinstance(d, tuple):
            parts.append(day_cell(d[0], d[1]))
        else:
            parts.append(day_cell(d))
    return "\n              ".join(parts)

cal_rows = "\n            ".join(
    f'<div class="ex-cal-row">\n              {render_row(r)}\n            </div>'
    for r in (row0, row1, row2, row3, row4, row5)
)

result_tabs = lambda active: f"""
        <nav class="ex-rs-tabs" aria-label="Ergebnis Navigation">
          <a href="/lernen" data-page-link class="{'active' if active=='learn' else ''}">
            <img src="/static/figma/exam/ex-rs-tab-book.svg" width="22" height="22" alt="" />
            Lernen
          </a>
          <a href="/pruefungen/bestanden" data-page-link class="{'active' if active=='results' else ''}">
            <img src="/static/figma/exam/ex-rs-tab-award.svg" width="22" height="22" alt="" />
            Ergebnisse
          </a>
          <a href="/pruefungen/kammertermine" data-page-link class="{'active' if active=='cal' else ''}">
            <img src="/static/figma/exam/ex-rs-tab-cal.svg" width="22" height="22" alt="" />
            Kalender
          </a>
          <a href="/mehr" data-page-link class="{'active' if active=='profile' else ''}">
            <img src="/static/figma/exam/ex-rs-tab-user.svg" width="22" height="22" alt="" />
            Profil
          </a>
        </nav>
        <div class="ex-rs-home" aria-hidden="true"></div>"""

# For 06.8 active=learn, 06.9 active=cal — use matching colored icons
tabs_068 = """
        <nav class="ex-rs-tabs" aria-label="Ergebnis Navigation">
          <a href="/lernen" data-page-link class="active">
            <img src="/static/figma/exam/ex-wk-tab-book.svg" width="22" height="22" alt="" />
            Lernen
          </a>
          <a href="/pruefungen/bestanden" data-page-link>
            <img src="/static/figma/exam/ex-wk-tab-award.svg" width="22" height="22" alt="" />
            Ergebnisse
          </a>
          <a href="/pruefungen/kammertermine" data-page-link>
            <img src="/static/figma/exam/ex-wk-tab-cal.svg" width="22" height="22" alt="" />
            Kalender
          </a>
          <a href="/mehr" data-page-link>
            <img src="/static/figma/exam/ex-wk-tab-user.svg" width="22" height="22" alt="" />
            Profil
          </a>
        </nav>
        <div class="ex-rs-home" aria-hidden="true"></div>"""

tabs_069 = """
        <nav class="ex-rs-tabs" aria-label="Ergebnis Navigation">
          <a href="/lernen" data-page-link>
            <img src="/static/figma/exam/ex-cal-tab-book.svg" width="22" height="22" alt="" />
            Lernen
          </a>
          <a href="/pruefungen/bestanden" data-page-link>
            <img src="/static/figma/exam/ex-cal-tab-award.svg" width="22" height="22" alt="" />
            Ergebnisse
          </a>
          <a href="/pruefungen/kammertermine" data-page-link class="active">
            <img src="/static/figma/exam/ex-cal-tab-cal.svg" width="22" height="22" alt="" />
            Kalender
          </a>
          <a href="/mehr" data-page-link>
            <img src="/static/figma/exam/ex-cal-tab-user.svg" width="22" height="22" alt="" />
            Profil
          </a>
        </nav>
        <div class="ex-rs-home" aria-hidden="true"></div>"""

new_screens = f'''  "s06_3-pruefung-uebersicht": () => `
      <div class="ex-screen ex-ov-screen" data-node-id="136:8178">
        <div class="ex-ov-top">
          <header class="ex-ov-header">
            <a class="ex-ov-close" href="/pruefungen/frage" data-page-link aria-label="Schließen">
              <img src="/static/figma/exam/ex-ov-close.svg" width="20" height="20" alt="" />
            </a>
            <h2>Übersicht</h2>
            <div class="ex-ov-timer">
              <img src="/static/figma/exam/ex-ov-alarm.svg" width="16" height="16" alt="" />
              <strong>47:23</strong>
            </div>
          </header>
          <div class="ex-ov-body">
            <div class="ex-ov-grid">
            {grid_html}
            </div>
            <div class="ex-ov-divider" aria-hidden="true"></div>
            <div class="ex-ov-stats">
              <div><span>Beantwortet:</span><strong class="blue">8</strong></div>
              <div><span>Markiert:</span><strong class="orange">2</strong></div>
              <div><span>Offen:</span><strong>37</strong></div>
            </div>
            <div class="ex-ov-legend">
              <div><i class="lg-answered"></i>Beantwortet</div>
              <div><i class="lg-current"></i>Aktuell</div>
              <div><i class="lg-marked"></i>Markiert</div>
              <div><i class="lg-open"></i>Unbeantwortet</div>
            </div>
          </div>
        </div>
        <footer class="ex-ov-footer">
          <a class="ex-ov-primary" href="/pruefungen/frage" data-page-link>Zur aktuellen Frage</a>
          <a class="ex-ov-secondary" href="/pruefungen/abgabe" data-page-link>Prüfung abgeben</a>
          <div class="ex-home-indicator" aria-hidden="true"></div>
        </footer>
      </div>
    `,
  "s06_4-pruefung-timer": () => `
      <div class="ex-screen ex-tm-screen" data-node-id="136:8326">
        <div class="ex-tm-top">
          <header class="ex-tm-header">
            <a class="ex-tm-close" href="/pruefungen" data-page-link aria-label="Schließen">
              <img src="/static/figma/exam/ex-tm-close.svg" width="20" height="20" alt="" />
            </a>
            <div class="ex-tm-timer">
              <img src="/static/figma/exam/ex-tm-timer.svg" width="18" height="18" alt="" />
              <strong>09:42</strong>
            </div>
            <span class="ex-tm-progress">38/45</span>
          </header>
          <div class="ex-tm-warn">
            <img src="/static/figma/exam/ex-tm-alert.svg" width="18" height="18" alt="" />
            <p>Weniger als 10 Minuten verbleibend!</p>
          </div>
          <div class="ex-tm-body">
            <article class="ex-tm-card">
              <div class="ex-tm-meta">
                <span>Frage 38</span>
                <em>Maschinensicherheit</em>
              </div>
              <p>Welche Verhaltensregel verhindert Unfälle an Antrieben besonders wirksam?</p>
            </article>
            <a class="ex-tm-jump" href="/pruefungen/uebersicht" data-page-link>
              <img src="/static/figma/exam/ex-tm-flag-off.svg" width="16" height="16" alt="" />
              <span><em>Markiert:</em> <strong>#3, #6, #22</strong> — Zur Frage springen</span>
              <img class="ex-tm-jump-x" src="/static/figma/exam/ex-tm-dismiss.svg" width="14" height="14" alt="" />
            </a>
            <div class="ex-tm-options">
              <button type="button" class="ex-tm-opt"><span>A</span><strong>Schutzabdeckung entfernen</strong></button>
              <button type="button" class="ex-tm-opt"><span>B</span><strong>Sicherheitsschalter überbrücken</strong></button>
              <button type="button" class="ex-tm-opt"><span>C</span><strong>Haarnetz tragen bei langen Haaren</strong></button>
              <button type="button" class="ex-tm-opt"><span>D</span><strong>Eng anliegende Kleidung tragen</strong></button>
            </div>
          </div>
        </div>
        <footer class="ex-tm-footer">
          <div class="ex-tm-nav">
            <a class="ex-tm-back" href="/pruefungen/frage" data-page-link>Zurück</a>
            <button class="ex-tm-flag" type="button" aria-label="Markiert">
              <img src="/static/figma/exam/ex-tm-flag.svg" width="18" height="18" alt="" />
            </button>
            <a class="ex-tm-next" href="/pruefungen/uebersicht" data-page-link>Weiter</a>
          </div>
          <div class="ex-home-indicator" aria-hidden="true"></div>
        </footer>
      </div>
    `,
  "s06_5-abgabe-bestaetigung": () => `
      <div class="ex-screen ex-dark ex-ab-screen" data-node-id="136:8398">
        <div class="ex-ab-bg" aria-hidden="true">
          <div class="ex-ab-bg-head">
            <span>Abschlussprüfung Teil 1</span>
            <em>45:12 Min</em>
          </div>
          <div class="ex-ab-bg-bar"><i></i></div>
          <div class="ex-ab-bg-card">
            <strong>Frage 38 von 45</strong>
            <p>Erklären Sie den Unterschied zwischen einer SPS und einer festverdrahteten Steuerung...</p>
          </div>
        </div>
        <div class="ex-ab-overlay">
          <div class="ex-ab-modal" role="dialog" aria-modal="true" aria-labelledby="ex-ab-title">
            <div class="ex-ab-icon">
              <img src="/static/figma/exam/ex-ab-alert.svg" width="40" height="40" alt="" />
            </div>
            <div class="ex-ab-text">
              <h2 id="ex-ab-title">Prüfung abgeben?</h2>
              <p>Möchtest du deine Antworten wirklich einreichen und die Prüfung beenden?</p>
            </div>
            <div class="ex-ab-summary">
              <div><span>Beantwortet:</span><strong class="ok">38 Fragen</strong></div>
              <div><span>Offen (unbeantwortet):</span><strong class="bad">7 Fragen</strong></div>
              <div><span>Markiert:</span><strong class="warn">2 Fragen</strong></div>
            </div>
            <div class="ex-ab-callout">
              <img src="/static/figma/exam/ex-ab-info.svg" width="18" height="18" alt="" />
              <p>Offene Fragen werden als falsch gewertet.</p>
            </div>
            <div class="ex-ab-actions">
              <a class="ex-ab-primary" href="/pruefungen/bestanden" data-page-link>Prüfung abgeben</a>
              <a class="ex-ab-secondary" href="/pruefungen/uebersicht" data-page-link>Zurück zur Prüfung</a>
            </div>
          </div>
        </div>
      </div>
    `,
  "s06_6-ergebnis-bestanden": () => `
      <div class="ex-screen ex-dark ex-rs-screen ex-rs-pass" data-node-id="136:8446">
        <div class="ex-rs-scroll">
          <header class="ex-rs-header">
            <h2>Prüfungsergebnis</h2>
            <span class="ex-rs-xp"><img src="/static/figma/exam/ex-rs-star.svg" width="14" height="14" alt="" />1.450 XP</span>
          </header>
          <div class="ex-rs-hero">
            <span class="ex-rs-spark s1" aria-hidden="true"></span>
            <span class="ex-rs-spark s2" aria-hidden="true"></span>
            <span class="ex-rs-spark s3" aria-hidden="true"></span>
            <span class="ex-rs-spark s4" aria-hidden="true"></span>
            <span class="ex-rs-spark s5" aria-hidden="true"></span>
            <div class="ex-rs-burst">
              <img src="/static/figma/exam/ex-rs-check.svg" width="48" height="48" alt="" />
            </div>
          </div>
          <div class="ex-rs-headline">
            <h3>Bestanden!</h3>
            <p>Hervorragende Leistung!</p>
          </div>
          <article class="ex-rs-grade">
            <div class="ex-rs-grade-main">
              <span>Deine Bewertung</span>
              <div class="ex-rs-note"><strong>Note 2</strong><em>Gut</em></div>
              <p>78% (35/45 richtig)</p>
            </div>
            <div class="ex-rs-xp-glow">
              <strong>+200 XP</strong>
              <span>Erhalten</span>
            </div>
          </article>
          <article class="ex-rs-stats">
            <h4>Statistik</h4>
            <div class="ex-rs-stat-row"><span><img src="/static/figma/exam/ex-rs-dot-g.svg" width="10" height="10" alt="" />Richtig beantwortet</span><strong>35 Fragen</strong></div>
            <div class="ex-rs-stat-row"><span><img src="/static/figma/exam/ex-rs-dot-r.svg" width="10" height="10" alt="" />Falsch beantwortet</span><strong>8 Fragen</strong></div>
            <div class="ex-rs-stat-row"><span><img src="/static/figma/exam/ex-rs-dot-s.svg" width="10" height="10" alt="" />Offen gelassen</span><strong>2 Fragen</strong></div>
            <div class="ex-rs-stat-row"><span><img src="/static/figma/exam/ex-rs-clock.svg" width="16" height="16" alt="" />Benötigte Zeit</span><strong>52:18 Min</strong></div>
            <div class="ex-rs-divider" aria-hidden="true"></div>
            <div class="ex-rs-record"><img src="/static/figma/exam/ex-rs-record.svg" width="16" height="16" alt="" />Neuer persönlicher Rekord!</div>
          </article>
          <div class="ex-rs-actions">
            <a class="ex-rs-primary" href="/pruefungen/schwach" data-page-link>Auswertung ansehen</a>
            <a class="ex-rs-ghost" href="/dashboard" data-page-link>Zum Dashboard</a>
          </div>
        </div>
        {result_tabs("results")}
      </div>
    `,
  "s06_7-ergebnis-durchgefallen": () => `
      <div class="ex-screen ex-dark ex-rs-screen ex-rs-fail" data-node-id="136:8542">
        <div class="ex-rs-scroll">
          <header class="ex-rs-header">
            <h2>Prüfungsergebnis</h2>
            <span class="ex-rs-xp"><img src="/static/figma/exam/ex-rs-star.svg" width="14" height="14" alt="" />1.450 XP</span>
          </header>
          <div class="ex-rs-hero fail">
            <div class="ex-rs-burst fail">
              <img src="/static/figma/exam/ex-fl-x.svg" width="44" height="44" alt="" />
            </div>
          </div>
          <div class="ex-rs-headline fail">
            <h3>Nicht bestanden</h3>
            <p>Das war knapp! Kopf hoch.</p>
          </div>
          <article class="ex-rs-grade">
            <div class="ex-rs-grade-main">
              <span>Deine Bewertung</span>
              <div class="ex-rs-note"><strong>Note 5</strong><em class="bad">Mangelhaft</em></div>
              <p class="bad">42% (19/45 richtig)</p>
            </div>
            <div class="ex-rs-xp-soft">
              <strong>+50 XP</strong>
              <span>Teilnahme</span>
            </div>
          </article>
          <article class="ex-rs-encourage">
            <div class="ex-rs-encourage-title">
              <img src="/static/figma/exam/ex-fl-book.svg" width="20" height="20" alt="" />
              <strong>Nicht aufgeben!</strong>
            </div>
            <p>Wiederhole deine Schwachstellen in Steuerungstechnik und lade dein Wissen vor dem nächsten Versuch auf.</p>
            <a class="ex-rs-encourage-btn" href="/pruefungen/schwach" data-page-link>Schwache Themen ansehen</a>
          </article>
          <div class="ex-rs-mini">
            <div><span>Richtig</span><strong class="ok">19</strong></div>
            <div><span>Falsch</span><strong class="bad">23</strong></div>
            <div><span>Offen</span><strong>3</strong></div>
          </div>
          <div class="ex-rs-actions">
            <a class="ex-rs-primary" href="/pruefungen/schwach" data-page-link>Auswertung</a>
            <a class="ex-rs-ghost" href="/pruefungen" data-page-link>Nochmal versuchen</a>
          </div>
        </div>
        {result_tabs("results")}
      </div>
    `,
  "s06_8-schwache-themen": () => `
      <div class="ex-screen ex-dark ex-wk-screen" data-node-id="136:8622">
        <div class="ex-wk-scroll">
          <header class="ex-wk-header">
            <a class="ex-wk-back" href="/pruefungen/durchgefallen" data-page-link aria-label="Zurück">
              <img src="/static/figma/exam/ex-wk-back.svg" width="18" height="18" alt="" />
            </a>
            <h2>Schwache Themen</h2>
            <span class="ex-rs-xp"><img src="/static/figma/exam/ex-wk-star.svg" width="14" height="14" alt="" />1.450 XP</span>
          </header>
          <p class="ex-wk-sub">Basierend auf deiner letzten Prüfung:</p>
          <div class="ex-wk-list">
            <article class="ex-wk-card critical">
              <div class="ex-wk-top"><div class="ex-wk-title"><em>1.</em><strong>Steuerungstechnik</strong></div><span class="ex-wk-badge">Kritisch</span></div>
              <div class="ex-wk-bar"><i style="width:25%"></i><span>2/8 (25%)</span></div>
              <p>Empfehlung: Kapitel 7 wiederholen</p>
              <div class="ex-wk-actions"><a href="/lernen" data-page-link>Thema üben</a><img src="/static/figma/exam/ex-wk-chev.svg" width="16" height="16" alt="" /></div>
            </article>
            <article class="ex-wk-card weak">
              <div class="ex-wk-top"><div class="ex-wk-title"><em>2.</em><strong>Hydraulik</strong></div><span class="ex-wk-badge">Schwach</span></div>
              <div class="ex-wk-bar"><i style="width:43%"></i><span>3/7 (43%)</span></div>
              <p>Empfehlung: Formeln wiederholen</p>
              <div class="ex-wk-actions"><a href="/lernen" data-page-link>Thema üben</a><img src="/static/figma/exam/ex-wk-chev.svg" width="16" height="16" alt="" /></div>
            </article>
            <article class="ex-wk-card fair">
              <div class="ex-wk-top"><div class="ex-wk-title"><em>3.</em><strong>Elektrotechnik</strong></div><span class="ex-wk-badge">Ausbaufähig</span></div>
              <div class="ex-wk-bar"><i style="width:50%"></i><span>4/8 (50%)</span></div>
              <div class="ex-wk-actions"><a href="/lernen" data-page-link>Thema üben</a><img src="/static/figma/exam/ex-wk-chev.svg" width="16" height="16" alt="" /></div>
            </article>
            <article class="ex-wk-card ok">
              <div class="ex-wk-top"><div class="ex-wk-title"><em>4.</em><strong>Pneumatik</strong></div><span class="ex-wk-badge">OK</span></div>
              <div class="ex-wk-bar"><i style="width:71%"></i><span>5/7 (71%)</span></div>
            </article>
            <article class="ex-wk-card perfect">
              <div class="ex-wk-top"><div class="ex-wk-title"><em>5.</em><strong>Arbeitssicherheit</strong></div><span class="ex-wk-badge">Perfekt</span></div>
              <div class="ex-wk-bar"><i style="width:100%"></i><span>6/6 (100%)</span></div>
            </article>
          </div>
          <div class="ex-wk-bottom">
            <a class="ex-rs-primary" href="/lernen" data-page-link>Alle schwachen Themen üben</a>
          </div>
        </div>
        {tabs_068}
      </div>
    `,
  "s06_9-kammertermine": () => `
      <div class="ex-screen ex-dark ex-cal-screen" data-node-id="136:8741">
        <div class="ex-cal-scroll">
          <header class="ex-wk-header">
            <a class="ex-wk-back" href="/pruefungen" data-page-link aria-label="Zurück">
              <img src="/static/figma/exam/ex-cal-back.svg" width="18" height="18" alt="" />
            </a>
            <h2>Prüfungstermine</h2>
            <span class="ex-rs-xp"><img src="/static/figma/exam/ex-cal-star.svg" width="14" height="14" alt="" />1.450 XP</span>
          </header>
          <div class="ex-cal-wrap">
            <div class="ex-cal-card">
              <div class="ex-cal-month">
                <strong>März 2025</strong>
                <div class="ex-cal-arrows">
                  <button type="button" aria-label="Vorheriger Monat"><img src="/static/figma/exam/ex-cal-left.svg" width="16" height="16" alt="" /></button>
                  <button type="button" aria-label="Nächster Monat"><img src="/static/figma/exam/ex-cal-right.svg" width="16" height="16" alt="" /></button>
                </div>
              </div>
              <div class="ex-cal-weekdays"><span>M</span><span>D</span><span>M</span><span>D</span><span>F</span><span>S</span><span>S</span></div>
              <div class="ex-cal-grid">
            {cal_rows}
              </div>
            </div>
          </div>
          <div class="ex-cal-upcoming">
            <h3>Anstehende Termine</h3>
            <article class="ex-cal-event">
              <div class="ex-cal-event-top">
                <div>
                  <strong>Zwischenprüfung IHK</strong>
                  <p>Samstag, 15. März 2025</p>
                </div>
                <span class="ex-cal-pill blue">In 12 Tagen</span>
              </div>
              <div class="ex-cal-event-div" aria-hidden="true"></div>
              <div class="ex-cal-loc"><img src="/static/figma/exam/ex-cal-pin.svg" width="14" height="14" alt="" />IHK Düsseldorf, Raum 3.12</div>
              <div class="ex-cal-ready">
                <div class="ex-cal-ready-lab"><span>Prüfungsreife:</span><strong>67%</strong></div>
                <div class="ex-cal-ready-bar"><i style="width:67%"></i></div>
              </div>
              <div class="ex-cal-warn"><img src="/static/figma/exam/ex-cal-alert.svg" width="16" height="16" alt="" />Noch nicht prüfungsreif!</div>
            </article>
            <article class="ex-cal-event">
              <div class="ex-cal-event-top">
                <div>
                  <strong>Anmeldeschluss AP Teil 1</strong>
                  <p>Freitag, 28. März 2025</p>
                </div>
                <span class="ex-cal-pill gold">Frist</span>
              </div>
              <div class="ex-cal-event-div" aria-hidden="true"></div>
              <div class="ex-cal-status"><img src="/static/figma/exam/ex-cal-check.svg" width="14" height="14" alt="" />Status: Angemeldet ✓</div>
            </article>
          </div>
          <div class="ex-cal-link">
            <a href="https://www.ihk.de" target="_blank" rel="noopener">Zur IHK-Anmeldung</a>
          </div>
        </div>
        {tabs_069}
      </div>
    `,
'''

text = screens_path.read_text(encoding="utf-8")
start = text.index('  "s06_3-pruefung-uebersicht"')
end = text.index('  "s07_1-fortschritt-uebersicht"')
text = text[:start] + new_screens + text[end:]
screens_path.write_text(text, encoding="utf-8")
print("screens.js patched", len(new_screens))

css = r'''
/* --- 06.3 Übersicht / 06.4 Timer / 06.5–06.9 Results --- */
.app-frame[data-chrome="exam"]:has(.ex-ov-screen),
.app-frame[data-chrome="exam"]:has(.ex-tm-screen),
.app-frame[data-chrome="exam"]:has(.ex-ab-screen) { height: 844px; min-height: 844px; }
.app-frame[data-chrome="exam"]:has(.ex-rs-pass) { height: 958px; min-height: 958px; }
.app-frame[data-chrome="exam"]:has(.ex-rs-fail) { height: 961px; min-height: 961px; }
.app-frame[data-chrome="exam"]:has(.ex-wk-screen) { height: 967px; min-height: 967px; }
.app-frame[data-chrome="exam"]:has(.ex-cal-screen) { height: 928px; min-height: 928px; }

.app-frame[data-chrome="exam"]:has(.ex-dark) { background: #0f172a; }
.app-frame[data-chrome="exam"]:has(.ex-dark) .app-status { color: #f8fafc; }
.app-frame[data-chrome="exam"]:has(.ex-dark) .login-status-icon { filter: brightness(0) invert(1); }
.app-frame[data-chrome="exam"]:has(.ex-dark) .app-content { background: #0f172a; }

.ex-ov-screen { justify-content: space-between; }
.ex-ov-top { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.ex-ov-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 24px; background: #fff; border-bottom: 1px solid #e2e8f0; flex-shrink: 0;
}
.ex-ov-header h2 { margin: 0; color: #0f172a; font-size: 18px; font-weight: 800; }
.ex-ov-close { display: inline-grid; place-items: center; width: 20px; height: 20px; }
.ex-ov-close img { width: 20px; height: 20px; display: block; }
.ex-ov-timer { display: flex; align-items: center; gap: 6px; }
.ex-ov-timer img { width: 16px; height: 16px; display: block; }
.ex-ov-timer strong { color: #2563eb; font-size: 14px; font-weight: 800; }
.ex-ov-body {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 20px; padding: 20px; box-sizing: border-box;
}
.ex-ov-grid {
  display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; align-content: flex-start;
}
.ex-ov-cell {
  position: relative; display: grid; place-items: center; width: 34px; height: 34px; border-radius: 17px;
  text-decoration: none; font-size: 13px; box-sizing: border-box;
}
.ex-ov-cell.answered { background: #2563eb; border: 1px solid #2563eb; color: #fff; font-weight: 700; }
.ex-ov-cell.current { background: #eff6ff; border: 1px solid #2563eb; color: #2563eb; font-weight: 700; }
.ex-ov-cell.open { background: #fff; border: 1px solid #e2e8f0; color: #94a3b8; font-weight: 500; }
.ex-ov-cell.marked > i {
  position: absolute; top: -3px; right: -3px; width: 10px; height: 10px; border-radius: 5px;
  background: #ea580c; border: 1px solid #fff; display: block;
}
.ex-ov-divider { height: 1px; background: #e2e8f0; width: 100%; }
.ex-ov-stats {
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 12px; border-radius: 12px; background: #f1f5f9; font-size: 13px; white-space: nowrap;
}
.ex-ov-stats div { display: flex; align-items: center; gap: 4px; }
.ex-ov-stats span { color: #475569; font-weight: 600; }
.ex-ov-stats strong { color: #0f172a; font-weight: 700; }
.ex-ov-stats strong.blue { color: #2563eb; }
.ex-ov-stats strong.orange { color: #ea580c; }
.ex-ov-legend {
  display: flex; flex-wrap: wrap; gap: 12px; justify-content: center; align-items: center;
}
.ex-ov-legend > div {
  display: flex; align-items: center; gap: 6px; color: #475569; font-size: 12px; font-weight: 400;
}
.ex-ov-legend i {
  width: 12px; height: 12px; border-radius: 6px; display: block; box-sizing: border-box;
}
.ex-ov-legend .lg-answered { background: #2563eb; }
.ex-ov-legend .lg-current { background: #eff6ff; border: 1px solid #2563eb; }
.ex-ov-legend .lg-marked { background: #ea580c; }
.ex-ov-legend .lg-open { background: transparent; border: 1px solid #e2e8f0; }
.ex-ov-footer {
  background: #fff; border-top: 1px solid #e2e8f0; padding: 24px 24px 0; flex-shrink: 0;
  display: flex; flex-direction: column; gap: 12px; position: relative;
}
.ex-ov-primary, .ex-ov-secondary {
  display: flex; align-items: center; justify-content: center; height: 48px; border-radius: 100px;
  font-size: 15px; font-weight: 700; text-decoration: none; box-sizing: border-box;
}
.ex-ov-primary { background: #2563eb; color: #fff; }
.ex-ov-secondary { border: 1px solid #e2e8f0; color: #475569; }
.ex-ov-footer .ex-home-indicator { padding-bottom: 8px; }

/* 06.4 Timer */
.ex-tm-screen { justify-content: space-between; }
.ex-tm-top { display: flex; flex-direction: column; flex: 1; min-height: 0; }
.ex-tm-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 24px; background: #fff; border-bottom: 2px solid #ea580c; flex-shrink: 0;
}
.ex-tm-close { display: inline-grid; place-items: center; width: 20px; height: 20px; }
.ex-tm-close img { width: 20px; height: 20px; display: block; }
.ex-tm-timer {
  display: flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 8px; background: #fff7ed;
}
.ex-tm-timer img { width: 18px; height: 18px; display: block; }
.ex-tm-timer strong { color: #ea580c; font-size: 18px; font-weight: 800; }
.ex-tm-progress {
  padding: 4px 10px; border-radius: 6px; background: #f1f5f9; color: #0f172a; font-size: 13px; font-weight: 700;
}
.ex-tm-warn {
  display: flex; align-items: center; gap: 10px; padding: 12px 24px; background: #ea580c; flex-shrink: 0;
}
.ex-tm-warn img { width: 18px; height: 18px; display: block; flex-shrink: 0; }
.ex-tm-warn p { margin: 0; color: #fff; font-size: 13px; font-weight: 700; }
.ex-tm-body {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; gap: 16px; padding: 20px; box-sizing: border-box;
}
.ex-tm-card {
  display: flex; flex-direction: column; gap: 10px; padding: 18px; border-radius: 16px;
  background: #fff; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(15,23,42,0.03); box-sizing: border-box;
}
.ex-tm-meta { display: flex; align-items: center; justify-content: space-between; }
.ex-tm-meta > span { color: #2563eb; font-size: 13px; font-weight: 700; }
.ex-tm-meta em {
  font-style: normal; padding: 4px 8px; border-radius: 6px; background: #f5f3ff; color: #7c3aed; font-size: 11px; font-weight: 700;
}
.ex-tm-card > p { margin: 0; color: #0f172a; font-size: 14px; font-weight: 600; line-height: 1.5; }
.ex-tm-jump {
  display: flex; align-items: center; gap: 8px; padding: 12px; border-radius: 12px;
  background: #fefbf0; border: 1px solid #f59e0b; text-decoration: none; box-sizing: border-box;
}
.ex-tm-jump > img:first-child { width: 16px; height: 16px; flex-shrink: 0; }
.ex-tm-jump span { flex: 1; color: #475569; font-size: 12px; font-weight: 600; }
.ex-tm-jump span em { font-style: normal; }
.ex-tm-jump span strong { color: #0f172a; font-weight: 700; }
.ex-tm-jump-x { width: 14px; height: 14px; flex-shrink: 0; }
.ex-tm-options { display: flex; flex-direction: column; gap: 8px; }
.ex-tm-opt {
  display: flex; align-items: center; gap: 12px; padding: 12px; border-radius: 10px;
  background: #fff; border: 1px solid #e2e8f0; cursor: pointer; text-align: left; box-sizing: border-box;
}
.ex-tm-opt span {
  display: grid; place-items: center; width: 20px; height: 20px; border-radius: 4px;
  background: #f1f5f9; color: #475569; font-size: 11px; font-weight: 700; flex-shrink: 0;
}
.ex-tm-opt strong { color: #0f172a; font-size: 13px; font-weight: 500; }
.ex-tm-footer {
  background: #fff; border-top: 1px solid #e2e8f0; padding: 24px 24px 0; flex-shrink: 0; position: relative;
}
.ex-tm-nav { display: flex; align-items: center; justify-content: space-between; padding-bottom: 24px; }
.ex-tm-back { padding: 12px 16px; color: #475569; font-size: 14px; font-weight: 600; text-decoration: none; }
.ex-tm-flag {
  display: grid; place-items: center; width: 44px; height: 44px; border-radius: 22px; background: #ea580c; border: 0; cursor: pointer;
}
.ex-tm-flag img { width: 18px; height: 18px; display: block; }
.ex-tm-next {
  padding: 12px 24px; border-radius: 100px; background: #2563eb; color: #fff;
  font-size: 14px; font-weight: 700; text-decoration: none;
}
.ex-tm-footer .ex-home-indicator { padding-bottom: 8px; }

/* 06.5 Abgabe */
.ex-ab-screen { position: relative; background: #0f172a; color: #f8fafc; overflow: hidden; }
.ex-ab-bg { display: flex; flex-direction: column; gap: 20px; padding: 20px; opacity: 0.3; }
.ex-ab-bg-head { display: flex; align-items: center; justify-content: space-between; }
.ex-ab-bg-head span { color: #f8fafc; font-size: 16px; font-weight: 600; }
.ex-ab-bg-head em { font-style: normal; color: #ef4444; font-size: 14px; }
.ex-ab-bg-bar { height: 8px; border-radius: 4px; background: #334155; overflow: hidden; }
.ex-ab-bg-bar i { display: block; height: 100%; width: 84%; border-radius: 4px; background: #3b82f6; }
.ex-ab-bg-card {
  display: flex; flex-direction: column; gap: 12px; padding: 16px; border-radius: 12px; background: #1e293b;
}
.ex-ab-bg-card strong { color: #f8fafc; font-size: 16px; font-weight: 600; }
.ex-ab-bg-card p { margin: 0; color: #94a3b8; font-size: 14px; }
.ex-ab-overlay {
  position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
  padding: 24px; background: rgba(0,0,0,0.63); box-sizing: border-box;
}
.ex-ab-modal {
  width: 100%; display: flex; flex-direction: column; gap: 24px; padding: 24px; border-radius: 24px;
  background: #1e293b; border: 1px solid #334155; box-shadow: 0 10px 12px rgba(0,0,0,0.25); box-sizing: border-box;
}
.ex-ab-icon {
  width: 80px; height: 80px; border-radius: 40px; background: rgba(245,158,11,0.1);
  display: grid; place-items: center;
}
.ex-ab-icon img { width: 40px; height: 40px; display: block; }
.ex-ab-text { text-align: center; display: flex; flex-direction: column; gap: 8px; }
.ex-ab-text h2 { margin: 0; color: #f8fafc; font-size: 22px; font-weight: 700; }
.ex-ab-text p { margin: 0; color: #94a3b8; font-size: 15px; }
.ex-ab-summary {
  display: flex; flex-direction: column; gap: 10px; padding: 16px; border-radius: 12px; background: #0f172a; font-size: 14px;
}
.ex-ab-summary div { display: flex; justify-content: space-between; }
.ex-ab-summary span { color: #94a3b8; }
.ex-ab-summary strong { font-weight: 700; }
.ex-ab-summary .ok { color: #10b981; }
.ex-ab-summary .bad { color: #ef4444; }
.ex-ab-summary .warn { color: #f59e0b; }
.ex-ab-callout {
  display: flex; align-items: center; gap: 10px; padding: 12px; border-radius: 8px; background: rgba(239,68,68,0.1);
}
.ex-ab-callout img { width: 18px; height: 18px; flex-shrink: 0; }
.ex-ab-callout p { margin: 0; color: #ef4444; font-size: 12px; font-weight: 500; }
.ex-ab-actions { display: flex; flex-direction: column; gap: 10px; }
.ex-ab-primary, .ex-ab-secondary {
  display: flex; align-items: center; justify-content: center; height: 50px; border-radius: 100px;
  font-size: 16px; text-decoration: none; box-sizing: border-box;
}
.ex-ab-primary { background: #3b82f6; color: #f8fafc; font-weight: 700; }
.ex-ab-secondary { border: 1px solid #334155; color: #94a3b8; font-weight: 600; }

/* 06.6 / 06.7 results */
.ex-rs-screen { justify-content: space-between; background: #0f172a; color: #f8fafc; }
.ex-rs-scroll {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; align-items: center;
  gap: 20px; padding: 12px 20px 24px; box-sizing: border-box;
}
.ex-rs-header {
  display: flex; align-items: center; gap: 12px; width: 100%; height: 56px; box-sizing: border-box;
}
.ex-rs-header h2 {
  margin: 0; flex: 1; color: #f8fafc; font-size: 20px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ex-rs-xp {
  display: inline-flex; align-items: center; gap: 4px; padding: 6px 10px; border-radius: 100px;
  background: rgba(234,179,8,0.1); color: #eab308; font-size: 12px; font-weight: 700; white-space: nowrap;
}
.ex-rs-xp img { width: 14px; height: 14px; display: block; }
.ex-rs-hero {
  position: relative; width: 100%; height: 160px; display: flex; align-items: center; justify-content: center;
}
.ex-rs-hero.fail { height: 120px; }
.ex-rs-burst {
  width: 100px; height: 100px; border-radius: 50px; border: 4px solid #10b981; background: rgba(16,185,129,0.1);
  display: grid; place-items: center; box-sizing: border-box;
}
.ex-rs-burst.fail {
  width: 90px; height: 90px; border-radius: 45px; border-color: #ef4444; background: rgba(239,68,68,0.1);
}
.ex-rs-burst img { display: block; }
.ex-rs-spark { position: absolute; border-radius: 50%; display: block; }
.ex-rs-spark.s1 { left: 60px; top: 20px; width: 8px; height: 8px; background: #eab308; }
.ex-rs-spark.s2 { left: 310px; top: 40px; width: 10px; height: 10px; background: #10b981; }
.ex-rs-spark.s3 { left: 190px; top: 10px; width: 6px; height: 6px; background: #64748b; }
.ex-rs-spark.s4 {
  left: 76px; top: 110px; width: 12px; height: 6px; background: #3b82f6; border-radius: 1px; transform: rotate(45deg);
}
.ex-rs-spark.s5 {
  left: 280px; top: 95px; width: 10px; height: 5px; background: #f59e0b; border-radius: 1px; transform: rotate(-30deg);
}
.ex-rs-headline { text-align: center; display: flex; flex-direction: column; gap: 4px; }
.ex-rs-headline h3 { margin: 0; color: #10b981; font-size: 28px; font-weight: 800; }
.ex-rs-headline.fail h3 { color: #ef4444; }
.ex-rs-headline p { margin: 0; color: #94a3b8; font-size: 16px; }
.ex-rs-grade {
  width: 100%; display: flex; align-items: center; gap: 12px; padding: 16px; border-radius: 16px;
  background: #1e293b; border: 1px solid #334155; box-sizing: border-box;
}
.ex-rs-grade-main { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.ex-rs-grade-main > span { color: #94a3b8; font-size: 13px; }
.ex-rs-note { display: flex; align-items: center; gap: 6px; }
.ex-rs-note strong { color: #f8fafc; font-size: 24px; font-weight: 800; }
.ex-rs-note em {
  font-style: normal; padding: 2px 8px; border-radius: 4px; background: rgba(16,185,129,0.1); color: #10b981; font-size: 12px; font-weight: 700;
}
.ex-rs-note em.bad { background: rgba(239,68,68,0.1); color: #ef4444; }
.ex-rs-grade-main > p { margin: 0; color: #10b981; font-size: 13px; }
.ex-rs-grade-main > p.bad { color: #ef4444; }
.ex-rs-xp-glow {
  display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px; border-radius: 12px;
  background: rgba(234,179,8,0.1); border: 1.5px solid #eab308; color: #eab308;
  box-shadow: 0 4px 12px rgba(234,179,8,0.2);
}
.ex-rs-xp-glow strong { font-size: 22px; font-weight: 800; }
.ex-rs-xp-glow span { font-size: 11px; font-weight: 600; text-transform: uppercase; }
.ex-rs-xp-soft {
  display: flex; flex-direction: column; align-items: center; gap: 2px; padding: 10px 14px; border-radius: 12px;
  background: rgba(234,179,8,0.1); color: #eab308;
}
.ex-rs-xp-soft strong { font-size: 18px; font-weight: 800; }
.ex-rs-xp-soft span { font-size: 10px; font-weight: 600; text-transform: uppercase; }
.ex-rs-stats {
  width: 100%; display: flex; flex-direction: column; gap: 14px; padding: 20px; border-radius: 16px;
  background: #1e293b; box-sizing: border-box;
}
.ex-rs-stats h4 { margin: 0; color: #f8fafc; font-size: 16px; font-weight: 700; }
.ex-rs-stat-row { display: flex; align-items: center; justify-content: space-between; }
.ex-rs-stat-row span { display: inline-flex; align-items: center; gap: 8px; color: #94a3b8; font-size: 14px; }
.ex-rs-stat-row span img { display: block; }
.ex-rs-stat-row strong { color: #f8fafc; font-size: 14px; font-weight: 700; }
.ex-rs-divider { height: 1px; background: #334155; width: 100%; }
.ex-rs-record {
  display: flex; align-items: center; gap: 8px; color: #10b981; font-size: 13px;
}
.ex-rs-record img { width: 16px; height: 16px; display: block; }
.ex-rs-actions { width: 100%; display: flex; flex-direction: column; gap: 10px; }
.ex-rs-primary, .ex-rs-ghost {
  display: flex; align-items: center; justify-content: center; height: 48px; border-radius: 24px;
  font-size: 15px; text-decoration: none; box-sizing: border-box;
}
.ex-rs-primary { background: #3b82f6; color: #f8fafc; font-weight: 700; }
.ex-rs-ghost { border: 1px solid #334155; color: #94a3b8; font-weight: 600; }
.ex-rs-encourage {
  width: 100%; display: flex; flex-direction: column; gap: 14px; padding: 18px; border-radius: 16px;
  background: rgba(245,158,11,0.1); border: 1px solid #f59e0b; box-sizing: border-box;
}
.ex-rs-encourage-title { display: flex; align-items: center; gap: 8px; color: #f59e0b; }
.ex-rs-encourage-title img { width: 20px; height: 20px; }
.ex-rs-encourage-title strong { font-size: 15px; font-weight: 700; }
.ex-rs-encourage > p { margin: 0; color: #f8fafc; font-size: 14px; line-height: 1.4; }
.ex-rs-encourage-btn {
  display: flex; align-items: center; justify-content: center; height: 38px; border-radius: 19px;
  background: #1e293b; color: #f8fafc; font-size: 13px; font-weight: 700; text-decoration: none;
}
.ex-rs-mini { width: 100%; display: flex; gap: 8px; }
.ex-rs-mini > div {
  flex: 1; display: flex; flex-direction: column; align-items: center; gap: 4px; padding: 12px;
  border-radius: 12px; background: #1e293b;
}
.ex-rs-mini span { color: #94a3b8; font-size: 11px; }
.ex-rs-mini strong { color: #94a3b8; font-size: 18px; font-weight: 700; }
.ex-rs-mini strong.ok { color: #10b981; }
.ex-rs-mini strong.bad { color: #ef4444; }
.ex-rs-tabs {
  display: flex; align-items: center; justify-content: space-between; height: 72px; padding: 0 16px;
  background: #1e293b; border-top: 1px solid #334155; flex-shrink: 0; box-sizing: border-box;
}
.ex-rs-tabs a {
  width: 64px; display: flex; flex-direction: column; align-items: center; gap: 4px;
  color: #94a3b8; font-size: 11px; font-weight: 500; text-decoration: none;
}
.ex-rs-tabs a.active { color: #3b82f6; font-weight: 600; }
.ex-rs-tabs img { width: 22px; height: 22px; display: block; }
.ex-rs-home {
  height: 20px; background: #1e293b; display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.ex-rs-home::after {
  content: ""; width: 120px; height: 5px; border-radius: 100px; background: #334155; display: block;
}

/* 06.8 Schwache Themen */
.ex-wk-screen { justify-content: space-between; background: #0f172a; color: #f8fafc; }
.ex-wk-scroll {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; box-sizing: border-box;
}
.ex-wk-header {
  display: flex; align-items: center; gap: 12px; height: 56px; padding: 0 20px; flex-shrink: 0; box-sizing: border-box;
}
.ex-wk-back {
  display: grid; place-items: center; width: 36px; height: 36px; border-radius: 18px; background: #1e293b; flex-shrink: 0;
}
.ex-wk-back img { width: 18px; height: 18px; display: block; }
.ex-wk-header h2 {
  margin: 0; flex: 1; color: #f8fafc; font-size: 20px; font-weight: 700; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.ex-wk-sub { margin: 0; padding: 0 20px 16px; color: #94a3b8; font-size: 14px; }
.ex-wk-list { display: flex; flex-direction: column; gap: 12px; padding: 0 20px; }
.ex-wk-card {
  display: flex; flex-direction: column; gap: 12px; padding: 16px; border-radius: 16px;
  background: #1e293b; border-left: 4px solid #3b82f6; box-sizing: border-box;
}
.ex-wk-card.critical { border-left-color: #ef4444; }
.ex-wk-card.weak { border-left-color: #f59e0b; }
.ex-wk-card.fair { border-left-color: #eab308; }
.ex-wk-card.ok { border-left-color: #3b82f6; }
.ex-wk-card.perfect { border-left-color: #10b981; }
.ex-wk-top { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.ex-wk-title { display: flex; align-items: center; gap: 10px; min-width: 0; flex: 1; }
.ex-wk-title em { font-style: normal; color: #64748b; font-size: 14px; font-weight: 800; }
.ex-wk-title strong {
  color: #f8fafc; font-size: 16px; font-weight: 700; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.ex-wk-badge {
  padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; text-transform: uppercase; white-space: nowrap;
}
.ex-wk-card.critical .ex-wk-badge { background: rgba(239,68,68,0.08); color: #ef4444; }
.ex-wk-card.weak .ex-wk-badge { background: rgba(245,158,11,0.08); color: #f59e0b; }
.ex-wk-card.fair .ex-wk-badge { background: rgba(234,179,8,0.08); color: #eab308; }
.ex-wk-card.ok .ex-wk-badge { background: rgba(59,130,246,0.08); color: #3b82f6; }
.ex-wk-card.perfect .ex-wk-badge { background: rgba(16,185,129,0.08); color: #10b981; }
.ex-wk-bar { display: flex; align-items: center; gap: 12px; }
.ex-wk-bar > i {
  flex: 1; height: 6px; border-radius: 3px; background: #334155; position: relative; display: block; overflow: hidden;
}
.ex-wk-bar > i::before {
  content: ""; position: absolute; inset: 0 auto 0 0; width: inherit; height: 100%; border-radius: 3px; background: currentColor;
}
.ex-wk-card.critical .ex-wk-bar > i { color: #ef4444; }
.ex-wk-card.weak .ex-wk-bar > i { color: #f59e0b; }
.ex-wk-card.fair .ex-wk-bar > i { color: #eab308; }
.ex-wk-card.ok .ex-wk-bar > i { color: #3b82f6; }
.ex-wk-card.perfect .ex-wk-bar > i { color: #10b981; }
.ex-wk-bar > i {
  background: linear-gradient(to right, currentColor var(--pct, 25%), #334155 var(--pct, 25%));
}
.ex-wk-bar span { width: 90px; text-align: right; color: #94a3b8; font-size: 13px; flex-shrink: 0; }
.ex-wk-card > p { margin: 0; color: #94a3b8; font-size: 13px; }
.ex-wk-actions { display: flex; align-items: center; justify-content: space-between; }
.ex-wk-actions a {
  padding: 8px 16px; border-radius: 100px; background: rgba(59,130,246,0.13); color: #3b82f6;
  font-size: 12px; font-weight: 700; text-decoration: none;
}
.ex-wk-actions img { width: 16px; height: 16px; display: block; }
.ex-wk-bottom { padding: 20px; }
.ex-wk-bar > i[style] {
  /* width on i is fill via inline style - use nested approach */
}
.ex-wk-bar {
  /* override: use child fill */
}
.ex-wk-bar > i {
  background: #334155 !important;
  position: relative;
}
.ex-wk-bar > i::after {
  content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: inherit; border-radius: 3px;
  background: currentColor; width: 100%;
  /* will be clipped by parent width set via inline style on a wrapper - instead use transform */
}
'''

# Fix progress bar approach - rewrite wk-bar CSS more carefully
css_fix = '''
.ex-wk-bar {
  display: flex; align-items: center; gap: 12px;
}
.ex-wk-bar-track {
  flex: 1; height: 6px; border-radius: 3px; background: #334155; overflow: hidden;
}
.ex-wk-bar-track > i {
  display: block; height: 100%; border-radius: 3px;
}
.ex-wk-card.critical .ex-wk-bar-track > i { background: #ef4444; }
.ex-wk-card.weak .ex-wk-bar-track > i { background: #f59e0b; }
.ex-wk-card.fair .ex-wk-bar-track > i { background: #eab308; }
.ex-wk-card.ok .ex-wk-bar-track > i { background: #3b82f6; }
.ex-wk-card.perfect .ex-wk-bar-track > i { background: #10b981; }
.ex-wk-bar > span { width: 90px; text-align: right; color: #94a3b8; font-size: 13px; flex-shrink: 0; }

/* 06.9 Kammertermine */
.ex-cal-screen { justify-content: space-between; background: #0f172a; color: #f8fafc; }
.ex-cal-scroll {
  flex: 1; min-height: 0; overflow: auto; display: flex; flex-direction: column; box-sizing: border-box;
}
.ex-cal-wrap { padding: 0 20px 20px; }
.ex-cal-card {
  display: flex; flex-direction: column; gap: 12px; padding: 16px; border-radius: 16px; background: #1e293b;
}
.ex-cal-month { display: flex; align-items: center; justify-content: space-between; }
.ex-cal-month strong { color: #f8fafc; font-size: 16px; font-weight: 700; }
.ex-cal-arrows { display: flex; gap: 8px; }
.ex-cal-arrows button {
  background: transparent; border: 0; padding: 0; cursor: pointer; width: 16px; height: 16px;
}
.ex-cal-arrows img { width: 16px; height: 16px; display: block; }
.ex-cal-weekdays {
  display: flex; justify-content: space-between; color: #64748b; font-size: 12px; font-weight: 600; text-align: center;
}
.ex-cal-weekdays span { width: 28px; }
.ex-cal-grid { display: flex; flex-direction: column; gap: 8px; }
.ex-cal-row { display: flex; justify-content: space-between; }
.ex-cal-empty { width: 28px; height: 28px; display: block; }
.ex-cal-day {
  position: relative; width: 28px; height: 28px; border-radius: 14px; border: 0; background: transparent;
  color: #f8fafc; font-size: 13px; font-weight: 500; cursor: pointer; display: grid; place-items: center; padding: 0;
}
.ex-cal-day.selected { background: #3b82f6; font-weight: 700; }
.ex-cal-day.has-dot { font-weight: 700; }
.ex-cal-dot {
  position: absolute; bottom: 2px; left: 50%; transform: translateX(-50%); width: 4px; height: 4px; display: block;
}
.ex-cal-upcoming { display: flex; flex-direction: column; gap: 12px; padding: 0 20px; }
.ex-cal-upcoming h3 { margin: 0; color: #f8fafc; font-size: 16px; font-weight: 700; }
.ex-cal-event {
  display: flex; flex-direction: column; gap: 12px; padding: 16px; border-radius: 16px;
  background: #1e293b; border: 1px solid #334155; box-sizing: border-box;
}
.ex-cal-event-top { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.ex-cal-event-top strong { color: #f8fafc; font-size: 16px; font-weight: 700; display: block; }
.ex-cal-event-top p { margin: 2px 0 0; color: #94a3b8; font-size: 13px; }
.ex-cal-pill {
  padding: 6px 10px; border-radius: 100px; font-size: 12px; font-weight: 700; white-space: nowrap;
}
.ex-cal-pill.blue { background: rgba(59,130,246,0.13); color: #3b82f6; }
.ex-cal-pill.gold { background: rgba(234,179,8,0.1); color: #eab308; }
.ex-cal-event-div { height: 1px; background: #334155; width: 100%; }
.ex-cal-loc, .ex-cal-status {
  display: flex; align-items: center; gap: 8px; color: #94a3b8; font-size: 13px;
}
.ex-cal-status { color: #10b981; }
.ex-cal-loc img, .ex-cal-status img { width: 14px; height: 14px; display: block; }
.ex-cal-ready { display: flex; flex-direction: column; gap: 6px; }
.ex-cal-ready-lab { display: flex; justify-content: space-between; font-size: 12px; }
.ex-cal-ready-lab span { color: #94a3b8; }
.ex-cal-ready-lab strong { color: #f59e0b; font-weight: 700; }
.ex-cal-ready-bar { height: 6px; border-radius: 3px; background: #334155; overflow: hidden; }
.ex-cal-ready-bar > i { display: block; height: 100%; border-radius: 3px; background: #f59e0b; }
.ex-cal-warn {
  display: flex; align-items: center; gap: 8px; padding: 10px; border-radius: 8px;
  background: rgba(245,158,11,0.1); color: #f59e0b; font-size: 12px; font-weight: 600;
}
.ex-cal-warn img { width: 16px; height: 16px; display: block; }
.ex-cal-link { display: flex; justify-content: center; padding: 20px; }
.ex-cal-link a { color: #3b82f6; font-size: 14px; font-weight: 600; text-decoration: underline; }
'''

# Fix wk-bar markup in screens - replace broken bar with track
text = screens_path.read_text(encoding="utf-8")
text = text.replace(
    '<div class="ex-wk-bar"><i style="width:25%"></i><span>2/8 (25%)</span></div>',
    '<div class="ex-wk-bar"><div class="ex-wk-bar-track"><i style="width:25%"></i></div><span>2/8 (25%)</span></div>',
)
text = text.replace(
    '<div class="ex-wk-bar"><i style="width:43%"></i><span>3/7 (43%)</span></div>',
    '<div class="ex-wk-bar"><div class="ex-wk-bar-track"><i style="width:43%"></i></div><span>3/7 (43%)</span></div>',
)
text = text.replace(
    '<div class="ex-wk-bar"><i style="width:50%"></i><span>4/8 (50%)</span></div>',
    '<div class="ex-wk-bar"><div class="ex-wk-bar-track"><i style="width:50%"></i></div><span>4/8 (50%)</span></div>',
)
text = text.replace(
    '<div class="ex-wk-bar"><i style="width:71%"></i><span>5/7 (71%)</span></div>',
    '<div class="ex-wk-bar"><div class="ex-wk-bar-track"><i style="width:71%"></i></div><span>5/7 (71%)</span></div>',
)
text = text.replace(
    '<div class="ex-wk-bar"><i style="width:100%"></i><span>6/6 (100%)</span></div>',
    '<div class="ex-wk-bar"><div class="ex-wk-bar-track"><i style="width:100%"></i></div><span>6/6 (100%)</span></div>',
)
screens_path.write_text(text, encoding="utf-8")

# Strip broken wk-bar CSS from first css block - append clean CSS
# Remove the messy trailing wk-bar overrides from css string
css_clean = css.split(".ex-wk-bar > i[style]")[0]
css_final = css_clean + css_fix

css_text = css_path.read_text(encoding="utf-8")
marker = "/* --- 06.3 Übersicht"
if marker in css_text:
    css_text = css_text[: css_text.index(marker)]
css_path.write_text(css_text.rstrip() + "\n" + css_final + "\n", encoding="utf-8")
print("ui.css appended")
print("done")
