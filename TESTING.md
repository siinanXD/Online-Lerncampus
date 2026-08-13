# TESTING.md — Online-Lerncampus

## Vorhanden

```powershell
pytest
```

Wichtige Dateien:

| Datei | Prueft |
|---|---|
| `tests/test_api.py` | Kern-API, Curriculum, Fragen |
| `tests/test_auth_flow.py` | Login, Session, Logout |
| `tests/test_exam_sessions.py` | serverseitige Pruefungsversuche |
| `tests/test_frontend_wiring.py` | Auth/me, Reset, Gamification, Coach |
| `tests/test_platform_api.py` | Formeln, Diagnose, Trainer, Admin |
| `tests/test_learning_units.py` | Einheiten, Quellen, Draft-Start |
| `tests/test_content_*.py` | Seed, Schema, Factory, JSON-Bundle |
| `tests/test_review_and_reports.py` | Review-Queue, Berichtsheft |

Es gibt **kein Playwright** und keine E2E-Suite fuer den Teilnehmer-Flow im
Browser.

## Regel fuer neue Arbeit

- Bestehende pytest-Datei des betroffenen Dienstes zuerst ausfuehren.
- Neue Service-Logik bekommt einen gezielten Test, keinen Screenshot-Test.
- Ein Teilnehmer-Flow gilt erst als testbar, wenn Attempt, Mastery und
  Dashboard-Aktualisierung serverseitig geprueft sind.
- Keine Secrets in Tests. Demo-Login: `azubi-<uuid>` / `demo-pass`.
