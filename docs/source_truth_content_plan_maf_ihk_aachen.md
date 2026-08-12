# Source Truth und 24-Monate-Contentplan

Projekt: Online Lerncampus  
Beruf: Maschinen- und Anlagenfuehrer/-in  
Schwerpunkt: Metall- und Kunststofftechnik  
Regionale Ausrichtung: IHK Aachen, BZE Euskirchen, Berufskolleg Eschweiler  
Stand der Recherche: 2026-08-12

## Ziel

Dieses Dokument definiert die belastbare Quellenbasis fuer Content-Generierung,
Fact-Checking, Lernreise, Quizfragen und Pruefungssimulationen. Inhalte duerfen
nicht frei aus Foren oder kommerziellen Pruefungsheften kopiert werden. Die
Plattform soll eigene Erklaerungen, eigene Aufgaben und eigene Quizfragen
erzeugen, aber gegen diese Quellen pruefen.

## Quellenhierarchie

Tier 1: Verbindliche und amtliche Quellen

- IHK Aachen Berufsseite Maschinen- und Anlagenfuehrer/-in
- IHK Aachen Pruefungsinformationen und Pruefungsordnung
- BIBB Berufsprofil und Ausbildungsordnungs-PDF
- Gesetze-im-Internet: aktuelle MaschFueAusbV
- KMK Rahmenlehrplan-Referenz
- BZE Euskirchen UeLU-Kursplanung Metall- und Kunststofftechnik

Tier 2: Regionale Einordnung

- Berufskolleg Eschweiler: Berufsschulstandort, Blockunterricht, Lernbereiche

Tier 3: Nur zur Inspiration, nicht als Truth Source

- Kommerzielle Pruefungsvorbereitung
- Herstellerunterlagen
- Wikipedia
- Foren
- YouTube

## Lokal archivierte Dateien

Die Rohquellen liegen unter `work/source_truth/raw/`. Fuer Nachvollziehbarkeit
wird jede Datei per SHA-256 identifiziert.

| Datei | Zweck | SHA-256 |
| --- | --- | --- |
| `01_www_ihk_de_aachen_bildung_ausbildung_ausbildungsberufe_maschinen_anlagenfuehrer_6888522.html` | IHK Aachen Berufsprofil, Struktur, Pruefungszeitpunkte | `82CD23FE9D7441AC0781BE4531CD6FD25B443E4C82A73661EE7B6F518B4C7D4D` |
| `02_www_ihk_de_aachen_bildung_ausbildung_alles_ueber_ausbildungspruefungen_3999084.html` | IHK Aachen FAQ zu Anmeldung, Bestehen, Zeugnis, Wiederholung | `B553C980F7F558BC2A8B3E319E7D3F2A130AA4B3F2FBFD3C82692B76CD970250` |
| `03_www_ihk_de_aachen_ueber_uns_rechtsgrundlagen_pruefungsordnung_abschluss_u_umschulung_50.html` | IHK Aachen Pruefungsordnung | `9414BC64F0BD5FD99B601CD033988D56081AEEB3C9D7905B213C9B66F6BD1EF3` |
| `04_www_bibb_de_dienst_berufesuche_de_index_berufesuche_php_profile_apprenticeship_87iz96t0.html` | BIBB Berufsprofil, Kompetenzen, Dauer, Schwerpunkte | `72A2D4D565F8124B3012B4453BD7C336A1C4895B19E03938629B7A656D55E22F` |
| `05_www_bibb_de_dienst_berufesuche_de_index_berufesuche_php_regulation_maschinen_und_anlage.pdf` | Ausbildungsordnung als PDF-Fassung | `45841E14E93ECBFA59B1B6670C66505ED798E17F18C898DD248040E6125D1CEE` |
| `06_www_gesetze_im_internet_de_maschf_ausbv_BJNR064700004_html.html` | Aktuelle konsolidierte Ausbildungsordnung | `03FDC60E3BE8C6BFFD22BECCEF324B6F6C1757DF3B8ED7ADE58CF5F110A67A76` |
| `07_www_kmk_org_service_servicebereich_berufliche_schulen_downloadbereich_rahmenlehrplaene_.html` | KMK Rahmenlehrplan-Referenz als PDF-Download | `4EFD9DB1A8896197EC152D9B0D4998D27E1856EC33F2F93C9049BD154A47782A` |
| `08_www_bze_euskirchen_de_leistungen_ausbildung_ueberbetriebliche_unterweisung_industrie_ma.html` | BZE UeLU-Seite mit Kursuebersicht | `A3F1CB1AD86C3B4E42D71A17D53F1DD1782AB925EFBEE4A07D200EC9C2769F88` |
| `09_www_bze_euskirchen_de_fileadmin_user_upload_pdfs_UELU_Industrie_2026_01_MA_Metall_und_K.pdf` | BZE Kursplanung 2026 | `3FAFD784ADB1858FC1839335AE25178751CC398048075B768B13D9F903879502` |
| `10_www_bze_euskirchen_de_fileadmin_user_upload_pdfs_UELU_Industrie_2027_06_Maschinen_und_A.pdf` | BZE Kursplanung 2027 | `546D0CA37534D3F20E794713152F5CC4F611504E50324116C1AAD16AA0A745AA` |
| `11_www_bk_eschweiler_de_cms_bildungsangebot_berufsschule_technik_maschinen_und_anlagenfueh.html` | Berufskolleg Eschweiler, regionale Berufsschulstruktur | `25C02A40CD3FFE0159241159A7613C75EEAB848E15137412FDAF9EFD5708A6C7` |

## Gesicherte Fakten fuer die Plattform

- Die Ausbildung dauert 24 Monate.
- IHK Aachen fuehrt den Beruf Maschinen- und Anlagenfuehrer/-in mit mehreren
  Schwerpunkten; fuer diesen MVP wird Metall- und Kunststofftechnik verwendet.
- Der Ausbildungsrahmenplan ist die Grundlage fuer den betrieblichen
  Ausbildungsplan.
- Die Zwischenpruefung findet zu Beginn des zweiten Ausbildungsjahres statt und
  bezieht sich auf die ersten 12 Monate.
- Die Abschlusspruefung findet am Ende der Ausbildung statt.
- Schriftliche Abschlusspruefung: Produktionstechnik, Produktionsplanung,
  Wirtschafts- und Sozialkunde.
- Fuer Metall- und Kunststofftechnik sind u. a. technische Unterlagen,
  Werkstoffe, Werkzeuge, Maschinenfunktionen, Pruefverfahren, Fertigungstechnik,
  Arbeitsschritte, Qualitaetssicherung, vorbeugende Instandhaltung,
  Produktionsanlagen und Uebergabeprotokoll relevant.
- BZE Euskirchen bietet fuer Metall und Kunststoff u. a. Pneumatik, Drehen /
  Fraesen, Werkstoffkunde und technische Kommunikation, Grundbildung Metall,
  QM & Kunststoffe, Blechkurs sowie Pruefungsvorbereitung an.
- Fuer Auszubildende aus der StaedteRegion Aachen mit Schwerpunkt Metalltechnik
  / Kunststofftechnik nennt das Berufskolleg Eschweiler den Unterrichtsort und
  Blockunterricht mit zwei Ausbildungsjahren.

## Content-Prinzip

Jeder Lerninhalt braucht:

- mindestens eine Tier-1-Quelle
- kurze eigene Fachkunde
- ein praktisches Beispiel
- ein Quiz mit Quellenbezug
- eine Defizit-Kategorie
- eine Review-Markierung: `draft`, `source_checked`, `approved`

Jede zehnte Untereinheit schaltet einen Checkpoint frei. Jede Frage gilt erst
als abgeschlossen, wenn sie mindestens einmal beantwortet und zweimal
hintereinander richtig geloest wurde.

## 24-Monate-Plan

| Monat | Lernwelt | Lernziele | Pruefungs-/Fragekategorien | Primarquellen |
| --- | --- | --- | --- | --- |
| 1 | Berufsstart, Betrieb, Rechte und Pflichten | Berufsbild verstehen, Ausbildungsnachweis, Betrieb und Rollen einordnen | Berufsbild, Ausbildungsvertrag, Berichtsheft, Betriebsorganisation, DQR, Lernapp-Regel | IHK Aachen, BIBB, MaschFueAusbV |
| 2 | Sicherheit, Gesundheit, Umwelt | Gefahren erkennen, PSA, Unfallverhuetung, Brandschutz, Umweltregeln anwenden | Arbeitsschutz, Brandschutz, Gefahrstoffe, Entsorgung, Verhalten bei Unfall, Umweltschutz | MaschFueAusbV, IHK Aachen |
| 3 | Werk-, Betriebs- und Hilfsstoffe | Werkstoffe unterscheiden, Betriebsstoffe sicher nutzen, Eigenschaften einordnen | Stahl, NE-Metalle, Kunststoffe, Schmierstoffe, Kuehlmittel, Lagerung, Kennzeichnung | MaschFueAusbV, BIBB |
| 4 | Technische Kommunikation | Zeichnungen, Tabellen, Arbeitsplaene und Dokumentation lesen | technische Zeichnung, Symbole, Tabellenbuch, Skizze, Uebergabe, Produktionsdaten | MaschFueAusbV, BZE WKTK, BK Eschweiler |
| 5 | Arbeitsablaeufe planen | Arbeitsschritte ordnen, Werkzeuge vorbereiten, Materialfluss planen | Arbeitsplanung, Reihenfolge, Werkzeuge, Betriebsstoffe, Zeitplanung, Sicherheitscheck | MaschFueAusbV, BIBB |
| 6 | Messen und Pruefen | Pruefmittel auswaehlen, Messergebnisse bewerten, Abweichungen dokumentieren | Messschieber, Grenzlehre, Sichtpruefung, Messfehler, Pruefprotokoll, Toleranz | MaschFueAusbV, DIN nur als Verweis |
| 7 | Fertigungstechniken I | manuelle Fertigung und Grundoperationen sicher ausfuehren | Saegen, Feilen, Bohren, Gewinde, Entgraten, Werkstueckspannung | MaschFueAusbV, BK Eschweiler |
| 8 | Pneumatik Grundlagen | Druckluftkomponenten verstehen, einfache Funktionen erklaeren | Zylinder, Ventile, Wartungseinheit, Schaltplan, Druck, Sicherheit | BZE 2026/2027, MaschFueAusbV |
| 9 | Drehen und Fraesen | spanende Fertigung, Werkzeugauswahl, Prozessparameter verstehen | Drehmaschine, Fraesmaschine, Schneidstoff, Vorschub, Drehzahl, Kuehlung | BZE 2026/2027, MaschFueAusbV |
| 10 | Grundbildung Metall | Metallbearbeitung als Prozess planen, ausfuehren und pruefen | Metallgrundlagen, Werkzeuge, Pruefen, Oberflaeche, Arbeitsfolge | BZE 2026/2027, BK Eschweiler |
| 11 | Materialfluss und Anlagenumfeld | Materialfluss ueberwachen, Stoerungen erkennen, Schnittstellen verstehen | Transport, Lager, Bereitstellung, FIFO, Stoerung, Schnittstelle | MaschFueAusbV, BIBB |
| 12 | Zwischenpruefung Sprint | erste 12 Monate wiederholen, praktische ZP-Situationen trainieren | Positionieren, Vorbereiten, Einstellen, technische Unterlagen, Sicherheit | IHK Aachen, MaschFueAusbV, BZE PVZP |
| 13 | Werkstoffeigenschaften vertiefen | Werkstoffe produktbezogen auswaehlen, Eigenschaften begruenden | Haerte, Festigkeit, Zaehigkeit, Kunststoffarten, Temperaturverhalten | MaschFueAusbV, BIBB |
| 14 | Produktionsplanung und Uebergabe | Arbeitsablaeufe abstimmen, Uebergabeprotokolle erstellen | Auftrag, Produktionsplan, Maschinenbelegung, Uebergabe, Dokumentation | MaschFueAusbV |
| 15 | Fertigungstechniken II | branchenspezifische Fertigungstechniken auswaehlen | Fuegen, Trennen, Umformen, Spanen, Kunststoffbearbeitung, Werkzeugwahl | MaschFueAusbV, BZE |
| 16 | Toleranzen und Qualitaetsmerkmale | Qualitaetsanforderungen aus Unterlagen ableiten | Mass-, Form-, Lagetoleranz, Oberflaechen, Pruefplan, Abweichung | MaschFueAusbV, BK Eschweiler |
| 17 | Steuerungs- und Regelungstechnik | Steuerungen bedienen, Sicherheitsvorschriften beachten | Sensor, Aktor, Steuerung, Regelkreis, Signal, Not-Halt, Bedienfehler | MaschFueAusbV, BK Eschweiler |
| 18 | Anlagen ruesten und umruesten | Maschinen vorbereiten, Ruestvorgang sicher durchfuehren | Ruestplan, Werkzeugwechsel, Einstellen, Probelauf, Freigabe | MaschFueAusbV |
| 19 | Produktionsprozess ueberwachen | Prozessdaten einstellen, Abweichungen erkennen | Soll-Ist-Vergleich, Parameter, Produktionsdaten, Prozessabweichung | MaschFueAusbV, BIBB |
| 20 | Stoerungssuche | Stoerungen systematisch eingrenzen und Massnahmen einleiten | Stoerungsart, Ursache, Korrektur, Eskalation, Dokumentation | MaschFueAusbV |
| 21 | Wartung und Inspektion | vorbeugende Instandhaltung planen und durchfuehren | Schmierung, Verschleissteil, Filter, Dichtung, Wartungsplan, Inbetriebnahme | MaschFueAusbV |
| 22 | QM und Kunststofftechnik | Qualitaetsabweichungen analysieren, Kunststofftechnik einordnen | Pruefplan, Fehlerursache, Korrekturmassnahme, Kunststoff, Prozessparameter | BZE 2026/2027, MaschFueAusbV |
| 23 | Blechkurs und integrierter Praxisfall | praktische Fertigungsaufgabe planen, pruefen und dokumentieren | Blechbearbeitung, Zuschnitt, Kanten, Messen, Dokumentation, Arbeitsschutz | BZE 2026/2027, BK Eschweiler |
| 24 | Abschlusspruefung Sprint | praktische und schriftliche Abschlusspruefung simulieren | Produktionstechnik, Produktionsplanung, WiSo, praktische Aufgabe, Zeitmanagement | IHK Aachen, MaschFueAusbV, BZE PVAP |

## Pruefungsstruktur fuer die App

Zwischenpruefung:

- Zeitpunkt: Beginn zweites Ausbildungsjahr.
- Inhalte: erste 12 Monate, technische Unterlagen, Arbeitsschritte,
  Arbeitsmittel, Sicherheit, Gesundheitsschutz, Umweltschutz.
- App-Umsetzung: Checkpoint nach Monat 12 mit Theoriefragen, Situationsfragen,
  Rechen-/Skizzenaufgaben und praktischer Ablaufplanung.

Abschlusspruefung:

- Praktischer Teil: Einrichten, Inbetriebnehmen, Bedienen, Umruesten oder
  vorbeugende Instandsetzung.
- Schriftlicher Teil: Produktionstechnik, Produktionsplanung, WiSo.
- App-Umsetzung: Checkpoint nach Monat 24 mit gemischtem Modus:
  Single Choice, offene Antworten, Berechnung, Skizzenhinweis,
  Uebergabeprotokoll.

## Empfohlene Content-Pakete pro Monat

Pro Monat:

- 10 Unterkapitel
- 10 Fachkunde-Karten
- 20 bis 40 Single-Choice-Fragen
- 5 offene Aufgaben
- 1 Praxisfall
- 1 Mini-Test

Nach jeweils 10 Unterkapiteln:

- 1 Checkpoint-Test
- Defizit-Auswertung nach Kategorien
- Wiederholung aller falsch beantworteten Fragen

Nach Monat 12 und Monat 24:

- grosse Pruefungssimulation
- Ergebnis nach Produktionstechnik, Produktionsplanung, WiSo/Praxis
- Lernempfehlung fuer Defizite

## Umsetzungsregeln fuer Content-Generierung

1. Jede generierte Fachkunde muss `source_keys` enthalten.
2. Jede Frage muss eine `category_slug` und mindestens eine Tier-1-Quelle haben.
3. Normen wie DIN duerfen nur referenziert, nicht reproduziert werden.
4. IHK/PAL Originalfragen duerfen nicht kopiert werden; nur eigene,
   pruefungsaehnliche Aufgaben erstellen.
5. BZE-Termine duerfen als lokale Planung verwendet werden; der fachliche
   Inhalt muss gegen Ausbildungsordnung/BIBB/KMK validiert werden.
6. Nutzer- und Lerndaten duerfen nie in die Source-Truth-Datenbank.
7. Content bleibt `draft`, bis Quellencheck und Fachreview abgeschlossen sind.

## Naechste technische Schritte

- `TRUSTED_SOURCES` regelmaessig gegen die archivierten Dateien abgleichen.
- Ingestion-Pipeline bauen: HTML/PDF -> Text -> Chunks -> Embeddings.
- Chunk-Metadaten: `source_key`, `title`, `publisher`, `url`, `sha256`,
  `retrieved_at`, `trust_tier`, `allowed_usage`.
- Admin-UI: Quellenstatus, letztes Scrape-Datum, Hash-Aenderung.
- Content-Generator nur mit Tier-1/2-Kontext laufen lassen.
- Review-UI: Quellenstellen anzeigen, aber keine langen Quelltexte kopieren.
