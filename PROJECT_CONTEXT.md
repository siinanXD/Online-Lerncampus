# PROJECT_CONTEXT.md — Online-Lerncampus

Stand: 2026-08-13. Erstellt in Phase 0, weil die Datei fehlte.

## Auftrag

Lernplattform fuer technische Ausbildungsberufe. Pilot: Maschinen- und
Anlagenfuehrer/-in, Schwerpunkt Metall- und Kunststofftechnik, Kammer IHK
Aachen, Traeger BZE Euskirchen.

## Warum dieser Ordner nicht der im Auftrag genannte ist

Der Masterauftrag nennt `siinanXD/bze-online-campus` und einen
Next.js-/TypeScript-/Supabase-Stack. Dieser Workspace ist
`siinanXD/Online-Lerncampus`: FastAPI, Vanilla-JS, SQLite.

Beide Ordner liegen parallel unter `C:\dev\Repositories\`. Das ist der
offene Konflikt **D-001**.

## Wo die Daten herkommen

- Fachinhalte: Python-Bundles unter `app/data/content/`, Seed nach SQLite
- Plattform-Werkzeuge: `app/data/platform_content.py`
- Lernstand: SQLite-Tabellen ueber `app/services/database.py`
- Design: lokale `.fig`-Datei plus extrahierte Tokens in `app/web/static/tokens.css`

`CONTENT_REVIEW_REQUIRED` ist in `.env.example` `true`. Neue Einheiten starten
als `draft`. Ein Review-Bypass existiert nur, wenn dieser Schalter aus ist.

Die im Auftrag genannten Demo-Flags `AI_MOCK_MODE`, `CONTENT_SOURCE_MODE` und
`RAG_ENABLED` gibt es hier nicht. Vorhanden sind `AI_PROVIDER=disabled` und
`CONTENT_SOURCE=db|memory`.

## Was dem Code nicht anzusehen ist

- Inhalte sind pruefungsrelevant. Ein fachlicher Fehler ist falsch gelerntes
  Wissen, kein Anzeigefehler.
- Die 114 gerouteten Figma-Screens sind keine 114 fertigen Features. Viele
  sind Pixelrahmen; die Live-Bindung steht in
  `docs/design/frontend-structure.md`.
- Rollen im Login sind Demo-Praefixe (`azubi-`, `trainer-`, `admin-`,
  `reviewer-`), kein SSO und kein echtes Rechtesystem fuer Produktion.
