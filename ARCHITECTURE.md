# ARCHITECTURE.md — Online-Lerncampus

Ist-Architektur dieses Repos. Nicht die Soll-Architektur aus
`../bze-online-campus/docs/ARCHITEKTUR.md`.

## Schichten

```text
app/web/          Seiten, Shells, Figma-Screens, Live-Binds
app/api/          duenne HTTP-Routen, Auth-Header, Rollenpruefung
app/schemas/      Pydantic-Antwort- und Request-Modelle
app/services/     Geschaeftslogik, Repositories, Seed, Sessions
app/models/       Domain-Dataclasses
app/data/         Curriculum, Fragen, Quellen, Plattform-Seed
app/db/           SQL-Schema-Texte
alembic/          additive Migrationen
tests/            pytest
```

## Regeln, die der Code bereits erzwingt

- Routen bleiben duenn. Validierung in Schemas, Logik in Services.
- Mutationen brauchen Bearer-Session. Trainer-/Admin-Endpunkte rufen
  `require_role(...)` serverseitig auf.
- Fragen-Mastery: mindestens einmal beantwortet und zweimal hintereinander
  richtig (`ProgressService.record_attempt`).
- Pruefungsversuche: Start, Ablauf, Antworten und Abgabe liegen serverseitig
  in `ExamSessionService`. Ein Browser-Timer allein reicht nicht.
- Content-Review: `draft → source_checked → approved`. Nur `approved` darf
  Azubis erreichen, wenn `CONTENT_REVIEW_REQUIRED=true`.
- Privacy Guard filtert offensichtliche Personenangaben in KI-/Review-Kontexten.

## Was hier bewusst nicht existiert

- Next.js App Router, Zod, Supabase RLS, pgvector, PWA-Outbox
- Zentrale TypeScript-`routes`-Map; die Route-Map ist
  `window.OLC_ROUTE_CONFIG` in `app/web/static/screens.js` plus
  `app/web/allowed_pages.json`
- Spaced-Repetition-Termin, Fehlerart, Hilfen-Zaehler, Bearbeitungszeit
  am einzelnen Versuch
