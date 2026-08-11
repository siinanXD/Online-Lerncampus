# Content-Governance

Wie Lerninhalte entstehen, belegt werden und freigegeben werden. Dieses Dokument
haelt die Regeln fest, die der Code technisch erzwingt.

## Review-Kette

Jede Lerneinheit und jede Frage durchlaeuft `ReviewStatus`:

`draft` → `source_checked` → `approved`

`needs_revision` fuehrt zurueck auf `draft`. **Nur `approved` darf Azubis
erreichen.** Der Test `test_learning_units_start_unapproved` stellt sicher, dass
neue Inhalte nicht versehentlich als freigegeben ausgeliefert werden.

## Quellenbindung

Jede Einheit fuehrt `source_keys`, die auf `app/data/sources.py` zeigen. Der
Test `test_every_learning_unit_cites_known_sources` bricht den Build, wenn
Inhalte eine unbekannte Quelle zitieren. Damit gibt es keine Inhalte ohne
nachvollziehbaren Beleg.

## Was NICHT uebernommen werden darf

Diese Grenzen sind rechtlich, nicht stilistisch:

- **Originale IHK-/PAL-Pruefungsaufgaben.** Sie sind urheberrechtlich geschuetzt.
  Die Fragen in diesem Repository sind eigenstaendig formuliert und orientieren
  sich nur am *Format*. Kein Inhalt darf als „offizielle IHK-Frage" ausgewiesen
  werden, solange dafuer keine Lizenz vorliegt.
- **Normtexte (DIN, ISO).** DIN 862 und DIN EN ISO 1 sind kostenpflichtig und
  geschuetzt. Anforderungen duerfen **in eigenen Worten** wiedergegeben und mit
  Nummer und Titel zitiert werden — der Normtext selbst nicht.
- **Wikipedia-Text.** Wikipedia steht unter CC BY-SA 4.0. Wer Text uebernimmt,
  muss Autoren und Lizenz nennen **und das Ergebnis selbst unter CC BY-SA
  stellen** (Share-alike). Das faerbt auf ein kommerzielles Produkt ab. Deshalb:
  Wikipedia als *Rechercheeinstieg* nutzen, Inhalte eigenstaendig formulieren,
  gegen eine Fachquelle pruefen. Wird doch uebernommen, gehoert das in
  `sources.py` mit Lizenzvermerk.

## Fachliche Freigabe

Automatisch erzeugte oder KI-gestuetzte Entwuerfe sind **Vorschlaege**. Vor
`approved` braucht es eine fachkundige Person (Ausbilder/-in oder
Reviewer-Rolle), die Richtigkeit und Pruefungsrelevanz bestaetigt. Der
Privacy Guard (`app/services/privacy_guard.py`) haelt zusaetzlich
personenbezogene Daten aus Generierungs- und Review-Kontexten heraus.

## Offener Punkt

Die aktuell hinterlegten Einheiten stehen auf `draft`. Sie sind fachlich sorgfaeltig
formuliert, aber **noch nicht durch eine ausbildende Fachkraft freigegeben**.
