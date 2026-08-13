from pathlib import Path

p = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
text = p.read_text(encoding="utf-8")

s07 = r'''  "s07_1-fortschritt-uebersicht": () => `
      <div class="fp-screen" data-node-id="136:8922">
        <header class="fp-header">
          <span class="fp-header-spacer" aria-hidden="true"></span>
          <h2 class="fp-title">Mein Fortschritt</h2>
          <a class="fp-award-link" href="/gamification" data-page-link aria-label="Badges">
            <img src="/static/figma/fp/fp-award.svg" width="20" height="20" alt="" />
          </a>
        </header>
        <div class="fp-scroll">
          <article class="fp-hero">
            <div class="fp-hero-top">
              <div class="fp-avatar-wrap">
                <img class="fp-ring-track" src="/static/figma/fp/fp-track.svg" width="100" height="100" alt="" />
                <img class="fp-ring-progress" src="/static/figma/fp/fp-progress.svg" width="100" height="100" alt="" />
                <div class="fp-avatar">
                  <img src="/static/figma/fp/fp-avatar.png" width="78" height="78" alt="" />
                  <span class="fp-lvl">Lvl <span data-bind="level">7</span></span>
                </div>
              </div>
              <div class="fp-hero-copy">
                <div class="fp-streak"><img src="/static/figma/fp/fp-flame.svg" width="16" height="16" alt="" /><span data-bind="streak">12</span> Tage Streak</div>
                <strong>Exzellente Woche!</strong>
                <p>Du bist über dem Klassenschnitt.</p>
              </div>
            </div>
            <div class="fp-xp">
              <div class="fp-xp-row"><span>EP Fortschritt</span><b><span data-bind="xp">2450</span> / 3.000 XP</b></div>
              <div class="fp-xp-bar"><i data-bind="continue-bar" style="width:240px"></i></div>
            </div>
          </article>
          <h3 class="fp-section">Dein Lernpfad</h3>
          <div class="fp-gates">
            <div class="fp-gate done">
              <span class="fp-gate-ico ok"><img src="/static/figma/fp/fp-check.svg" width="20" height="20" alt="" /></span>
              <div><strong>Grundlagen</strong><p>Sicherheits- &amp; Werkstoffprüfungen</p></div>
              <img class="fp-gate-status" src="/static/figma/fp/fp-cc.svg" width="16" height="16" alt="" />
            </div>
            <div class="fp-gate done">
              <span class="fp-gate-ico ok"><img src="/static/figma/fp/fp-check.svg" width="20" height="20" alt="" /></span>
              <div><strong>Zwischenprüfung</strong><p>IHK Teil 1 Generalprobe</p></div>
              <img class="fp-gate-status" src="/static/figma/fp/fp-cc.svg" width="16" height="16" alt="" />
            </div>
            <div class="fp-gate active">
              <span class="fp-gate-ico info"><img src="/static/figma/fp/fp-zap.svg" width="20" height="20" alt="" /></span>
              <div><strong>Vertiefung</strong><p>Messtechnik &amp; Pneumatik Modul</p></div>
              <span class="fp-aktiv">AKTIV</span>
            </div>
            <div class="fp-gate locked">
              <span class="fp-gate-ico lock"><img src="/static/figma/fp/fp-lock.svg" width="20" height="20" alt="" /></span>
              <div><strong>AP Teil 1</strong><p>IHK Abschlussprüfung Teil 1</p></div>
              <img class="fp-gate-status" src="/static/figma/fp/fp-lock-sm.svg" width="16" height="16" alt="" />
            </div>
            <div class="fp-gate locked">
              <span class="fp-gate-ico lock"><img src="/static/figma/fp/fp-lock.svg" width="20" height="20" alt="" /></span>
              <div><strong>AP Teil 2</strong><p>Fachrichtungsspezifische Theorie</p></div>
              <img class="fp-gate-status" src="/static/figma/fp/fp-lock-sm.svg" width="16" height="16" alt="" />
            </div>
          </div>
          <div class="fp-badges-head">
            <h3 class="fp-section">Erfolge (12)</h3>
            <a href="/gamification" data-page-link class="fp-link">Alle Badges (12)</a>
          </div>
          <div class="fp-badges">
            <div class="fp-badge"><span><img src="/static/figma/fp/fp-badge-zap.svg" width="20" height="20" alt="" /></span><p>Pionier</p></div>
            <div class="fp-badge"><span><img src="/static/figma/fp/fp-badge-award.svg" width="20" height="20" alt="" /></span><p>10 Tage</p></div>
            <div class="fp-badge"><span><img src="/static/figma/fp/fp-badge-check.svg" width="20" height="20" alt="" /></span><p>Perfekt</p></div>
            <div class="fp-badge"><span><img src="/static/figma/fp/fp-badge-clock.svg" width="20" height="20" alt="" /></span><p>Speedy</p></div>
          </div>
          <div class="visually-hidden" aria-hidden="true">
            <span data-bind="mastered"></span><span data-bind="wrong"></span><span data-bind="readiness"></span>
          </div>
        </div>
        <nav class="fp-tabs" aria-label="Fortschritt Navigation">
          <a href="/dashboard" data-page-link><img src="/static/figma/fp/fp-tab-book.svg" width="20" height="20" alt="" />Campus</a>
          <a href="/lernen" data-page-link><img src="/static/figma/fp/fp-tab-edit.svg" width="20" height="20" alt="" />Üben</a>
          <a href="/berichtsheft" data-page-link class="active"><img src="/static/figma/fp/fp-tab-activity.svg" width="20" height="20" alt="" />Bericht</a>
          <a href="/mehr" data-page-link><img src="/static/figma/fp/fp-tab-user.svg" width="20" height="20" alt="" />Profil</a>
        </nav>
        <div class="fp-home-indicator" aria-hidden="true"></div>
      </div>
    `,'''

s08 = r'''  "s08_1-berichtsheft-liste": () => `
      <div class="bh2-screen" data-node-id="136:9762">
        <header class="bh2-header">
          <div class="bh2-brand">
            <span class="bh2-logo"><img src="/static/figma/bh/bh-book.svg" width="18" height="18" alt="" /></span>
            <h2>Berichtsheft</h2>
          </div>
          <a class="bh2-add" href="/berichtsheft/neu" data-page-link aria-label="Neuer Eintrag">
            <img src="/static/figma/bh/bh-plus.svg" width="20" height="20" alt="" />
          </a>
        </header>
        <div class="bh2-filters" role="tablist" aria-label="Filter">
          <button class="bh2-chip active" type="button">Alle</button>
          <button class="bh2-chip" type="button">Lücken</button>
          <button class="bh2-chip" type="button">Entwürfe</button>
          <button class="bh2-chip" type="button">Freigegeben</button>
        </div>
        <div class="bh2-scroll">
          <a class="bh2-warn" href="/berichtsheft/neu" data-page-link>
            <div class="bh2-warn-top">
              <span class="bh2-warn-ico"><img src="/static/figma/bh/bh-alert.svg" width="18" height="18" alt="" /></span>
              <div><strong>3 fehlende Einträge</strong><span>KW 10, KW 11, KW 12</span></div>
            </div>
            <div class="bh2-warn-cta">Jetzt ausfüllen und einreichen <img src="/static/figma/bh/bh-arrow.svg" width="16" height="16" alt="" /></div>
          </a>
          <p class="bh2-label">Berichte Chronologisch</p>
          <a class="bh2-entry" href="/berichtsheft/unterschrift" data-page-link>
            <div class="bh2-entry-top"><div><strong>KW 13</strong><span>25.–29.03.</span></div><span class="bh2-tag draft">Entwurf</span></div>
            <div class="bh2-entry-bottom"><div><strong>Montage Grundlagen, Pneumatik-Übung</strong><span>Letzte Änderung gestern</span></div><img src="/static/figma/bh/bh-chevron.svg" width="16" height="16" alt="" /></div>
          </a>
          <a class="bh2-entry gap" href="/berichtsheft/neu" data-page-link>
            <div class="bh2-entry-top"><div><strong>KW 12</strong><span>18.–22.03.</span></div><span class="bh2-tag gap">Lücke</span></div>
            <div class="bh2-entry-bottom"><div><strong class="danger">Eintrag fehlt!</strong><span>Fällig seit 4 Tagen</span></div><span class="bh2-fill">Ausfüllen</span></div>
          </a>
          <a class="bh2-entry gap" href="/berichtsheft/neu" data-page-link>
            <div class="bh2-entry-top"><div><strong>KW 11</strong><span>11.–15.03.</span></div><span class="bh2-tag gap">Lücke</span></div>
            <div class="bh2-entry-bottom"><div><strong class="danger">Eintrag fehlt!</strong><span>Fällig seit 11 Tagen</span></div><span class="bh2-fill">Ausfüllen</span></div>
          </a>
          <a class="bh2-entry" href="/berichtsheft/unterschrift" data-page-link>
            <div class="bh2-entry-top"><div><strong>KW 10</strong><span>04.–08.03.</span></div><span class="bh2-tag ok">Freigegeben</span></div>
            <div class="bh2-entry-bottom"><div><strong>Werkstoffprüfung, Messtechnik Labor</strong><span>Freigegeben durch H. Müller</span></div><img src="/static/figma/bh/bh-chevron.svg" width="16" height="16" alt="" /></div>
          </a>
          <a class="bh2-entry" href="/berichtsheft/unterschrift" data-page-link>
            <div class="bh2-entry-top"><div><strong>KW 9</strong><span>25.–29.02.</span></div><span class="bh2-tag ok">Freigegeben</span></div>
            <div class="bh2-entry-bottom"><div><strong>Drehen und Fräsen, Qualitätskontrolle</strong><span>Freigegeben durch H. Müller</span></div><img src="/static/figma/bh/bh-chevron.svg" width="16" height="16" alt="" /></div>
          </a>
          <div class="visually-hidden" data-bind="reports-live" aria-hidden="true"></div>
        </div>
        <div class="bh2-progress">
          <div class="bh2-progress-row"><span>Dokumentierter Fortschritt</span><b>12 von 24 Wochen (50%)</b></div>
          <div class="bh2-progress-bar"><i style="width:175px"></i></div>
        </div>
        <nav class="bh2-tabs" aria-label="Bericht Navigation">
          <a href="/dashboard" data-page-link><span><img src="/static/figma/bh/bh-tab-home.svg" width="20" height="20" alt="" /></span>Campus</a>
          <a href="/berichtsheft" data-page-link class="active"><span class="on"><img src="/static/figma/bh/bh-tab-file.svg" width="20" height="20" alt="" /></span>Bericht</a>
          <a href="/fortschritt" data-page-link><span><img src="/static/figma/bh/bh-tab-trophy.svg" width="20" height="20" alt="" /></span>Erfolge</a>
          <a href="/mehr" data-page-link><span><img src="/static/figma/bh/bh-tab-user.svg" width="20" height="20" alt="" /></span>Profil</a>
        </nav>
      </div>
    `,'''

import re
text2, n1 = re.subn(
    r'  "s07_1-fortschritt-uebersicht": \(\) => `.*?`,\n  "s07_2',
    s07 + '\n  "s07_2',
    text,
    count=1,
    flags=re.S,
)
text3, n2 = re.subn(
    r'  "s08_1-berichtsheft-liste": \(\) => `.*?`,\n  "s08_2',
    s08 + '\n  "s08_2',
    text2,
    count=1,
    flags=re.S,
)
print("replaced", n1, n2)
p.write_text(text3, encoding="utf-8")
