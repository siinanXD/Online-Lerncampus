# SECURITY.md — Online-Lerncampus

## Niemals

- `.env` lesen, aendern, committen oder ausgeben
- Secrets, Tokens oder persoenliche Schluessel in Docs, Logs oder Tests
- interne Exception-Details oder Stacktraces an den Client geben
- echte PAL-/IHK-Aufgaben importieren
- Normvolltexte (DIN/ISO) in die App kopieren

## Bereits umgesetzt

- Pseudonyme Lerner-ID aus keyed Hash, keine Klartext-E-Mail in der Lernlogik
- Bearer-Tokens nur gehasht in SQLite, mit Ablauf
- Passwoerter mit bcrypt
- Consent, Datenexport, Logout, Kontoloeschung
- Audit-Events fuer Attempt, Pruefungsstart und relevante Admin-Aktionen
- Privacy Guard gegen offensichtliche Personenangaben in Review-/KI-Kontexten

## Offen / nicht produktionsreif

- Rollen entstehen aus Login-Praefixen, nicht aus einem echten IAM
- SQLite lokal, kein RLS
- `APP_SECRET` hat einen unsicheren Default in der Settings-Klasse
- Oeffentliche Fehlertexte sind meist deutsch und fachlich, aber `debug=True`
  ist der lokale Default
