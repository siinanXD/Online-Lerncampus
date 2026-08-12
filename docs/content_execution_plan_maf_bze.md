# Content-Ausfuehrungsplan: MAF · IHK Aachen · BZE

Projekt: Online Lerncampus  
Beruf: Maschinen- und Anlagenfuehrer/-in  
Schwerpunkt (MVP): Metall- und Kunststofftechnik  
Region / Traeger: IHK Aachen, BZE Euskirchen (UeLU), Berufskolleg Eschweiler  
Stand: 2026-08-12

Dieses Dokument ist der **operative Plan**, wie wir Inhalte strukturieren,
erzeugen und in die Datenbank bringen. Die Quellenbasis steht in
`docs/source_truth_content_plan_maf_ihk_aachen.md`. Die Review-Regeln stehen in
`docs/content-governance.md`.

---

## 1. Scope (bewusst eng)

Nur dieser eine Beruf, nur dieser eine Schwerpunkt:

| Ebene | Wert |
| --- | --- |
| Occupation | `maschinen-und-anlagenfuehrer` |
| Specialization | `metall-und-kunststofftechnik` |
| Dauer | 24 Monate (gesetzlich) |
| Lernkern in der App | Monate 1–18 Fachaufbau, Monate 12 / 19–24 Pruefungssprints |
| Nicht im MVP | Lebensmitteltechnik, Textiltechnik, Druckweiter-/Papierverarbeitung |

Andere Schwerpunkte der Ausbildungsordnung kommen spaeter als eigene
`specializations`-Zeilen — nicht vermischen.

---

## 2. Informationsgrundlage (bereits gesichert)

Tier-1-Quellen sind im Repo verdrahtet (`app/data/sources.py`) und archiviert
(siehe Source-Truth-Dokument):

1. IHK Aachen Berufsseite + Pruefungs-FAQ + Pruefungsordnung
2. BIBB Berufsprofil + Ausbildungsordnungs-PDF
3. MaschFueAusbV (Gesetze-im-Internet)
4. KMK Rahmenlehrplan-Referenz
5. BZE UeLU Metall-/Kunststofftechnik (Kursseite + Jahresplanung 2026/2027)
6. Berufskolleg Eschweiler (regionale Berufsschulstruktur)

**Gesicherte Eckdaten fuer die Lernreise**

- Ausbildung: 24 Monate
- Zwischenpruefung: Beginn 2. Ausbildungsjahr (Stoff der ersten 12 Monate)
- Abschlusspruefung schriftlich: Produktionstechnik, Produktionsplanung, WiSo
- Abschlusspruefung praktisch: Einrichten, Bedienen, Umruesten, vorbeugende Instandhaltung
- BZE-Praxisanker: Pneumatik, Drehen/Fraesen, Werkstoffkunde & TK, Grundbildung Metall,
  QM & Kunststoffe, Blechkurs, PVZP/PVAP

Keine Original-IHK/PAL-Fragen, keine Normtexte — nur eigene, quellengebundene Inhalte.

---

## 3. Hierarchie: so bauen wir den Content-Baum

```text
Occupation (MAF)
└── Specialization (Metall- und Kunststofftechnik)
    └── Super-Kategorie / Saeule (3 Stueck)
        └── Curriculum-Monat (1–24)
            └── Unterkapitel / question_category (10 pro Monat = 240)
                ├── learning_unit (Fachkunde)
                ├── quiz_questions (Single Choice)
                ├── open_questions (ungebunden)
                └── practice_exam / Checkpoint (am Monatsende / ZP / AP)
```

Das spiegelt exakt das Schema in `app/db/content_schema.sql` wider:

`occupations` → `specializations` → `curriculum_months` →
`question_categories` + `learning_units` → `quiz_questions` /
`open_questions` → `practice_exams`

---

## 4. Drei Super-Kategorien (Saeulen)

Statt den Beruf in andere Fachrichtungen zu splitten, teilen wir
**Metall- und Kunststofftechnik** in drei didaktische Saeulen. Jede
Unterkategorie und jede Frage bekommt genau eine Primaer-Saeule plus optional
eine Pruefungslinse.

### Saeule A — Querschnitt & Grundlagen

Gemeinsames Wissen fuer Metall *und* Kunststoff, Betrieb und Pruefung.

- Berufsbild, Rechte/Pflichten, Berichtsheft
- Arbeitsschutz, Gesundheit, Umwelt
- Technische Kommunikation
- Arbeitsplanung, Materialfluss
- Messen/Pruefen (allgemein)
- WiSo / Ausbildungsrecht
- Pruefungsorganisation IHK

### Saeule B — Metalltechnik

- Stahl / NE-Metalle, Eigenschaften
- Manuelle Fertigung (Saegen, Feilen, Bohren, Gewinde)
- Drehen / Fraesen, Schneidstoffe, Parameter
- Grundbildung Metall (BZE)
- Blechbearbeitung (BZE)
- Metallbezogene Qualitaet und Oberflaechen

### Saeule C — Kunststofftechnik & Anlagenfuehrung

- Kunststoffarten, Verhalten, Prozessparameter
- Pneumatik / Druckluftsysteme (BZE)
- Ruesten, Umruesten, Probelauf
- Prozessueberwachung, Stoerungssuche
- Vorbeugende Instandhaltung
- QM & Kunststoff (BZE)

**Pruefungslinsen** (zusaetzliches Tagging, nicht eigene Saeule):

- `produktionstechnik`
- `produktionsplanung`
- `wiso`
- `praxis`

Damit lassen sich spaeter Defizit-Reports und AP-Simulationen sauber schneiden.

---

## 5. Zeitstruktur: 18 Monate Aufbau + Pruefungsfenster

Gesetzlich 24 Monate. In der App steuern wir die Lernlast so:

| Phase | Monate | Zweck |
| --- | --- | --- |
| Fundament | 1–6 | Saeule A + Einstieg B/C (Werkstoffe, Messen) |
| Werkstatt & BZE I | 7–11 | Fertigung I, Pneumatik, Drehen/Fraesen, Metall, Materialfluss |
| ZP-Sprint | 12 | Wiederholung Monate 1–11, Checkpoint Zwischenpruefung |
| Vertiefung | 13–18 | Werkstoffe II, Planung, Fertigung II, Toleranzen, Steuerung, Ruesten |
| Betriebsfuehrung | 19–21 | Prozess, Stoerung, Wartung |
| Integration & AP | 22–24 | QM/Kunststoff, Blech/Praxisfall, Abschlusspruefung-Sprint |

Faustregel fuer Azubis: **Monate 1–18 = neues Fachwissen**,  
**Monate 12 und 22–24 = Verdichtung + Pruefungssimulation**.  
Monat 12 ist frueh absichtlich als ZP-Fenster gesetzt (IHK: Beginn 2. Jahr).

Die bestehende Monatszuordnung in `app/data/machine_operator.py` und
`docs/source_truth_content_plan_maf_ihk_aachen.md` bleibt die kanonische
Reihenfolge; die drei Saeulen sind die **Querklassifikation** darueber.

### Mapping Monat → Primaer-Saeule

| Monat | Titel | Primaer |
| --- | --- | --- |
| 1 | Berufsstart | A |
| 2 | Sicherheit / Umwelt | A |
| 3 | Werkstoffe | A (+ B/C Anteile in Unterkapiteln) |
| 4 | Technische Kommunikation | A |
| 5 | Arbeitsablaeufe planen | A |
| 6 | Messen und Pruefen | A |
| 7 | Fertigungstechniken I | B |
| 8 | Pneumatik | C |
| 9 | Drehen und Fraesen | B |
| 10 | Grundbildung Metall | B |
| 11 | Materialfluss | A |
| 12 | Zwischenpruefung | A+B+C (Mix) |
| 13 | Werkstoffe vertiefen | B+C |
| 14 | Produktionsplanung / Uebergabe | A |
| 15 | Fertigungstechniken II | B+C |
| 16 | Toleranzen / Qualitaet | A |
| 17 | Steuerung / Regelung | C |
| 18 | Ruesten / Umruesten | C |
| 19 | Prozess ueberwachen | C |
| 20 | Stoerungssuche | C |
| 21 | Wartung / Inspektion | C |
| 22 | QM und Kunststoff | C |
| 23 | Blech + Praxisfall | B |
| 24 | Abschlusspruefung | A+B+C (Mix) |

---

## 6. Unterkategorien und Content-Menge (nicht zu viel, nicht zu wenig)

### Pro Monat (Soll)

| Artefakt | Soll | DB-Tabelle |
| --- | --- | --- |
| Unterkapitel / Kategorien | 10 | `question_categories` |
| Learning Units (Fachkunde) | 10 (1:1 zu Unterkapitel) | `learning_units` + `theory_blocks` + `glossary_entries` |
| Single-Choice-Fragen | 30–40 (Start 20, Ausbau) | `quiz_questions` |
| Offene Aufgaben | 5 | `open_questions` |
| Praxisfall | 1 (in Unit oder Open) | Text in Unit / Open |
| Monats-Quiz / Mini-Test | 1 Checkpoint am Ende | `practice_exams` (`is_checkpoint=1`) |

### Gesamt-Soll MVP (Specialization Metall/Kunststoff)

| Artefakt | Soll | Ist (Seed, 2026-08-12) | Luecke |
| --- | --- | --- | --- |
| Kategorien | 240 | 240 | — |
| Learning Units | 240 | 144 (M1–12 voll, M13–24 nur je 2) | **96 Units** |
| Quizfragen | Start 480 → Ziel 720–960 | 480 (je Monat 20) | **+240 bis +480** |
| Offene Fragen | 120 (5 × 24) | 60 | **+60** |
| Checkpoints | 24 Monats-Quizzes + ZP + AP | teilweise vorhanden | vervollstaendigen |
| Review-Status | `approved` nach Fachreview | ueberwiegend `draft` | Review-Pipeline |

### Inhaltstiefe je Unit (Template)

Jede `learning_unit` enthaelt:

1. Titel + 2–4 Lernziele
2. 2 Theoriebloecke (`theory_blocks`): Kernwissen + Anwendung
3. 3–6 Key Points
4. 2–4 Glossar-Begriffe
5. 1 Praxisaufgabe (kurz, betriebsnah)
6. `source_keys` (mindestens eine Tier-1-Quelle)
7. Geschaetzte Dauer: 10–15 Minuten
8. Am Ende: Verweis auf Kategorie-Quiz

Faustregel: **eine Unit = ein Unterkapitel = ein abgeschlossenes Thema**.  
Keine Lexikon-Aufsaetze, keine Folienfriedhoefe.

---

## 7. Quiz-Strategie: immer am Ende des Fachs

### Regel

- Nach **jeder** Learning Unit: Kategorie-Quiz (Fragen der zugehoerigen
  `question_category`).
- Nach **jedem** Monat: Checkpoint-Exam (Mix aus den 10 Kategorien).
- Nach Monat 12: ZP-Simulation.
- Nach Monat 24: AP-Simulation (Produktionstechnik / Planung / WiSo / Praxis).

### Mastery (bereits Produktregel)

Eine Frage gilt erst als abgeschlossen, wenn sie:

1. mindestens einmal beantwortet wurde und
2. zweimal hintereinander richtig geloest wurde.

Falsche Antworten speisen Defizit-Kategorien.

### Fragekatalog kontinuierlich erweitern

Pro Kategorie waechst der Pool in Wellen:

| Welle | Fragen pro Kategorie | Fokus |
| --- | --- | --- |
| W0 (jetzt) | ~2 | Skeleton, Struktur fuellen |
| W1 | 3–4 | Kernfakten, Definitionen |
| W2 | 5–6 | Anwendung / Stoerfall |
| W3 | 7–8 | Pruefungsnaehe, Transfer |

Zielband: **3–4 Fragen/Kategorie im MVP-Release**, spaeter 7–8.  
Schwierigkeit 1–3 mischen (ca. 30 % / 50 % / 20 %).  
`exam_style`-Tags nutzen: Grundlagen, Anwendung, Berechnung, Situation, WiSo.

---

## 8. Vorgehen: wie die Datenbank gefuellt wird

### Prinzip

**Python-Seed ist Source of Truth fuer den Import.**  
Ablauf:

```text
Recherche (Tier-1)
  → Unit-/Fragen-Entwurf in app/data/content/
  → ReviewStatus draft
  → python -m app.tools.seed_content --force
  → Tabellen in content_schema
  → source_checked → approved (Review-UI / Ausbilder)
  → erst dann fuer Azubis sichtbar
```

### Seed-Befehl

```bash
python -m app.tools.seed_content --dry-run   # Zaehlung
python -m app.tools.seed_content --force     # Vollimport
```

`ContentSeeder` schreibt deterministisch:

1. `occupations` / `specializations`
2. `curriculum_months` / `learning_modules`
3. `source_documents`
4. `question_categories` (aus `MONTH_SUBCHAPTERS`)
5. `learning_units` + Theorie/Glossar/Source-Links
6. `quiz_questions` / `open_questions`
7. `practice_exams` + Zuordnungen

### Dateiorte fuer Autoren

| Was | Wo |
| --- | --- |
| Monats-Curriculum | `app/data/machine_operator.py` |
| Unterkapitel-Titel | `app/data/content/subchapters.py` |
| Units M1–M12 | `app/data/content/units/m01.py` … `m12.py` |
| Units M13–M24 | `app/data/content/units/m13_m24.py` (ausbauen!) |
| Quizfragen | `app/data/content/questions.py` (+ spaeter monatsweise Split) |
| Offene Fragen | `app/data/content/units/open_questions.py` |
| Quellenkatalog | `app/data/sources.py` |
| Aggregation | `app/data/content/aggregate.py` |

### Qualitaetsgates vor jedem Seed

1. Jede Unit zitiert bekannte `source_keys` (Test vorhanden).
2. Neue Inhalte starten als `draft` (Test vorhanden).
3. Keine Personen-/Klassendaten in Content-Dateien.
4. Keine Normvolltexte, keine IHK-Originalfragen.
5. Kategorie-Slug stabil (`m{month:02d}-{slugify(title)}`).

---

## 9. Arbeitsphasen (strukturell, in Reihenfolge)

### Phase 0 — Plan & Taxonomie (dieses Dokument)

- Scope fixieren (nur MAF Metall/Kunststoff)
- Saeulen A/B/C + Pruefungslinsen festlegen
- Sollmengen und Lueckeninventar

### Phase 1 — Taxonomie in Datenmodell verankern

- Optional: Feld/Tag `pillar` (`A|B|C`) an `curriculum_months` oder
  `question_categories` (JSON-Metadatum reicht fuer MVP)
- Pruefungslinse als `exam_style` / zusaetzliches Tag an Fragen
- Export-Skript: Abdeckungsreport Monat × Saeule × Fragenanzahl

### Phase 2 — Units M13–M24 auf Soll bringen (groesste Luecke)

Pro Monat 2 → 10 Units nach dem Unit-Template. Prioritaet:

1. M13 Werkstoffe II  
2. M14 Planung / Uebergabe  
3. M15 Fertigung II  
4. M16 Toleranzen  
5. M17 Steuerung  
6. M18 Ruesten  
7. M19–M21 Prozess / Stoerung / Wartung  
8. M22 QM/Kunststoff  
9. M23 Blech/Praxisfall  
10. M24 AP-Sprint-Inhalte

Nach jedem Monatsblock: `seed_content --force`, Smoke-Test API
(`/api/learning/...`, `/api/questions?month=N`).

### Phase 3 — Fragekatalog Welle 1

- Pro vorhandener Kategorie von ~2 auf 3–4 Fragen
- Jede neue Frage: Erklaerung + `source_keys` + Difficulty
- Monats-Checkpoint-Exams vervollstaendigen (10 Fragen Mix)
- ZP- und AP-Exams als eigene `practice_exams`

### Phase 4 — Offene Aufgaben auf 5/Monat

- Formate mischen: `short_text`, `calculation`, `sketch`
- Bewertungskriterien (`open_question_criteria`) pflegen

### Phase 5 — Review & Freigabe

- Batchweise `draft` → `source_checked` → `approved`
- Nur `approved` fuer Azubi-UI
- Fachreview durch Ausbilder/BZE-nahe Rolle

### Phase 6 — Katalogwachstum (Daueraufgabe)

- Welle 2/3 Fragen
- Defizit-getriebene Nachproduktion (Kategorien mit hoher Fehlerquote zuerst)
- Quellen-Hashes periodisch gegen Archive pruefen

---

## 10. Definition of Done je Monat

Ein Monat gilt als „datenbankfertig“, wenn:

- [ ] 10 Kategorien existieren und benannt sind
- [ ] 10 Learning Units mit Theorie, Glossar, Praxis, Sources
- [ ] ≥ 30 Quizfragen ueber die 10 Kategorien
- [ ] ≥ 5 offene Aufgaben
- [ ] 1 Monats-Checkpoint-Exam
- [ ] Alle Entities mindestens `source_checked`
- [ ] Seed laeuft idempotent / mit `--force` sauber
- [ ] API liefert Monat ohne leere Units

Beruf-MVP fertig, wenn alle 24 Monate DoD erfuellen und ZP/AP-Simulationen
bestehen.

---

## 11. Was wir bewusst nicht tun

- Keine parallelen Berufe im ersten Content-Lauf
- Keine Vermischung mit anderen MAF-Schwerpunkten
- Kein Scraping von Pruefungsheften als Fragenquelle
- Keine Riesenkapitel: lieber 10 kurze Units als 3 Aufsaetze
- Keine Freigabe ohne Tier-1-Quellenbezug

---

## 12. Sofort naechster Umsetzungsschritt

1. Saeulen-Tagging-Tabelle (Monat/Unterkapitel → A/B/C) als kleine
   Maschine in `app/data/content/` ablegen.
2. `m13_m24.py` Monat fuer Monat auf 10 Units erweitern — Start M13.
3. Parallel Fragewelle 1 fuer Monate 1–6 (Fundament staerken).
4. Nach jedem Block seeden und Abdeckungsreport aktualisieren.

Damit ist die Struktur klar: **eine Specialization, drei Saeulen,
24 Monate, 240 Unterkapitel, Unit+Quiz am Ende jedes Fachs, Seed in die
Content-DB, Review vor Azubi-Sicht.**
