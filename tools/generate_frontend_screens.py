"""Generate screens.js and route allowlist from work/screen_catalog.json."""

from __future__ import annotations

import json
from pathlib import Path


def esc(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("${", "\\${")
        .replace("</", "<\\/")
    )


def list_items(texts: list[str], limit: int = 8) -> str:
    items = texts[:limit] or ["Noch keine Inhalte."]
    return "".join(f"<li>{esc(item)}</li>" for item in items)


def chips(texts: list[str], limit: int = 5) -> str:
    items = texts[:limit] or ["Demo"]
    return "".join(f'<span class="tool-chip">{esc(item)}</span>' for item in items)


def build_screen_body(screen: dict) -> str:
    num = screen["num"]
    title = esc(screen["title"])
    texts = [t for t in screen.get("texts", []) if t]
    layout = screen["layout"]
    path = screen["path"]
    section = int(num.split(".")[0])

    # Specialized templates by section / known paths
    if path == "/login":
        return ""  # handled by static HTML layout
    if path == "/":
        return ""  # landing static

    if path == "/passwort":
        return f"""
      <div class="auth-card screen-card">
        <div class="login-brand"><div class="logo-mark">BZE</div><strong>Online Campus</strong></div>
        <h1>Passwort aendern</h1>
        <p class="muted">Dein vorlaeufiges Passwort muss geaendert werden.</p>
        <form class="stack-form" data-action="change-password">
          <label class="field"><span>Aktuelles Passwort</span><input type="password" name="current" required minlength="4" /></label>
          <label class="field"><span>Neues Passwort</span><input type="password" name="next" required minlength="8" /></label>
          <label class="field"><span>Passwort bestaetigen</span><input type="password" name="confirm" required minlength="8" /></label>
          <ul class="hint-list"><li>Mindestens 8 Zeichen</li><li>Gross- und Kleinbuchstaben</li><li>Mindestens eine Zahl</li></ul>
          <button class="primary-button btn-block" type="submit">Passwort speichern</button>
        </form>
        <p class="feedback" data-feedback></p>
      </div>"""

    if path == "/sprache":
        return """
      <div class="auth-card screen-card">
        <h1>Sprache waehlen</h1>
        <p class="muted">Waehle deine bevorzugte Sprache fuer die Plattform.</p>
        <div class="lang-grid">
          <button type="button" class="lang-option active" data-lang="de">Deutsch</button>
          <button type="button" class="lang-option" data-lang="en">English</button>
          <button type="button" class="lang-option" data-lang="tr">Tuerkce</button>
          <button type="button" class="lang-option" data-lang="ar">العربية</button>
          <button type="button" class="lang-option" data-lang="uk">Ukrainisch</button>
        </div>
        <label class="field"><span>Kohortencode (optional)</span><input name="cohort" placeholder="z.B. BZE-2026-F" /></label>
        <div class="row-actions">
          <a class="primary-button" href="/onboarding" data-page-link>Weiter</a>
          <a class="secondary-button" href="/dashboard" data-page-link>Ueberspringen</a>
        </div>
      </div>"""

    if path == "/onboarding":
        return """
      <div class="auth-card screen-card onboarding-card">
        <h1>Willkommen bei BZE!</h1>
        <p class="muted">Dein persoenlicher Lernbegleiter fuer die IHK-Pruefung.</p>
        <ul class="feature-bullets">
          <li>Pruefungsfragen mit sofortigem Feedback</li>
          <li>Fortschritt verfolgen &amp; Schwaechen erkennen</li>
          <li>KI-Coach fuer individuelle Erklaerungen</li>
        </ul>
        <a class="primary-button btn-block" href="/dashboard" data-page-link>Los geht's!</a>
        <a class="secondary-button btn-block" href="/dashboard" data-page-link>Ueberspringen</a>
      </div>"""

    if path == "/level-up":
        return """
      <div class="auth-card screen-card levelup-card">
        <div class="level-burst" aria-hidden="true">8</div>
        <h1>LEVEL UP!</h1>
        <p>Level 8 erreicht · Neuer Titel: Facharbeiter</p>
        <ul class="reward-list">
          <li>+100 Bonus-XP</li>
          <li>Neues Abzeichen freigeschaltet</li>
          <li>Freischaltung: Hydraulik</li>
        </ul>
        <a class="primary-button btn-block" href="/dashboard" data-page-link>Weiter</a>
        <p class="muted">Level 9 in 1.550 XP</p>
      </div>"""

    # Dashboard variants
    if path.startswith("/dashboard"):
        return f"""
      <div class="screen-head">
        <p class="eyebrow">{esc(num)} Start</p>
        <h2>{title}</h2>
      </div>
      <article class="continue-card fortsetzen-card">
        <div><p class="eyebrow">Fortsetzen</p><h3>Messschieber</h3><p class="muted">Theorie, Uebung, Fragen.</p></div>
        <a class="btn btn-primary" href="/lernen" data-page-link>Weiter</a>
      </article>
      <article class="card tagesziel-card">
        <div class="row-between"><strong>Tagesziel</strong><span class="muted">2 von 5</span></div>
        <div class="segmented-progress"><span class="filled"></span><span class="filled"></span><span></span><span></span><span></span></div>
      </article>
      <div class="metric-grid">
        <article class="metric-card card"><strong>72%</strong><span>Pruefungsreife</span></article>
        <article class="metric-card card"><strong>12</strong><span>Streak</span></article>
      </div>
      <article class="card"><strong>Highlights</strong><ul class="plain-list">{list_items(texts)}</ul>
        <div class="hub-actions"><a class="secondary-button" href="/lernen" data-page-link>Zum Lernen</a></div>
      </article>"""

    # Learn / Fachkunde shared patterns
    if path == "/lernen":
        return """
      <div class="screen-head"><p class="eyebrow">04 Lernen</p><h2>Lernen</h2></div>
      <div class="learn-hub">
        <article class="hub-card"><p class="eyebrow">Ueben</p><h3>Fragenpraxis</h3><p class="muted">PAL-aehnliche Single-Choice.</p>
          <div class="hub-actions"><a class="primary-button" href="/lernen/fragen" data-page-link>Starten</a></div></article>
        <article class="hub-card"><p class="eyebrow">Fachkunde</p><h3>Lerneinheiten</h3><p class="muted">Theorie, Glossar, Uebungen.</p>
          <div class="hub-actions"><a class="secondary-button" href="/fachkunde" data-page-link>Oeffnen</a></div></article>
        <article class="hub-card"><p class="eyebrow">Werkzeuge</p><h3>Hilfsmittel</h3>
          <div class="hub-meta"><a class="tool-chip" href="/lernen/glossar" data-page-link>Glossar</a>
            <a class="tool-chip" href="/lernen/formeltrainer" data-page-link>Formeltrainer</a>
            <a class="tool-chip" href="/lernen/fehlerdiagnose" data-page-link>Fehlerdiagnose</a></div>
        </article>
      </div>"""

    if path in {"/lernen/themen", "/fachkunde/lernpfad", "/lernen/lernpfad"}:
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)}</p><h2>{title}</h2>
        <a class="secondary-button" href="/lernen" data-page-link>Zurueck</a></div>
      <div class="path-map">
        <button class="path-node done" type="button">1 · Grundlagen</button>
        <button class="path-node done" type="button">2 · Messschieber</button>
        <button class="path-node active" type="button">3 · Toleranzen</button>
        <button class="path-node" type="button">4 · Spritzguss</button>
        <button class="path-node locked" type="button">5 · Pruefung</button>
      </div>
      <ul class="nav-list">{list_items(texts, 10)}</ul>"""

    if path in {"/lernen/fragen", "/lernen/fragen/fehler"}:
        mode = "Fehler" if "fehler" in path else "Alle"
        return f"""
      <div class="screen-head"><p class="eyebrow">Fragenliste · {mode}</p><h2>{title}</h2>
        <div class="row-actions">
          <a class="{'primary-button' if mode=='Alle' else 'secondary-button'}" href="/lernen/fragen" data-page-link>Alle</a>
          <a class="{'primary-button' if mode=='Fehler' else 'secondary-button'}" href="/lernen/fragen/fehler" data-page-link>Fehler</a>
        </div>
      </div>
      <div class="question-list" data-bind="question-list">
        <article class="list-row"><strong>Frage wird geladen …</strong><span class="muted">API</span></article>
      </div>
      <a class="primary-button btn-block" href="/lernen/frage" data-page-link>Erste Frage oeffnen</a>"""

    if path.startswith("/lernen/frage") or path.startswith("/lernen/feedback"):
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)}</p><h2>{title}</h2></div>
      <article class="card question-play">
        <p class="eyebrow">Frage 3 von 20</p>
        <h3 data-bind="live-question-prompt">Welche Funktion erfuellt das Rueckschlagventil?</h3>
        <div class="answer-options" data-bind="live-answers">
          <button class="answer-option" type="button">Verhindert Ruecklauf</button>
          <button class="answer-option" type="button">Erhoeht den Druck</button>
          <button class="answer-option" type="button">Misst den Durchfluss</button>
          <button class="answer-option" type="button">Kuehlt das Medium</button>
        </div>
        <p class="feedback" data-bind="live-feedback"></p>
        <div class="row-actions">
          <a class="secondary-button" href="/lernen/melden" data-page-link>Melden</a>
          <a class="secondary-button" href="/lernen/uebersetzung" data-page-link>Uebersetzung</a>
          <a class="primary-button" href="/lernen/fragen" data-page-link>Weiter</a>
        </div>
      </article>
      <ul class="plain-list muted">{list_items(texts, 6)}</ul>"""

    if path in {"/lernen/formeltrainer", "/lernen/flashcard", "/fachkunde/toleranz", "/fachkunde/spritzguss", "/fachkunde/messschieber"}:
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)} Werkzeug</p><h2>{title}</h2>
        <a class="secondary-button" href="/lernen" data-page-link>Zurueck</a></div>
      <article class="card tool-stage">
        <p class="eyebrow">Interaktive Uebung</p>
        <h3>{title}</h3>
        <p class="muted">Demo-Zustand mit realistischen Platzhaltern aus dem Designsystem.</p>
        <div class="tool-canvas" aria-hidden="true"><span></span><span></span><span></span></div>
        <div class="hub-meta">{chips(texts)}</div>
        <div class="row-actions">
          <button class="primary-button" type="button" data-action="toast" data-toast="Uebung gespeichert (+15 XP)">Pruefen</button>
          <button class="secondary-button" type="button" data-action="toast" data-toast="Naechste Aufgabe geladen">Naechste</button>
        </div>
      </article>"""

    if path in {"/lernen/fehlerdiagnose", "/lernen/video", "/lernen/detail", "/lernen/einheit", "/lernen/glossar", "/lernen/melden", "/lernen/uebersetzung", "/lernen/tablet"}:
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)}</p><h2>{title}</h2>
        <a class="secondary-button" href="/lernen" data-page-link>Zurueck</a></div>
      <article class="card">
        <p class="muted">Produkt-UI gemaess Figma {esc(num)}.</p>
        <ul class="plain-list">{list_items(texts, 12)}</ul>
        <div class="row-actions">
          <a class="primary-button" href="/lernen/frage" data-page-link>Weiterueben</a>
          <a class="secondary-button" href="/fachkunde" data-page-link>Zur Fachkunde</a>
        </div>
      </article>"""

    if path.startswith("/fachkunde"):
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)} Fachkunde</p><h2>{title}</h2>
        <a class="secondary-button" href="/lernen" data-page-link>Lern-Hub</a></div>
      <div class="card-grid">
        <article class="hub-card"><h3>Lernpfad</h3><p class="muted">Einheiten in Reihenfolge.</p>
          <a class="secondary-button" href="/fachkunde/lernpfad" data-page-link>Oeffnen</a></article>
        <article class="hub-card"><h3>Glossar</h3><p class="muted">Fachbegriffe nachschlagen.</p>
          <a class="secondary-button" href="/fachkunde/glossar" data-page-link>Oeffnen</a></article>
        <article class="hub-card"><h3>Bausteine</h3><p class="muted">Theorie &amp; Uebungen.</p>
          <a class="secondary-button" href="/fachkunde/bausteine" data-page-link>Oeffnen</a></article>
      </div>
      <article class="card"><strong>Inhalt</strong><ul class="plain-list">{list_items(texts, 10)}</ul></article>"""

    if path == "/pruefungen":
        return """
      <div class="screen-head"><p class="eyebrow">06 Pruefung</p><h2>Testpruefungen</h2></div>
      <div data-bind="exam-live"></div>
      <div class="link-grid">
        <a href="/pruefungen/uebersicht" data-page-link>Uebersicht</a>
        <a href="/pruefungen/timer" data-page-link>Timer</a>
        <a href="/pruefungen/kammertermine" data-page-link>Kammertermine</a>
        <a href="/pruefungen/schwach" data-page-link>Schwache Themen</a>
      </div>"""

    if path.startswith("/pruefungen/"):
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)} Pruefung</p><h2>{title}</h2>
        <a class="secondary-button" href="/pruefungen" data-page-link>Zur Liste</a></div>
      <article class="card exam-panel">
        <ul class="plain-list">{list_items(texts, 12)}</ul>
        <div class="row-actions">
          <a class="primary-button" href="/pruefungen" data-page-link data-action="exam-start-shortcut">Session starten</a>
          <a class="secondary-button" href="/pruefungen/abgabe" data-page-link>Abgabe</a>
          <a class="secondary-button" href="/pruefungen/bestanden" data-page-link>Ergebnis</a>
        </div>
      </article>"""

    if path.startswith("/fortschritt"):
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)} Fortschritt</p><h2>{title}</h2></div>
      <div class="metric-grid">
        <article class="metric-card card"><strong data-bind="mastered">0</strong><span>Gemeistert</span></article>
        <article class="metric-card card"><strong data-bind="wrong">0</strong><span>Fehler</span></article>
        <article class="metric-card card"><strong data-bind="readiness">0%</strong><span>Reife</span></article>
      </div>
      <article class="card"><ul class="plain-list">{list_items(texts, 10)}</ul>
        <div class="link-grid">
          <a href="/fortschritt/pruefungsreife" data-page-link>Pruefungsreife</a>
          <a href="/fortschritt/verlauf" data-page-link>Verlauf</a>
          <a href="/fortschritt/xp" data-page-link>XP &amp; Streak</a>
          <a href="/fortschritt/heatmap" data-page-link>Heatmap</a>
        </div>
      </article>"""

    if path == "/berichtsheft":
        return """
      <div class="screen-head"><p class="eyebrow">08 Berichtsheft</p><h2>Ausbildungsnachweis</h2>
        <a class="primary-button" href="/berichtsheft/neu" data-page-link>Neuer Eintrag</a></div>
      <div data-bind="reports-live"></div>
      <div class="link-grid">
        <a href="/berichtsheft/ki" data-page-link>KI-Assistent</a>
        <a href="/berichtsheft/kalender" data-page-link>Kalender</a>
        <a href="/berichtsheft/unterschrift" data-page-link>Unterschrift</a>
        <a href="/berichtsheft/export" data-page-link>PDF-Export</a>
        <a href="/berichtsheft/leer" data-page-link>Leerzustand</a>
      </div>"""

    if path.startswith("/berichtsheft/"):
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)}</p><h2>{title}</h2>
        <a class="secondary-button" href="/berichtsheft" data-page-link>Zur Liste</a></div>
      <article class="card">
        <ul class="plain-list">{list_items(texts, 12)}</ul>
        {"<form class='stack-form' data-action='create-report'><label class='field'><span>Datum</span><input type='date' name='report_date' required /></label><label class='field'><span>Stunden</span><input type='number' name='hours' min='1' max='12' step='0.5' value='8' required /></label><label class='field'><span>Taetigkeiten</span><textarea name='activities' rows='5' required></textarea></label><button class='primary-button' type='submit'>Speichern</button></form>" if path.endswith('/neu') else ""}
        <p class="feedback" data-feedback></p>
      </article>"""

    if path == "/mehr":
        return """
      <div class="screen-head"><p class="eyebrow">09 Mehr</p><h2>Profil &amp; Konto</h2></div>
      <article class="card">
        <p data-bind="profile-summary" class="muted">Nicht angemeldet.</p>
        <div class="settings-list">
          <a href="/mehr/ausbilder-sicht" data-page-link>Was sieht der Ausbilder?</a>
          <a href="/mehr/coach" data-page-link>KI-Coach</a>
          <a href="/mehr/lernplan" data-page-link>Lernplan</a>
          <a href="/mehr/export" data-page-link>Datenexport</a>
          <a href="/gamification" data-page-link>Gamification</a>
          <a href="/passwort" data-page-link>Passwort aendern</a>
          <a href="/sprache" data-page-link>Sprache</a>
          <a href="/ausbilder" data-page-link>Ausbilder-Bereich</a>
          <a href="/admin" data-page-link>Admin-Bereich</a>
          <a href="/mehr/logout" data-page-link>Abmelden</a>
          <a href="/mehr/loeschen" data-page-link>Konto loeschen</a>
        </div>
      </article>"""

    if path.startswith("/mehr/") or path.startswith("/gamification"):
        return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)}</p><h2>{title}</h2>
        <a class="secondary-button" href="/mehr" data-page-link>Zurueck</a></div>
      <article class="card">
        <ul class="plain-list">{list_items(texts, 12)}</ul>
        <div class="row-actions">
          {"<button class='primary-button' type='button' data-action='logout'>Abmelden</button>" if path.endswith('/logout') else ""}
          {"<button class='primary-button' type='button' data-action='delete-account'>Konto loeschen</button>" if path.endswith('/loeschen') else ""}
          {"<button class='primary-button' type='button' data-action='export-data'>Export laden</button>" if path.endswith('/export') else ""}
          {"<div class='chat-demo'><div class='chat-bubble bot'>Woran haengst du gerade?</div><div class='chat-bubble me'>Toleranzen H7</div><label class='field'><span>Nachricht</span><input placeholder='Frage den Coach…' /></label></div>" if 'coach' in path else ""}
        </div>
        <pre class="export-pre" data-bind="export-pre" hidden></pre>
      </article>"""

    if layout == "trainer":
        nav_hint = "Cockpit · Review · Content · Berichte"
        return f"""
      <div class="desk-head">
        <div><p class="eyebrow">{esc(num)} Ausbilder</p><h2>{title}</h2></div>
        <p class="muted">{nav_hint}</p>
      </div>
      <div class="desk-grid">
        <aside class="desk-side card">
          <strong>Schnellzugriff</strong>
          <nav class="settings-list">
            <a href="/ausbilder" data-page-link>Cockpit</a>
            <a href="/ausbilder/teilnehmer" data-page-link>Teilnehmer</a>
            <a href="/ausbilder/review" data-page-link>Review</a>
            <a href="/ausbilder/fragen" data-page-link>Fragen</a>
            <a href="/ausbilder/generator" data-page-link>KI-Generator</a>
            <a href="/ausbilder/berichte" data-page-link>Berichte</a>
            <a href="/ausbilder/planung" data-page-link>Planung</a>
          </nav>
        </aside>
        <section class="desk-main card">
          <div class="metric-grid desk-metrics">
            <article class="metric-card"><strong>24</strong><span>Teilnehmer</span></article>
            <article class="metric-card"><strong>6</strong><span>Risiko</span></article>
            <article class="metric-card"><strong>11</strong><span>Reviews offen</span></article>
            <article class="metric-card"><strong>82%</strong><span>Kohorten-Schnitt</span></article>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead><tr><th>Name</th><th>Status</th><th>Reife</th><th>Aktion</th></tr></thead>
              <tbody>
                <tr><td>Alex M.</td><td><span class="badge warn">Risiko</span></td><td>54%</td><td><a href="/ausbilder/teilnehmer" data-page-link>Oeffnen</a></td></tr>
                <tr><td>Samira K.</td><td><span class="badge ok">Stabil</span></td><td>78%</td><td><a href="/ausbilder/teilnehmer" data-page-link>Oeffnen</a></td></tr>
                <tr><td>Jonas P.</td><td><span class="badge info">Neu</span></td><td>41%</td><td><a href="/ausbilder/teilnehmer" data-page-link>Oeffnen</a></td></tr>
              </tbody>
            </table>
          </div>
          <ul class="plain-list">{list_items(texts, 10)}</ul>
          <div class="row-actions">
            <button class="primary-button" type="button" data-action="load-reviews">Reviews laden</button>
            <button class="secondary-button" type="button" data-action="generate-draft">Mission erzeugen</button>
          </div>
          <div class="admin-output" data-bind="trainer-output"></div>
        </section>
      </div>"""

    if layout == "admin":
        return f"""
      <div class="desk-head">
        <div><p class="eyebrow">{esc(num)} Admin</p><h2>{title}</h2></div>
      </div>
      <div class="desk-grid">
        <aside class="desk-side card">
          <strong>Betrieb</strong>
          <nav class="settings-list">
            <a href="/admin" data-page-link>Shell</a>
            <a href="/admin/nutzer" data-page-link>Nutzer</a>
            <a href="/admin/audit" data-page-link>Audit Log</a>
            <a href="/admin/einstellungen" data-page-link>Einstellungen</a>
            <a href="/admin/monitoring" data-page-link>Monitoring</a>
            <a href="/admin/content" data-page-link>Content</a>
            <a href="/admin/import" data-page-link>Import</a>
            <a href="/admin/dubletten" data-page-link>Dubletten</a>
          </nav>
        </aside>
        <section class="desk-main card">
          <div class="metric-grid desk-metrics">
            <article class="metric-card"><strong>128</strong><span>Nutzer</span></article>
            <article class="metric-card"><strong>99.9%</strong><span>Uptime</span></article>
            <article class="metric-card"><strong>3</strong><span>Incidents</span></article>
            <article class="metric-card"><strong>42</strong><span>Pending Content</span></article>
          </div>
          <div class="table-wrap">
            <table class="data-table">
              <thead><tr><th>ID</th><th>Ereignis</th><th>Zeit</th><th>Akteur</th></tr></thead>
              <tbody>
                <tr><td>A-1024</td><td>Login</td><td>heute 09:12</td><td>admin-demo</td></tr>
                <tr><td>A-1025</td><td>Content Freigabe</td><td>heute 10:03</td><td>reviewer-demo</td></tr>
                <tr><td>A-1026</td><td>Import</td><td>gestern 16:40</td><td>admin-demo</td></tr>
              </tbody>
            </table>
          </div>
          <ul class="plain-list">{list_items(texts, 10)}</ul>
        </section>
      </div>"""

    # generic fallback
    shell_back = "/dashboard" if layout == "app" else ("/ausbilder" if layout == "trainer" else "/admin")
    return f"""
      <div class="screen-head"><p class="eyebrow">{esc(num)}</p><h2>{title}</h2>
        <a class="secondary-button" href="{shell_back}" data-page-link>Zurueck</a></div>
      <article class="card">
        <p class="muted">Figma-Frame {esc(num)} · {screen['w']}x{screen['h']}</p>
        <ul class="plain-list">{list_items(texts, 14)}</ul>
      </article>"""


def main() -> None:
    catalog = json.loads(Path("work/screen_catalog.json").read_text(encoding="utf-8"))
    screens = catalog["screens"]
    aliases = catalog["aliases"]

    route_entries = []
    renderers = []
    for screen in screens:
        title = esc(screen["title"])
        layout = screen["layout"]
        # landing/login stay as static layouts with empty mount optional
        if screen["path"] in {"/", "/login"}:
            route_entries.append(
                f'  "{screen["path"]}": {{ layout: "{layout}", screen: "{screen["id"]}", '
                f'title: "{title}", tab: {json.dumps(screen.get("tab"))}, num: "{screen["num"]}" }},'
            )
            renderers.append(
                f'  "{screen["id"]}": () => `<div class="screen-static" data-screen="{screen["id"]}"></div>`,'
            )
            continue
        body = build_screen_body(screen)
        route_entries.append(
            f'  "{screen["path"]}": {{ layout: "{layout}", screen: "{screen["id"]}", '
            f'title: "{title}", tab: {json.dumps(screen.get("tab"))}, num: "{screen["num"]}" }},'
        )
        renderers.append(f'  "{screen["id"]}": () => `\n{body}\n    `,')

    for alias, target in aliases.items():
        route_entries.append(f'  "{alias}": {{ aliasOf: "{target}" }},')

    paths = sorted({s["path"] for s in screens} | set(aliases.keys()))
    # strip leading slash for FastAPI allowlist ("" for root)
    allow = []
    for path in paths:
        allow.append("" if path == "/" else path.lstrip("/"))

    js = f"""/* Auto-generated by tools/generate_frontend_screens.py — Figma screen registry. */
window.OLC_SCREEN_CATALOG = {{
  generatedFrom: "BZE Online Campus Fachkunde Designsystem.fig",
  count: {len(screens)},
}};

window.OLC_ROUTE_CONFIG = {{
{chr(10).join(route_entries)}
}};

window.OLC_SCREEN_RENDERERS = {{
{chr(10).join(renderers)}
}};

window.OLC_ALLOWED_PAGES = {json.dumps(allow, ensure_ascii=False)};
"""
    Path("app/web/static/screens.js").write_text(js, encoding="utf-8")
    Path("app/web/allowed_pages.json").write_text(
        json.dumps(allow, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    Path("work/allowed_pages.json").write_text(
        json.dumps(allow, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"wrote screens.js routes={len(screens)} allow={len(allow)}")


if __name__ == "__main__":
    main()
