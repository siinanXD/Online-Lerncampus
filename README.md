# Online Lerncampus

DSGVO-bewusste Lernplattform fuer technische Ausbildungsberufe. Der MVP startet mit Maschinen- und Anlagenfuehrer/-in, Schwerpunkt Metall- und Kunststofftechnik.

## Umfang des ersten MVP

- FastAPI Backend
- Lokale Web-App unter `/`
- 24-Monats-Curriculum fuer Maschinen- und Anlagenfuehrer
- 240 Fragekategorien: 24 Monate mit je 10 Unterkapiteln
- 20 PAL-aehnliche Testpruefungen mit je 10 Single-Choice-Fragen
- Kapitel 1 mit Fachkunde, 10 Unterkapiteln und eigenen Pruefungsfragen
- Quellenkatalog mit IHK Aachen, BZE Euskirchen, BIBB und Ausbildungsverordnung
- Content-Factory fuer erste Lernmissions-Entwuerfe
- Review-Workflow: Entwurf, Quellencheck, Fachreview, Freigabe
- Privacy Guard gegen offensichtliche personenbezogene Daten in KI-/Review-Kontexten
- Pseudonymer Login fuer Azubis ohne Klartext-E-Mail-Speicherung im MVP
- Persistenter SQLite-Lernstand fuer lokale Entwicklung
- Gehashte Bearer-Sessions mit Ablaufzeit und Logout
- Serverseitige Fuehrerschein-App Lernlogik: Jede Frage muss mindestens einmal
  beantwortet und zweimal hintereinander richtig geloest werden.
- Falsch beantwortete Fragen werden serverseitig je pseudonymer Lerner-ID
  getrackt, um Defizite je Kategorie sichtbar zu machen.
- Dashboard mit Level, XP, offenen Fragen, Defiziten und 24-Monate-Lernreise
- Datenschutzfunktionen: Einwilligung, Datenexport und Kontoloeschung

## Lokal starten

```powershell
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Danach:

- API: http://127.0.0.1:8000
- Landingpage: http://127.0.0.1:8000
- Login: http://127.0.0.1:8000/login
- Dashboard: http://127.0.0.1:8000/dashboard
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/health

Demo-Login: `azubi-bze-01` / `demo-pass`, Kohorte `BZE-2026-F`.
Ausbilder: `trainer-demo` / `demo-pass`. Admin: `admin-demo` / `demo-pass`.

## Am Handy ansehen

Die App ist responsive. `127.0.0.1` funktioniert nur auf dem Rechner, auf dem der Server laeuft.

**Gleiches WLAN:** Server mit `--host 0.0.0.0` starten, dann auf dem Handy `http://<LAN-IP>:8000` oeffnen.

**Oeffentliche URL (Railway):** https://web-production-5f260.up.railway.app

```bash
docker build -t online-lerncampus .
docker run --rm -p 8000:8000 -e APP_ENV=preview -e APP_SECRET=bitte-aendern-16plus online-lerncampus
```

Preview-Tunnel (Cloudflare Quick Tunnel) sind nur solange erreichbar, wie der Agent bzw. `cloudflared` laeuft. Keine echten Azubi-Daten darueber speichern.

## Browser-Routen

- `/` Landingpage
- `/funktionen` Feature-Uebersicht
- `/login` Login und Onboarding
- `/dashboard` Lernstand, XP und Defizit-Kurzuebersicht
- `/lernreise` 24-Monate-Ausbildungsreise
- `/lernen` Kapitel 1, Fachkunde und Quiz
- `/pruefungen` 20 Testpruefungen
- `/defizite` offene Fragen und Fehlertracking
- `/review` Content Factory und Datenexport-Anzeige
- `/datenschutz` Datenschutzaktionen fuer Einwilligung, Export, Logout und Loeschung

## Wichtige Endpunkte

- `GET /api/occupations`
- `GET /api/occupations/maschinen-und-anlagenfuehrer/curriculum`
- `GET /api/occupations/maschinen-und-anlagenfuehrer/modules`
- `GET /api/sources`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/logout`
- `POST /api/auth/password`
- `POST /api/privacy/consent`
- `GET /api/privacy/export`
- `DELETE /api/privacy/account`
- `GET /api/dashboard`
- `GET /api/learning/journey`
- `GET /api/learning/first-chapter`
- `GET /api/questions/categories`
- `GET /api/questions?month=1`
- `GET /api/exams`
- `GET /api/exams/exam-01`
- `POST /api/progress/attempt`
- `POST /api/progress/reset`
- `POST /api/content/generate`
- `POST /api/content/review`

## DSGVO-Startprinzip

Der MVP trennt Fachinhalte von Lerndaten. Der Login erzeugt aus der Kennung per
gekeytem Hash eine pseudonyme Lerner-ID. Bearer-Tokens werden nur gehasht in
SQLite gespeichert und laufen ab. Die Lernlogik speichert Fortschritt,
Fehlerzaehler und Streaks je pseudonymer ID. Keine Klartext-E-Mail wird fuer die
Lernlogik abgelegt.

Bereits umgesetzt sind Datenschutzbestaetigung, Datenexport, Logout und
Kontoloeschung. Fuer produktive Accounts, Klassenraeume oder
Ausbilder-Dashboards muessen als naechste Stufe ein vollstaendiges Rollenmodell,
Rechtsgrundlagen je Nutzergruppe, Aufbewahrungsfristen,
Auftragsverarbeitungsvertraege, Backups mit Loeschkonzept und ein echtes
Passwort-/SSO-System umgesetzt werden.

## Beispiel: Content-Entwurf generieren

```json
{
  "occupation_slug": "maschinen-und-anlagenfuehrer",
  "specialization_slug": "metall-und-kunststofftechnik",
  "month": 8,
  "learner_level": "azubi"
}
```

## Naechste Ausbaustufe

- PostgreSQL und Alembic-Migrationen
- Auth mit Rollen fuer Azubi, Ausbilder, Reviewer und Admin
- Source Ingestion fuer HTML/PDF
- Chunking und Embeddings
- Vektor-Datenbank
- LLM-Provider mit deaktiviertem Training und EU-konformer Verarbeitung
- Persistenter Lernstand mit pseudonymen Nutzer-IDs
- Ausbilder-Dashboard fuer Defizite nur mit klarer Rechtsgrundlage
