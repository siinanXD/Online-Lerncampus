# ROUTES.md

Verbindlich fuer tatsaechlich vorhandene Seiten in **diesem** Repository.
Quelle im Code: `app/web/static/screens.js` (`OLC_ROUTE_CONFIG`) und
`app/web/allowed_pages.json`.

Rollen-Ist: `learner` (Teilnehmer), `trainer`, `reviewer`, `admin`.
Frontend-Gates allein reichen nicht; Mutationen prueft `require_role`.

Status-Werte: **live** (API-Daten), **teilweise** (Screen + Teilbindung),
**shell** (Figma-Pixel, lokal oder Dummy).

## Teilnehmer

| Route | Figma | Zweck | Datenquelle | Zustaende | Status |
|---|---|---|---|---|---|
| `/` | 01.5 | Landing | statisch | — | shell |
| `/login` | 01.1 | Login / Onboarding-Einstieg | `POST /api/auth/login` | Error | live |
| `/passwort` | 01.2 | Passwort aendern | `POST /api/auth/password` | Error | live |
| `/sprache` | 01.3 | Sprache | `PUT /api/me/preferences` | Loading | live |
| `/onboarding` | 01.4 | Willkommen + Consent | `POST /api/privacy/consent`, `POST /api/auth/onboarding/complete` | Error | live |
| `/dashboard` | 19.1 / 03.1 | Lernstand, XP, Fortsetzen | `GET /api/dashboard` (`continue_slug` → Pilot `messschieber` → `toleranzen-pruefen`) | Loading, Empty | live |
| `/dashboard/fortsetzen` | 03.5 | Naechste Einheit | Dashboard + Units (`open-unit` → `/lernen/einheit`) | Empty | live |
| `/dashboard/tagesziel` | 03.2 | Tagesziel | `GET /api/daily-goal` | Empty | teilweise |
| `/dashboard/streak` | 03.3 | Streak | Gamification | Empty | teilweise |
| `/lernen` | 19.2 | Lernreise / Hub | `GET /api/learning/journey`, `/api/learning/units` | Loading, Empty | live |
| `/lernen/fragen` | 04.3 | Fragenliste | `GET /api/questions` | Loading, Empty | live |
| `/lernen/fragen/fehler` | 04.4 | Fehlerliste | `GET /api/progress` | Empty | live |
| `/lernen/frage` | 04.5 | Multiple Choice | `POST /api/progress/attempt` | Error | live |
| `/lernen/frage/freitext` | 04.6 | Freitext-Uebung | lokal / Open-Question-API | Error | teilweise |
| `/lernen/feedback/richtig` | 04.7 | Feedback richtig | letzter Attempt | — | live |
| `/lernen/feedback/falsch` | 04.8 | Feedback falsch | letzter Attempt | — | live |
| `/lernen/einheit` | 04.17 | Lerneinheit | `GET /api/learning/units/{slug}` | Loading, Empty, Error | live |
| `/lernen/formeltrainer` | 04.11 | Formeln | `GET/POST /api/formulas` | Empty | live |
| `/lernen/fehlerdiagnose` | 04.12 | Diagnose | `GET/POST /api/diagnosis` | Empty | live |
| `/lernen/video` | 04.13 | Video | `GET/POST /api/videos` | Empty; Datei fehlt | teilweise |
| `/lernen/glossar` | 04.18 | Glossar | `GET /api/glossary` | Empty | live |
| `/fachkunde` | 05.1 | Fachkunde-Hub | Units + Screens | Empty | teilweise |
| `/fachkunde/lernpfad` | 05.2 | Lernpfad | Journey | Empty | teilweise |
| `/fachkunde/einheit` | 05.3 | Fachkunde-Einheit | Units | Loading | teilweise |
| `/fachkunde/messschieber` | 05.9 | Messschieber-Uebung | `GET /api/questions?category_slug=m06-messschieber`, `POST /api/progress/attempt` | Loading, Empty, Error | **live** |
| `/fachkunde/toleranz` | 05.7 | Toleranzfeld + Uebung | Rechner-UI + `GET /api/questions?category_slug=m06-toleranzen-pruefen`, `POST /api/progress/attempt` | Loading, Empty, Error | **live** |
| `/fachkunde/spritzguss` | 05.8 | Spritzgiesszyklus | lokale UI-Logik | — | shell |
| `/fachkunde/glossar` | 05.4 | Fachkunde-Glossar | Glossary-API oder Screen | Empty | teilweise |
| `/fachkunde/abschluss` | 05.5 | Einheit fertig | `POST /api/learning/units/{slug}/complete` | — | teilweise |
| `/pruefungen` | 19.3 / 06.1 | Pruefungsliste | `GET /api/exams` | Loading, Empty | live |
| `/pruefungen/frage` | 06.2 | Pruefungsfrage | Exam-Session-API | Error, Timer | live |
| `/pruefungen/uebersicht` | 06.3 | Fragenuebersicht | Session-State | — | live |
| `/pruefungen/abgabe` | 06.5 | Abgabe | `POST .../submit` | Confirm | live |
| `/pruefungen/bestanden` | 06.6 | Ergebnis bestanden | Submit-Response | — | live |
| `/pruefungen/durchgefallen` | 06.7 | Ergebnis nicht bestanden | Submit-Response | — | live |
| `/pruefungen/schwach` | 06.8 | Schwache Themen | Progress | Empty | teilweise |
| `/pruefungen/kammertermine` | 06.9 | Kammertermine | Screen | Empty | shell |
| `/pruefungen/timer` | 06.4 | Timer-Ansicht | Session `expires_at` | — | teilweise |
| `/fortschritt` | 19.4 / 07.1 | Fortschritt | Dashboard + Progress | Loading, Empty | live |
| `/fortschritt/pruefungsreife` | 07.2 | Pruefungsreife | Dashboard-Ableitung | Empty | teilweise |
| `/fortschritt/heatmap` | 07.6 | Themen-Heatmap | Progress | Empty | teilweise |
| `/berichtsheft` | 08.1 | Berichtsliste | Training-Reports-API | Loading, Empty | live |
| `/berichtsheft/neu` | 08.2 | Neuer Eintrag | `POST /api/training-reports` | Error | live |
| `/berichtsheft/ki` | 08.3 | Textvorschlag | `GET /api/training-reports/suggest` | Empty | teilweise |
| `/berichtsheft/unterschrift` | 08.4 | Signatur | Report-Update | Error | live |
| `/berichtsheft/export` | 08.6 | Export | `GET .../export` und `.pdf` | Error | live |
| `/berichtsheft/kalender` | 08.5 | Kalender | Reports, Pixelrahmen | Empty | teilweise |
| `/mehr` | 19.5 / 09.1 | Profil-Hub | `GET /api/auth/me` | — | live |
| `/mehr/profil` | 09.1b | Profil | me + Preferences | — | live |
| `/mehr/darstellung` | 09.1c | Theme / Kontrast | Preferences | — | live |
| `/mehr/benachrichtigungen` | 09.1d | Toggles | Notification-Settings | — | live |
| `/mehr/export` | 09.5 | Datenexport | `GET /api/privacy/export` | Error | live |
| `/mehr/loeschen` | 09.6 | Kontoloeschung | `DELETE /api/privacy/account` | Confirm, Error | live |
| `/mehr/logout` | 09.7 | Logout | `POST /api/auth/logout` | Confirm | live |
| `/mehr/coach` | 09.3 | Coach-Chat | `POST /api/coach/chat` | Empty, Error | teilweise |
| `/mehr/lernplan` | 09.4 | Lernplan | `GET /api/coach/plan` | Empty | teilweise |
| `/datenschutz` | — | Privacy-Aktionen | Privacy-API | Error | live |
| `/defizite` | — | Offene / falsche Fragen | Progress | Empty | live |
| `/lernreise` | — | 24-Monate-Reise | Journey-API | Empty | live |

Legacy-Aliase (`/dashboard/legacy`, `/lernen/hub-legacy`, …) bleiben als
Figma-Vergleichsrahmen. Sie sind keine Produktrouten.

## Ausbilder

Prefix `/ausbilder/*`. Rolle: `trainer` oder `reviewer` oder `admin`.

| Route | Figma | Zweck | Datenquelle | Status |
|---|---|---|---|---|
| `/ausbilder` | 11.1 | Cockpit | `GET /api/trainer/learners` | teilweise |
| `/ausbilder/teilnehmer` | 11.2 | Teilnehmerliste | Trainer-Learners | teilweise |
| `/ausbilder/kohorte` | 11.6 | Kohortenvergleich | Learners | teilweise |
| `/ausbilder/risiko` | 11.4 | Risiko | `GET /api/trainer/risk` | teilweise |
| `/ausbilder/hotspots` | 11.5 | Heatmap | Risk + Progress | teilweise |
| `/ausbilder/pruefungsreife` | 11.3 | Reife-Dialog | Learners | teilweise |
| `/ausbilder/review` | 12.1 | Review-Queue | `GET /api/content/reviews` | live |
| `/ausbilder/review/detail` | 12.2 | Review-Detail | Review-Decision-API | live |
| `/ausbilder/fragen` | 12.3 | Fragenverwaltung | Questions | teilweise |
| `/ausbilder/generator` | 12.4 | Content-Factory | `POST /api/content/generate` | teilweise |
| `/ausbilder/freigabe` | 12.7 | Freigabe | Review-API | teilweise |
| `/ausbilder/berichte` | 13.1 | Berichtsheft-Pruefung | `GET /api/trainer/reports` | live |
| `/ausbilder/medien` | 12.9 | Medien-Metadaten | `GET/POST /api/media` | teilweise |

## Admin

Prefix `/admin/*`. Rolle: `admin`.

| Route | Figma | Zweck | Datenquelle | Status |
|---|---|---|---|---|
| `/admin` | 14.1 / 16.1 | Admin-Hub | Monitoring + Users | teilweise |
| `/admin/nutzer` | 15.1 | Nutzerliste | `GET /api/admin/users` | live |
| `/admin/nutzer/detail` | 15.2 | Nutzerdetail | Users + Role-Update | live |
| `/admin/audit` | 15.3 | Audit | `GET /api/admin/audit` | live |
| `/admin/einstellungen` | 15.4 | Settings | `GET/PUT /api/admin/settings` | live |
| `/admin/monitoring` | 15.5 | Monitoring | `GET /api/admin/monitoring` | live |
| `/admin/zugangsdaten` | 15.6 | Zugang drucken | Users | shell |
| `/admin/content` | 16.1 | Content-Dashboard | `GET /api/content/stats` | teilweise |
| `/admin/dubletten` | 16.11 | Dubletten | `GET /api/admin/duplicates` | live |
| `/admin/quiz` | 16.6 | Quiz-Verwaltung | Questions | teilweise |
| `/admin/wissen` | 16.4 | Wissensdatenbank | nicht vorhanden | shell |
| `/admin/lernziele` | 16.5 | Rahmenlehrplan | Curriculum-API | teilweise |

## Pflichtfelder fuer jede neue Seite

Route, Rolle, Zweck, Parameter, Datenquelle, Loading, Empty, Error,
Offline falls relevant, Akzeptanzkriterien, Eintrag in dieser Datei,
Figma-Name `Route: /...`.
