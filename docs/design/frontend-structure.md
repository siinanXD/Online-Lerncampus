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
- Dashboard / Fortschritt: `/dashboard` ist Figma **03.1** (`169:879`, helles Stone-UI, Tabs Start · Lernen · Prüfung · Bericht · Mehr); mastery, XP, Level, Streak, Reset, Tagesziel, Unit-Abschluss. Altes dunkles 19.1-Hub liegt unter `/dashboard/legacy`.
- Lernen: Fragen + Attempt, Lerneinheiten-Liste, Unit-Detail, `POST /api/learning/units/{slug}/complete`
- Formeltrainer, Fehlerdiagnose, Videolektionen, Uebersetzungshilfe (Glossary)
- Lernpfad: Journey + Curriculum/Occupations/Sources
- Pruefung: Sessions, Choice-Answers, Open-Answers, Submit (Checkpoint-Exams)
- Berichtsheft: Create + Liste + Submit/Update, Signatur, Regel-Vorschlag, Text-Export
- Privacy: Export, Account-Delete, Consent
- Gamification: `/api/gamification` plus Kohorten-Leaderboard (`/api/leaderboard`)
- KI-Coach / Lernplan: `/api/coach/plan` (regelbasiert aus Schwaechen/Journey)
- Sprache, Darstellung, Benachrichtigungs-Toggles: `/api/me/preferences`, `/api/me/notifications/settings`
- Content-Meldung: `POST /api/content/flags`
- Ausbilder: Review-Queue, Kohorte, Risiko-Radar, Berichtsheft-Freigabe, Medien-Metadaten
- Admin: Nutzerliste, Rollen, Monitoring, Audit, Dubletten, Settings
- Rollen-Gate: Trainer/Admin-Layouts nur fuer `reviewer|trainer|admin`

### Noch Shell / teilweise statisch

- Marketing/Landing-Illustrationen, Level-Up-Animation (XP kommt live, Animation bleibt UI)
- Berichtsheft-Kalender-Pixelrahmen (Daten liegen in `/api/training-reports`)
- Echte Videodateien und binaerer Medien-Upload (nur Metadaten/URL im MVP)
- LLM-gestuetzter Berichtsheft-Text (Regelgenerator statt externem KI-Provider)

## Dateien

- `app/web/static/tokens.css` — BZE Tokens aus `.fig`
- `app/web/static/ui.css` — Komponenten + Shells auf Tokens
- `app/web/static/screens.js` — generiertes Screen-Registry (+ Live-Binds)
- `app/web/static/app.js` — Routing + API-Binds
- `app/web/index.html` — Landing/Login/App/Trainer/Admin Shells
- `app/web/pages.py` + `allowed_pages.json` — FastAPI Page-Allowlist
- `docs/design/screens.md` — Inventar mit Completion-Checkboxen
