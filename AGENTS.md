# AGENTS.md — Online-Lerncampus

**Diese Datei beschreibt nur dieses Repository.** Sie ist keine Spezifikation
fuer `siinanXD/bze-online-campus`.

Vor jeder Aenderung zuerst `docs/DECISIONS.md` lesen. **D-001 ist entschieden:
dieses Repository ist die Produktbasis.**

## Was dieses Repository ist

FastAPI-Lernplattform mit lokaler Vanilla-JS-Oberflaeche fuer den Pilotberuf
Maschinen- und Anlagenfuehrer (MAF), Metall- und Kunststofftechnik.

Es ist **nicht** die Next.js-/Supabase-Anwendung, die der Masterauftrag und
`docs/SPEC.md` im Geschwisterordner `../bze-online-campus` beschreiben.

## Stack (Ist, nicht Soll)

| Bereich | Technologie |
|---|---|
| Backend | FastAPI, Pydantic, Python 3.12+ |
| Daten | SQLite (`local.db`), Alembic-Migrationen, optional PostgreSQL |
| Frontend | `app/web/index.html` + `app.js` + `screens.js` + Token-CSS |
| Auth | Pseudonyme Lerner-ID, gehashte Bearer-Sessions, bcrypt |
| Tests | pytest unter `tests/` |
| Designquelle | lokale Datei `BZE Online Campus Fachkunde Designsystem.fig` |

## Verbindliche Dokumente in diesem Repo

1. `docs/DECISIONS.md` — offene Architekturentscheidungen
2. `docs/product/ROUTES.md` — tatsaechliche Seiten
3. `docs/product/FEATURES.md` — Funktionen und Luecken
4. `docs/product/IMPLEMENTATION_STATUS.md` — Status je Feature
5. `docs/content-governance.md` — Review, Quellen, PAL-/IHK-Grenze
6. `ARCHITECTURE.md` — Schichten dieses Repos

## Harte Grenzen

- Nicht auf `main` implementieren.
- Keine destruktiven Git-Operationen, kein Force-Push.
- `.env` nicht lesen, aendern oder ausgeben.
- Datenbank nicht zuruecksetzen.
- Nur additive Alembic-Migrationen.
- Keine echten PAL-/IHK-Pruefungsaufgaben.
- Figma ist Designreferenz, keine Routen- oder Geschaeftslogik-Quelle.
- Figma Make ist Prototyp, kein Produktcode.
- Kein paralleles zweites Produkt aufbauen. `../bze-online-campus` ist Referenz,
  nicht parallele Produktentwicklung.

## Befehle

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
pytest
```

## Geschwisterprojekt

`C:\dev\Repositories\bze-online-campus` → `siinanXD/bze-online-campus`

Dort liegen CLAUDE.md, AGENTS.md, Next.js 15, Supabase, MDX-Fachkunde und der
bereits als Welle 3 markierte Vertical Slice „Messschieber und Toleranzen“.
Das ist der im Masterauftrag genannte Produktstand — nicht dieser Ordner.
