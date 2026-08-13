# FEATURES.md

Funktionen dieses Repositories. Prioritaet: echter Lernflow vor weiteren
Screens. Stand: 2026-08-13.

Legende: **existiert** · **teilweise** · **fehlt** · **blockiert**

## Teilnehmer — Lernen

| Feature | Status | Wo | Luecke |
|---|---|---|---|
| Login, Session, Logout, Passwort | existiert | Auth-Service | Demo-Praefix-Rollen, kein SSO |
| Onboarding + Consent | existiert | Privacy + Preferences | — |
| Dashboard mit XP, Level, Streak, offenen Fragen | existiert | `ProgressService.dashboard_summary` | Continue-Kette `messschieber` → `toleranzen-pruefen` |
| Fachkunde-Screen Messschieber 05.9 | existiert | `/fachkunde/messschieber` | Live-Fragen `m06-messschieber` + `POST /api/progress/attempt` |
| Fachkunde-Screen Toleranzfeld 05.7 | existiert | `/fachkunde/toleranz` | Rechner + Live-Fragen `m06-toleranzen-pruefen` + Attempt-API |
| 24-Monate-Lernreise | existiert | Curriculum + Journey-API | — |
| Lerneinheit lesen (Theorie, Glossar, Auftrag) | existiert | `GET /api/learning/units/{slug}` | Draft-Filter, wenn Review Pflicht |
| Frage beantworten + Mastery speichern | existiert | `POST /api/progress/attempt` | nur Index, keine Zeit/Hilfe/Fehlerart |
| Fuehrerschein-Mastery (1× + 2 richtig in Folge) | existiert | `QuestionProgress` | kein naechster Wiederholungstermin |
| Feedback richtig/falsch | existiert | Learn-Flow in `app.js` | — |
| Formeltrainer | existiert | `/api/formulas` | nicht an Messschieber-Unit gekoppelt |
| Fehlerdiagnose | existiert | `/api/diagnosis` | 8 Seed-Faelle, nicht curriculum-weit |
| Glossar / Uebersetzungshilfe | existiert | `/api/glossary` | Overlay nutzt Heuristik, nicht Frage-ID |
| Video-Lektion | teilweise | `/api/videos` | `video_url` leer, nur Metadaten/Fortschritt |
| Spritzgiesszyklus 05.8 | teilweise | lokale UI | keine Persistenz |
| Adaptive Wiederholung | fehlt | — | kein Intervall, kein naechster Termin |
| QuestionQuality-Modell (kognitiv, Kontext, Irrtuemer) | fehlt | `QuizQuestion` hat nur difficulty/exam_style/sources | eigener Schema-Slice |
| Offline-Sync | fehlt | — | kein Service Worker in diesem Repo |

## Teilnehmer — Pruefung und Fortschritt

| Feature | Status | Wo | Luecke |
|---|---|---|---|
| Pruefung starten, Antworten speichern, Frist, Abgabe | existiert | `ExamSessionService` | Fragenreihenfolge nicht explizit eingefroren dokumentiert |
| Ergebnis + Bestanden/Durchgefallen | existiert | Submit-Response | — |
| Schwache Themen | teilweise | Progress-Buckets | Screen 06.8 nicht voll gebunden |
| Kammertermine | fehlt | Screen 06.9 | keine Datentabelle |
| Pruefungsreife | teilweise | abgeleitet | keine serverseitige Empfehlung an Ausbilder |
| Heatmap / Verlauf / XP-Statistik | teilweise | Dashboard-Ableitung | Pixelrahmen 07.4–07.6 |

## Teilnehmer — Bericht und Profil

| Feature | Status | Wo | Luecke |
|---|---|---|---|
| Bericht anlegen, listen, signieren | existiert | Training-Reports | Kalender nur teilweise |
| Regel-Textvorschlag | existiert | `/api/training-reports/suggest` | kein LLM, bewusst |
| PDF-Export | existiert | `/export.pdf` | Layout grob |
| Datenexport / Kontoloeschung | existiert | Privacy-API | — |
| Coach / Lernplan | teilweise | regelbasiert aus Schwaechen | kein LLM |
| Leaderboard | existiert | `/api/leaderboard` | DSGVO-Risiko bei Klarnamen; pruefen |

## Ausbilder und Admin

| Feature | Status | Wo | Luecke |
|---|---|---|---|
| Review-Queue + Entscheidung | existiert | Content-Review-API | fachliche Freigabe fehlt inhaltlich |
| Kohorte / Risiko | teilweise | Trainer-APIs | Ownership nur grob |
| Berichtsheft-Freigabe | existiert | Trainer-Reports | — |
| Nutzer + Rollen aendern | existiert | Admin-Users | Praefix-Modell |
| Audit + Monitoring + Settings | existiert | Admin-APIs | Monitoring ist Zaehlstand, kein APM |
| Wissensdatenbank / RAG | fehlt | — | Auftrag nennt RAG; hier `AI_PROVIDER=disabled` |
| Qualitaetspruefer (7 Checks) | fehlt | — | kein automatischer Fragen-Quality-Gate |
| Medien-Binaerupload | fehlt | nur Metadaten | — |

## Content und Qualitaet

| Feature | Status | Wo | Luecke |
|---|---|---|---|
| 24 Monate, Kategorien, PAL-aehnliche Fragen | existiert | `app/data/content/` | Qualitaet ungleichmaessig, viele Definitionsfragen |
| Unit `messschieber` (DIN 862, Nonius, Fehler) | existiert | `m06_messschieber.py` | `review_status=draft` |
| Unit `toleranzen-pruefen` | existiert | `m06.py` Position 4 | `review_status=draft`, Kategorie `m06-toleranzen-pruefen` |
| Kategorie `m06-messschieber` + `m06-toleranzen-pruefen` | existiert | Subchapters + Questions | an Screens 05.9 / 05.7 gebunden |
| Quellenkatalog | existiert | `app/data/sources.py` | Fundstelle Seite/Abschnitt oft grob |
| Content-Factory | existiert | `ContentFactory` | erzeugt Drafts, kein Quality-Score |
| KI-generiert-Kennzeichnung | teilweise | Review-Status | kein sichtbares „ungeprueft“-Badge im Learn-UI |
| Demo-Flags laut Auftrag | fehlt | — | `AI_MOCK_MODE` / `CONTENT_SOURCE_MODE` / `RAG_ENABLED` nicht implementiert |

## Blockiert

_(D-001 entschieden. Keine Feature-Blockade.)_
