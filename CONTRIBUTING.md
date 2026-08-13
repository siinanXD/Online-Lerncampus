# CONTRIBUTING.md — Online-Lerncampus

1. Nicht auf `main` arbeiten. Feature-Branch, dann Review.
2. Phase 0 vor Code: Bestand suchen, Luecke benennen, kleinsten Slice planen.
3. Eine Funktion ist ein Vertical Slice, kein isolierter Screen.
4. Figma nicht in Routen oder Tabellen uebersetzen.
5. Bestehende Mastery-, Pruefungs- und Review-Logik wiederverwenden.
6. Nur additive Migrationen. Kein `db reset`.
7. Tests gezielt ausfuehren. Siehe `TESTING.md`.
8. `docs/product/IMPLEMENTATION_STATUS.md` und bei neuen Seiten
   `docs/product/ROUTES.md` im selben Slice aktualisieren.
9. `docs/DECISIONS.md` aktualisieren, wenn sich eine Architekturentscheidung
   aendert. D-001 ist entschieden (dieses Repo).
