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

### Live (API-verdrahtet)

- Auth: Login, Logout, Passwort, `/api/auth/me` (Profil/Rolle), Onboarding-Consent → `/api/privacy/consent`
- Dashboard / Fortschritt: mastery, XP, Level, Streak, Reset (`POST /api/progress/reset`)
- Lernen: Fragen + Attempt, Lerneinheiten-Liste, Unit-Detail via `/api/learning/units/{slug}`
- Lernpfad: Journey + Curriculum/Occupations/Sources
- Pruefung: Sessions, Choice-Answers, **Open-Answers**, Submit (Checkpoint-Exams)
- Berichtsheft: Create + Liste + Submit/Update (`PUT /api/training-reports/{id}`)
- Privacy: Export, Account-Delete, Consent
- Gamification: `/api/gamification` (XP/Level/Streak/Badges aus Progress+Audit)
- KI-Coach / Lernplan: `/api/coach/plan` (regelbasiert aus Schwaechen/Journey)
- Ausbilder Review: Pending-Queue + Approve/Needs-Revision (`/api/content/review/decision`), Draft-Generate + `/api/content/review`
- Rollen-Gate: Trainer/Admin-Layouts nur fuer `reviewer|trainer|admin`

### Noch Shell / teilweise statisch

- Marketing/Landing-Illustrationen, Level-Up-Animation, Sprache
- Formeltrainer / Fehlerdiagnose / Video / Flashcard / Uebersetzungshilfe (Demo-Toasts)
- Berichtsheft KI-Assistent, Kalender, PDF-Export-UI (ohne Server-PDF)
- Ausbilder: Teilnehmer-CRUD, Kohorten-Risiko-Tabellen, Medien-Upload, Editor-Voll-CRUD
- Admin: Nutzerverwaltung, Monitoring-Charts, Import/Dubletten, Audit-UI (nur Shell)
- Gamification-Leaderboard (nur eigener Streak/Badges, keine Kohorten-Rangliste)

## Dateien

- `app/web/static/tokens.css` — BZE Tokens aus `.fig`
- `app/web/static/ui.css` — Komponenten + Shells auf Tokens
- `app/web/static/screens.js` — generiertes Screen-Registry (+ Live-Binds)
- `app/web/static/app.js` — Routing + API-Binds
- `app/web/index.html` — Landing/Login/App/Trainer/Admin Shells
- `app/web/pages.py` + `allowed_pages.json` — FastAPI Page-Allowlist
- `docs/design/screens.md` — Inventar mit Completion-Checkboxen
