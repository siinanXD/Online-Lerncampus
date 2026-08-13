from pathlib import Path

path = Path(r"C:\dev\Repositories\Online-Lerncampus\app\web\static\screens.js")
text = path.read_text(encoding="utf-8")
start = text.index('  "s04_2-themenliste":')
end = text.index('  "s04_4-fragenliste-fehler":')

new = r'''  "s04_2-themenliste": () => `
      <section class="learn-drill" data-node-id="136:3719">
        <header class="learn-drill-header" data-node-id="136:3731">
          <a class="learn-back" href="/lernen" data-page-link>
            <img src="/static/figma/learn2/arrow-left.svg" width="20" height="20" alt="" />
            Fragen nach Thema
          </a>
          <div class="learn-drill-actions">
            <div class="learn-pct-ring" aria-label="Fortschritt 67%">
              <img class="learn-pct-track" src="/static/figma/learn2/ring-track.svg" width="36" height="36" alt="" />
              <img class="learn-pct-fill" src="/static/figma/learn2/ring-fill.svg" width="36" height="36" alt="" />
              <strong data-bind="readiness">67%</strong>
            </div>
            <a class="learn-menu-btn" href="/mehr" data-page-link aria-label="Menue">
              <img src="/static/figma/learn2/menu.svg" width="20" height="20" alt="" />
            </a>
          </div>
        </header>
        <div class="filter-pills learn-filters" data-node-id="136:3744">
          <button type="button" class="filter-pill active">Alle</button>
          <button type="button" class="filter-pill">Offen</button>
          <a class="filter-pill" href="/lernen/fragen/fehler" data-page-link>Fehler</a>
          <button type="button" class="filter-pill">Beherrscht</button>
        </div>
        <div class="topic-list figma-topics" data-node-id="136:3753">
          <a class="topic-row done" href="/lernen/fragen" data-page-link>
            <span class="topic-icon green"><img src="/static/figma/learn2/folder-green.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body">
              <span class="row-between"><strong>Grundlagen Metall</strong><span class="muted">30/30</span></span>
              <span class="row-between"><span class="stars-imgs"><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /></span><span class="status-pill ok">Beherrscht</span></span>
            </span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </a>
          <a class="topic-row" href="/lernen/fragen" data-page-link>
            <span class="topic-icon amber"><img src="/static/figma/learn2/folder-amber.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body">
              <span class="row-between"><strong>Werkstoffkunde</strong><span class="muted">26/30</span></span>
              <span class="row-between"><span class="stars-imgs"><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-half.svg" width="12" height="12" alt="" /></span><span class="mini-bar"><i style="width:86%;background:#f59e0b"></i></span></span>
            </span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </a>
          <a class="topic-row" href="/lernen/fragen" data-page-link>
            <span class="topic-icon blue"><img src="/static/figma/learn2/folder-blue.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body">
              <span class="row-between"><strong>Messtechnik</strong><span class="muted">18/30</span></span>
              <span class="row-between"><span class="stars-imgs"><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-off.svg" width="12" height="12" alt="" /></span><span class="mini-bar"><i style="width:60%;background:#2563eb"></i></span></span>
            </span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </a>
          <a class="topic-row" href="/lernen/fragen" data-page-link>
            <span class="topic-icon blue"><img src="/static/figma/learn2/folder-blue.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body">
              <span class="row-between"><strong>Pneumatik</strong><span class="muted">12/30</span></span>
              <span class="row-between"><span class="stars-imgs"><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-off.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-off.svg" width="12" height="12" alt="" /></span><span class="mini-bar"><i style="width:40%;background:#2563eb"></i></span></span>
            </span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </a>
          <a class="topic-row" href="/lernen/fragen" data-page-link>
            <span class="topic-icon muted"><img src="/static/figma/learn2/folder-gray.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body">
              <span class="row-between"><strong>Hydraulik</strong><span class="muted">3/30</span></span>
              <span class="row-between"><span class="stars-imgs"><img src="/static/figma/learn2/star-half.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-off.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-off.svg" width="12" height="12" alt="" /></span><span class="mini-bar"><i style="width:10%;background:#6b6661"></i></span></span>
            </span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </a>
          <div class="topic-row locked">
            <span class="topic-icon locked"><img src="/static/figma/learn2/lock.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body"><span class="row-between"><strong class="locked-title">Steuerungstechnik</strong><span class="muted">0/25</span></span></span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </div>
          <div class="topic-row locked">
            <span class="topic-icon locked"><img src="/static/figma/learn2/lock.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body"><span class="row-between"><strong class="locked-title">Elektrotechnik</strong><span class="muted">0/28</span></span></span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </div>
          <a class="topic-row done" href="/lernen/fragen" data-page-link>
            <span class="topic-icon green"><img src="/static/figma/learn2/folder-green.svg" width="18" height="18" alt="" /></span>
            <span class="topic-body">
              <span class="row-between"><strong>Arbeitssicherheit</strong><span class="muted">23/25</span></span>
              <span class="row-between"><span class="stars-imgs"><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /><img src="/static/figma/learn2/star-on.svg" width="12" height="12" alt="" /></span><span class="status-pill ok">Beherrscht</span></span>
            </span>
            <img class="topic-chev" src="/static/figma/learn2/chevron-right.svg" width="16" height="16" alt="" />
          </a>
        </div>
      </section>
    `,
  "s04_3-fragenliste-alle": () => `
      <section class="learn-drill" data-node-id="136:4019">
        <header class="learn-drill-header">
          <a class="learn-back" href="/lernen/themen" data-page-link>
            <img src="/static/figma/learn2/q-arrow-left.svg" width="20" height="20" alt="" />
            Pneumatik
          </a>
          <div class="learn-drill-actions">
            <div class="learn-pct-ring" aria-label="Fortschritt 67%">
              <img class="learn-pct-track" src="/static/figma/learn2/q-ring-track.svg" width="36" height="36" alt="" />
              <img class="learn-pct-fill" src="/static/figma/learn2/q-ring-fill.svg" width="36" height="36" alt="" />
              <strong>67%</strong>
            </div>
            <a class="learn-menu-btn" href="/mehr" data-page-link aria-label="Menue">
              <img src="/static/figma/learn2/q-menu.svg" width="20" height="20" alt="" />
            </a>
          </div>
        </header>
        <div class="topic-stats figma-topic-stats">
          <div class="row-between"><strong>30 Fragen — 12 beherrscht</strong><span class="mastery-pct">40%</span></div>
          <div class="mastery-track"><span class="mastery-fill" style="width:40%"></span></div>
        </div>
        <div class="filter-pills learn-filters">
          <a class="filter-pill active" href="/lernen/fragen" data-page-link>Alle</a>
          <button type="button" class="filter-pill">Offen</button>
          <a class="filter-pill" href="/lernen/fragen/fehler" data-page-link>Fehler</a>
          <button type="button" class="filter-pill">Beherrscht</button>
        </div>
        <div class="question-list figma-qlist" data-bind="question-list">
          <a class="q-row" href="/lernen/frage" data-page-link>
            <img class="q-dot" src="/static/figma/learn2/dot-green.svg" width="10" height="10" alt="" />
            <span>Was ist der Unterschied zwischen 2/2 und 3/2-Wegeventilen?</span>
            <span class="diff-bars" aria-hidden="true"><i></i><i></i><i></i></span>
            <img class="q-chev" src="/static/figma/learn2/q-chevron.svg" width="14" height="14" alt="" />
          </a>
        </div>
        <a class="primary-button btn-block hub-cta learn-all-btn" href="/lernen/frage" data-page-link>Alle lernen</a>
      </section>
    `,
'''

path.write_text(text[:start] + new + text[end:], encoding="utf-8")
print("ok", len(new))
