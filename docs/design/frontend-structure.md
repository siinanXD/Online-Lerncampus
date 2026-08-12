# Frontend-Struktur (Figma → Code)

Quelle: `BZE Online Campus Fachkunde Designsystem.fig`  
Extraktion: `python tools/figma_extract.py "...fig" --css app/web/static/tokens.css --screens docs/design/screens.md`

## Shell (Figma 02)

Tab-Bar laut Dashboard-Frame:

`Start · Lernen · Pruefung · Bericht · Mehr`

## Umgesetzte Kernscreens

| Route | Figma | Umsetzung |
|-------|-------|-----------|
| `/` | 01.5 Landing | Hero + Features + Trust |
| `/login` | 01.1 Login | Logo, Formular, Demo-CTA |
| `/dashboard` | 03.1 Dashboard | Greeting, Fortsetzen, Tagesziel, Stats, Wochenbericht |
| `/lernen` | 04.1 Lernen Hub | Hub-Karten → Fragen / Einheiten |
| `/pruefungen` | 06.x | Session-UI + API |
| `/berichtsheft` | 08.x | Liste + neuer Eintrag |
| `/defizite` | 07.x | Mastery/Defizite |
| `/mehr` | 09.x | Profil/Konto |

## Dateien

- `app/web/static/tokens.css` — BZE Tokens aus `.fig`
- `app/web/static/ui.css` — Komponenten auf Tokens
- `app/web/index.html` — Landing/Login/App-Shell
- `app/web/static/app.js` — Routing + API

## Naechste Pixel-Passungen

Ausbilder (10–13) und Admin (14–16) noch Stub/Backend-only.
