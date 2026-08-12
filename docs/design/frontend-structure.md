# Frontend-Struktur (Figma → Code)

Quelle: `BZE Online Campus Fachkunde Designsystem.fig`  
Extraktion: `python tools/figma_extract.py "...fig" --css app/web/static/tokens.css --screens docs/design/screens.md`  
Screen-Katalog: `python tools/generate_screen_catalog.py && python tools/generate_frontend_screens.py`

## Shells

| Rolle | Layout | Chrome |
|-------|--------|--------|
| Teilnehmer | `app` (mobile) | Tab-Bar `Start · Lernen · Pruefung · Bericht · Mehr` |
| Auth | `auth` / `login` | Auth-Cards ohne Tab-Bar |
| Ausbilder | `trainer` (desktop) | Top-Nav Cockpit · Review · Content · Berichte |
| Admin | `admin` (desktop) | Top-Nav Nutzer · Content · Monitoring · Audit |

## Status

**114 produktive Screens** aus dem Designsystem sind geroutet und gerendert
(`app/web/static/screens.js`, Allowlist `app/web/allowed_pages.json`).

Abgedeckt (App-Screens 01–16 + Gamification 18, ohne Foundations/Prototypen-Doku):

- Auth: Login, Passwort, Sprache, Onboarding, Level-Up, Landing
- Teilnehmer 03–09: Dashboard-Varianten, Lernen/Fachkunde-Tools, Pruefung, Fortschritt, Berichtsheft, Mehr/Coach/Export
- Ausbilder 10–13: Cockpit, Teilnehmer, Review, Content, Berichte/Planung
- Admin 14–16: Nutzer, Audit, Monitoring, Content-Ops, Import/Dubletten
- Gamification 18: Uebersicht, XP, Badges, Streaks

API-Wiring wo vorhanden: Auth, Dashboard, Fragen/Mastery, Exams, Berichtsheft, Content-Review/Generate, Privacy-Export.

## Dateien

- `app/web/static/tokens.css` — BZE Tokens aus `.fig`
- `app/web/static/ui.css` — Komponenten + Shells auf Tokens
- `app/web/static/screens.js` — generiertes Screen-Registry
- `app/web/static/app.js` — Routing + API-Binds
- `app/web/index.html` — Landing/Login/App/Trainer/Admin Shells
- `app/web/pages.py` + `allowed_pages.json` — FastAPI Page-Allowlist
- `docs/design/screens.md` — Inventar mit Completion-Checkboxen
