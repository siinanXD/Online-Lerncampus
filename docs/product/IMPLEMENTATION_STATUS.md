# IMPLEMENTATION_STATUS.md

Stand: 2026-08-13. D-001 entschieden. Messschieber + Toleranzfeld testbar.

Repo: `siinanXD/Online-Lerncampus` @ Branch `feat/messschieber-vertical-slice`.
Figma: `BZE Online Campus Fachkunde Designsystem.fig` (nicht Figma Make).

Statuswerte: geplant · in Arbeit · testbar · fertig · blockiert

## 0. Entscheidungen

- **D-001:** Produkt = dieses Repo (`Online-Lerncampus`).
- **D-005:** Screen 05.9 nutzt denselben Attempt-Pfad wie `/lernen/frage`.
- **D-006:** Screen 05.7 folgt derselben Referenz; Continue-Kette
  `messschieber` → `toleranzen-pruefen`.

## 1. Wiederverwendete Bausteine (Messschieber → Toleranz)

| Baustein | Wiederverwendung |
|---|---|
| `PILOT_CONTINUE_UNIT_SLUGS` / `resolve_continue_unit` | geordnete Continue-Kette |
| `category_mastery_counts` | kategoriebezogener Continue-Fortschritt |
| `POST /api/progress/attempt` + `QuestionProgress` | einzige Attempt-/Mastery-Logik |
| `GET /api/learning/units/{slug}` | Unit-Detail inkl. `review_status` |
| `GET /api/questions?category_slug=` | Uebungsfragen ohne Loesung |
| `POST /api/learning/units/{slug}/complete` | Unit abschliessen |
| `bindCategoryPracticeExercise` in `app.js` | gemeinsame Fachkunde-Uebungsbindung |
| Dashboard Fortsetzen → `/lernen/einheit` | Navigation |
| `CONTENT_REVIEW_REQUIRED` / `require_approved` | Drafts fuer Lerner unsichtbar |

Kein neues Schema, keine neue Progress-Tabelle, kein paralleler Toast-Pfad.

## 2. Vertical Slice „Messschieber“ — testbar

| Feld | Wert |
|---|---|
| Route | `/dashboard` → `/lernen/einheit` → `/fachkunde/messschieber` oder `/lernen/frage` |
| Daten | Unit `messschieber`, `m06-messschieber` |
| Tests | `tests/test_messschieber_slice.py` |

## 3. Vertical Slice „Toleranzfeld“ — testbar

| Feld | Wert |
|---|---|
| Ziel / Figma | 05.7 Toleranzfeld-Rechner + Uebung |
| Route | `/dashboard` (nach Messschieber-Complete) → `/lernen/einheit` → `/fachkunde/toleranz` |
| Rolle | `learner` |
| Daten | Unit `toleranzen-pruefen`, Kategorie `m06-toleranzen-pruefen` |
| Status | **testbar** |
| Risiken | Draft-Sperre bei `CONTENT_REVIEW_REQUIRED=true` (gewollt) |
| Tests | `tests/test_toleranz_slice.py` |

### Umgesetzt

1. Continue nach Messschieber-Complete zeigt `toleranzen-pruefen`.
2. Unit-Detail: Entwurf-Hinweis + Chip „Toleranzfeld-Übung“.
3. `/fachkunde/toleranz`: Rechner bleibt Lernhilfe; Quiz speichert via Attempt-API.
4. Review-Pflicht: Draft-Units/Fragen fuer Lerner unsichtbar (Test abgesichert).

### Akzeptanzkriterien

```text
[x] Fortsetzen oeffnet naechste unerledigte Pilot-Unit
[x] Entwurf-/Freigabestatus sichtbar (Demo ohne Review-Pflicht)
[x] Speichern nur ueber POST /api/progress/attempt
[x] dieselbe Kategorie-/Mastery-Logik
[x] keine Dummy-Toasts / keine neue Fortschrittstabelle
[x] Messschieber-Regressionstests gruen
[x] ROUTES / FEATURES / STATUS / D-006 aktualisiert
[ ] Playwright-E2E (keine Suite im Repo)
```

## 4. Gap-Rest

| Thema | Status |
|---|---|
| Spaced Repetition | fehlt |
| QuestionQuality-Modell | fehlt |
| Playwright-E2E | fehlt |
| Fachliche Freigabe der Draft-Units | offen (Prozess) |

## 5. Features (Kern)

| Feature | Status | Tests |
|---|---|---|
| Dashboard Continue Pilot-Kette | testbar | `test_messschieber_slice`, `test_toleranz_slice` |
| Messschieber-Slice | testbar | `test_messschieber_slice` |
| Toleranzfeld-Slice | testbar | `test_toleranz_slice` |
| Draft-Sichtbarkeit bei Review-Pflicht | testbar | `test_toleranz_slice` |
| Exam-Session | testbar | `test_exam_sessions` |
