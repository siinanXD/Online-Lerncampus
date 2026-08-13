# Entscheidungen

Nur konkrete, belastbare Entscheidungen. Keine Absichtserklaerungen.

## D-001 — Welche Codebasis ist das Produkt? (ENTSCHIEDEN)

**Entscheidung (2026-08-13):** Produktwahrheit ist
`siinanXD/Online-Lerncampus` (dieses Repository, FastAPI + Vanilla-JS +
SQLite). Remote: https://github.com/siinanXD/Online-Lerncampus.git

Der Geschwisterordner `../bze-online-campus` ist Referenz und paralleler
Stand, aber **kein** zweites Produkt, das hier nachgebaut wird. Stack,
Routen und Features folgen dem Ist dieses Repos. Auftragstext (Next.js/
Supabase) gilt hier nicht als technische Wahrheit.

**Status:** entschieden. Feature-Slices in diesem Repo sind freigegeben.

## D-005 — Messschieber-Antwortpfad (fest)

Screen `/fachkunde/messschieber` (Figma 05.9) nutzt dieselbe API wie
`/lernen/frage`: `GET /api/questions?category_slug=m06-messschieber` und
`POST /api/progress/attempt`. Kein paralleler Dummy-Toast-Pfad.

## D-006 — Toleranzfeld folgt Messschieber-Referenz (fest)

Screen `/fachkunde/toleranz` (Figma 05.7) ist der zweite Pilot-Slice und
folgt derselben Bausteine:

- Unit `toleranzen-pruefen` / Kategorie `m06-toleranzen-pruefen`
- Speichern nur ueber `POST /api/progress/attempt`
- Continue-Reihenfolge: `messschieber` → `toleranzen-pruefen`
  (`PILOT_CONTINUE_UNIT_SLUGS`)
- Rechner-UI bleibt Lernhilfe; Uebungsantworten sind keine lokalen Toasts

`CONTENT_REVIEW_REQUIRED=true` haelt Drafts fuer Lerner unsichtbar.

## D-002 — Figma ist Design, nicht Route (fest)

Figma-Datei: `BZE Online Campus Fachkunde Designsystem.fig`
(Online-Key im Geschwisterrepo: `wr0cGrNxC6kpOV1TalCgx9`).

Ein Screen erzeugt keine Route, keine Tabelle und keine Rolle. Die
verbindliche Route-Map dieses Repos ist `docs/product/ROUTES.md`.

## D-003 — Review-Bypass nur ohne Review-Pflicht (fest)

`CONTENT_REVIEW_REQUIRED=true` ist der dokumentierte Default.
Einheiten und Fragen starten als `draft`. Freigabe nur durch Reviewer,
Trainer oder Admin. Ein Bypass ist nur erlaubt, wenn der Schalter
ausdruecklich aus ist (lokaler Demo-/Seed-Fall).

## D-004 — Rollen-Ist vs. Rollen-Soll (offen, nicht blockierend)

Auftrag: `participant | trainer | admin`.
Ist: `learner | reviewer | trainer | admin`.

`reviewer` ist im Code eine eigene Rolle fuer die Content-Queue.
Umbenennung waere ein eigener, kleiner Slice nach D-001. Nicht nebenbei.
