"""Learning units for curriculum month 6 - Messen und Pruefen."""

from app.data.content.subchapters import MONTH_SUBCHAPTERS
from app.data.content.units._month_builder import build_unit, tb

_M = 6
_T = MONTH_SUBCHAPTERS[_M]
_S = ["bze-uelu-maf-metall-kunststoff", "din-862", "kmk-rahmenlehrplan-maf-2023"]

UNITS = [
    build_unit(_M, 1, _T[0], "Das richtige Pruefmittel waehlen",
        ["Pruefmittel zu Merkmal zuordnen.", "Genauigkeit vs. Aufwand.", "Kalibrierstatus pruefen."],
        [tb("Auswahl", "Laenge: Messschieber, Buegelmessschraube, Mikrometer. Form: Lehren, Winkel. Oberflaeche: Rauheitsmessgeraet.", ["Genauigkeit passend zur Toleranz.", "Gueltiges Kalibriersiegel."]),
         tb("Regel", "Pruefmittel muss mindestens zehnmal genauer sein als Toleranz (Faustregel).", ["Nicht ueberdimensionieren.", "Dokumentation der Wahl."])],
        "Fuer eine Bohrung 20 H7: Welches Pruefmittel waehlst du und warum?",
        {"Kalibrierung": "Nachweis der Messgenauigkeit.", "Lehre": "Pruefmittel fuer Passung."}, _S),
    build_unit(_M, 3, _T[2], "Messwerte sicher ablesen",
        ["Nonius und Skalen lesen.", "Einheiten korrekt.", "Parallaxefehler vermeiden."],
        [tb("Ablesen", "Senkrecht auf Skala schauen. Nonius-Nullstrich fuer ganze mm. Fluchtender Strich fuer Nachkomma.", ["Einheit notieren.", "Nullpunkt pruefen."]),
         tb("Fehler", "Parallaxe, falscher Nonius, Kippen, verschmutzte Messflaechen.", ["Zweite Messung zur Kontrolle.", "Mittelwert bei Streuung."])],
        "Miss dieselbe Stelle zweimal mit Messschieber. Vergleiche und erklaere Abweichungen.",
        {"Parallaxe": "Abweichung durch schraegen Blickwinkel.", "Nonius": "Hilfsskala fuer Bruchteile."}, _S),
    build_unit(_M, 4, _T[3], "Toleranzen pruefen und bewerten",
        ["Ist-Mass vs. Soll.", "Passung bewerten.", "Nicht konform melden."],
        [tb("Toleranz", "Ober- und Untergrenze aus Zeichnung. Ist innerhalb = i.O., ausserhalb = n.i.O.", ["Grenzmass beruecksichtigen.", "Nicht 'fast passend'."]),
         tb("Passung", "Spiel, Uebergang, Press - aus Ist-Mass von Bohrung und Welle ableiten.", ["Paarweise pruefen.", "Protokoll ausfuellen."])],
        "Bohrung Ist 20,02 mm, Soll 20 H7 (+0,021/0). Bewerte das Ergebnis.",
        {"Sollmass": "Vorgabe aus Zeichnung.", "Ist-Mass": "Gemessener tatsaechlicher Wert."}, _S),
    build_unit(_M, 5, _T[4], "Pruefprotokoll fuehren",
        ["Pflichtfelder ausfuellen.", "Messmittel dokumentieren.", "Unterschrift und Datum."],
        [tb("Inhalt", "Auftragsnummer, Merkmal, Soll, Ist, Pruefmittel, Datum, Pruefer, Ergebnis.", ["Lesbar und vollstaendig.", "Keine leeren Felder."]),
         tb("Rechtliche Bedeutung", "Nachweis bei Reklamation und Audit. Falschprotokollierung ist schwerwiegend.", ["Original aufbewahren.", "Korrektur nach Regel."])],
        "Fuellen ein Uebungs-Pruefprotokoll fuer drei Merkmale an einem Werkstueck aus.",
        {"Pruefprotokoll": "Schriftlicher Nachweis der Pruefung.", "Merkmal": "Zu pruefende Eigenschaft."}, _S),
    build_unit(_M, 6, _T[5], "Messfehler erkennen und vermeiden",
        ["Systematische und zufaellige Fehler.", "Temperatur und Kippen.", "Wiederholmessung."],
        [tb("Fehlerquellen", "Abnutzung, Temperatur, falsche Handhabung, falsches Messmittel.", ["Nullpunkt pruefen.", "Bezugstemperatur 20 C."]),
         tb("Vermeidung", "Kalibrierte Mittel, Schulung, saubere Messflaechen, wiederholte Messung.", ["Streuung analysieren.", "Geraet sperren bei Verdacht."])],
        "Nenne vier Ursachen, warum zwei Messungen am selben Mass abweichen.",
        {"Systematischer Fehler": "Konstante Abweichung in eine Richtung.", "Bezugstemperatur": "20 Grad Celsius fuer Laengenmass."}, _S),
    build_unit(_M, 7, _T[6], "Sichtpruefung als Pruefverfahren",
        ["Oberflaeche, Risse, Grate.", "Reinigung vor Pruefung.", "Beleuchtung und Kriterien."],
        [tb("Sichtpruefung", "Erkennen von Rissen, Kratzern, Graten, Farbabweichungen, Verschmutzung.", ["Normale Sehkraft oder Hilfsmittel.", "Pruefliste abarbeiten."]),
         tb("Dokumentation", "Maengel fotografieren oder markieren, Sperre veranlassen.", ["Kriterien aus Zeichnung.", "Kein 'gefuehlt i.O.'."])],
        "Pruefe ein Werkstueck sichtpruefend: Nenne drei Merkmale und ihr Ergebnis.",
        {"Grat": "Scharfe Materialkante nach Bearbeitung.", "Sichtpruefung": "Pruefung mit dem Auge."}, _S),
    build_unit(_M, 8, _T[7], "Grenzlehren einsetzen",
        ["Go und NoGo.", "Handhabung.", "Verschleiss erkennen."],
        [tb("Funktion", "Go-Lehre muss durchgehen, NoGo darf nicht. Schnelle Passungspruefung in Serie.", ["Lehre kalibriert.", "Nicht mit Gewalt."]),
         tb("Verschleiss", "Abgenutzte Lehren verfaelschen Ergebnis. Regelmaessige Pruefung der Lehren.", ["Lehre sperren.", "Ersatz anfordern."])],
        "Erklaere den Unterschied zwischen Go- und NoGo-Lehre an einer Bohrung.",
        {"Go-Lehre": "Prueft Mindestmass.", "NoGo-Lehre": "Prueft Hoechstmass."}, _S),
    build_unit(_M, 9, _T[8], "Bezugstemperatur bei Laengenmessung",
        ["Waermeausdehnung.", "20 Grad Celsius.", "Messung nach Abkuehlung."],
        [tb("Temperatur", "Metalle dehnen sich bei Waerme aus. Messung bei 20 C oder korrigieren.", ["Warmes Teil zu gross.", "Umgebung notieren."]),
         tb("Praxis", "Frisch bearbeitetes Teil abkuehlen lassen oder kurz acclimatisieren.", ["Klimatisierter Raum ideal.", "Schnelle Messung nach Transport vermeiden."])],
        "Warum misst ein heisses Aluminiumteil groesser als bei 20 C?",
        {"Waermeausdehnung": "Volumen-/Laengenaenderung durch Temperatur.", "DIN EN ISO 1": "Norm fuer Bezugstemperatur."}, _S),
    build_unit(_M, 10, _T[9], "Messen und Pruefen pruefungsreif",
        ["Nonius rechnen.", "Toleranz bewerten.", "Pruefmittel waehlen."],
        [tb("Typische Aufgaben", "Noniusablesung, Toleranzpruefung, Pruefmittelauswahl, Protokoll vervollstaendigen.", ["Rechenweg schreiben.", "Einheit nicht vergessen."]),
         tb("Vorbereitung", "Messschieber, Passungen, Protokollfelder wiederholen.", ["Tabellenbuch nutzen.", "Checkpoint ueben."])],
        "Rechne: Soll 25 +0,2/-0,1 mm, Ist 25,15 mm. Ist das Mass i.O.?",
        {"Toleranzfeld": "Bereich zwischen Ober- und Untergrenze.", "i.O.": "In Ordnung, innerhalb Toleranz."}, ["ihk-aachen-pruefungs-faq", "din-862"]),
]

# Note: position 2 (Messschieber) is in m06_messschieber.py
