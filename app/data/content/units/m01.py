"""Learning units for curriculum month 1 - Einstieg in die Ausbildung."""

from app.data.content.helpers import theory, unit
from app.data.content.subchapters import slugify

_MONTH = 1
_TITLES = [
    "Berufsbild MAF",
    "Ausbildungsvertrag",
    "Berichtsheft",
    "Betriebsorganisation",
    "Deutscher Qualifikationsrahmen",
    "Lernregeln der App",
    "Rechte des Azubis",
    "Pflichten des Azubis",
    "Schwerpunkt Metall/Kunststoff",
    "Pruefungsvorbereitung Einstieg",
]


def _cat(title: str) -> list[str]:
    return [f"m{_MONTH:02d}-{slugify(title)}"]


UNITS = [
    unit(
        slug=slugify(_TITLES[0]),
        month=_MONTH,
        position=1,
        title=_TITLES[0],
        subtitle="Taetigkeiten, Schwerpunkte und Ausbildungsziele des Berufs",
        learning_goals=[
            "Die Kernaufgaben eines Maschinen- und Anlagenfuehrers benennen.",
            "Den Schwerpunkt Metall- und Kunststofftechnik einordnen.",
            "Ausbildungsdauer und Pruefungsstruktur skizzieren.",
        ],
        theory_blocks=[
            theory(
                heading="Was Maschinen- und Anlagenfuehrer tun",
                body=(
                    "Maschinen- und Anlagenfuehrer bedienen, ruesten und ueberwachen "
                    "Produktionsanlagen. Du stellst Maschinen ein, fuehrst Probelaeufe "
                    "durch, pruefst Werkstuecke und dokumentierst Ergebnisse. Bei "
                    "Stoerungen grenzt du die Ursache ein und leitest Korrekturmassnahmen "
                    "ein. Der Beruf verbindet handwerkliches Verstaendnis mit "
                    "Prozesswissen und Teamarbeit in der Fertigung."
                ),
                key_points=[
                    "Bedienen, Ruesten, Pruefen und Dokumentieren gehoeren zum Alltag.",
                    "Stoerungen systematisch eingrenzen und melden.",
                    "Enge Zusammenarbeit mit Produktion, Qualitaet und Instandhaltung.",
                ],
            ),
            theory(
                heading="Schwerpunkte in Metall- und Kunststofftechnik",
                body=(
                    "Im Schwerpunkt Metall- und Kunststofftechnik bearbeitest du "
                    "Metallteile manuell und maschinell, arbeitest mit Kunststoffen und "
                    "fuehrst Pruefungen durch. Pneumatik, spanende Fertigung und "
                    "Qualitaetssicherung sind zentrale Bausteine. In der UeLU lernst du "
                    "praktische Verfahren wie Drehen, Fraesen und Werkstoffpruefung "
                    "unter realen Bedingungen."
                ),
                key_points=[
                    "Metallbearbeitung und Kunststoffverarbeitung im Fokus.",
                    "Pruefverfahren und Qualitaetssicherung sind Pflicht.",
                    "UeLU vertieft praktische Fertigkeiten.",
                ],
            ),
            theory(
                heading="Ausbildungsstruktur",
                body=(
                    "Die Ausbildung dauert 24 Monate. Sie gliedert sich in betriebliche "
                    "Ausbildung, Berufsschulunterricht und ueberbetriebliche Unterweisung. "
                    "Zu Beginn des zweiten Jahres steht die Zwischenpruefung an, am Ende "
                    "die Abschlusspruefung mit schriftlichen und praktischen Teilen."
                ),
                key_points=[
                    "24 Monate Ausbildungsdauer.",
                    "Zwischenpruefung nach 12 Monaten.",
                    "Abschlusspruefung am Ende der Ausbildung.",
                ],
            ),
        ],
        practice_task=(
            "Recherchiere in deinem Betrieb drei konkrete Taetigkeiten, die ein "
            "Maschinen- und Anlagenfuehrer im Schwerpunkt Metall/Kunststoff "
            "uebernimmt. Notiere Maschine, Aufgabe und welche Pruefung dabei "
            "anfaellt."
        ),
        glossary={
            "Maschinen- und Anlagenfuehrer": (
                "Fachkraft fuer Bedienung, Ruesten und Ueberwachung von Produktionsanlagen."
            ),
            "Schwerpunkt": "Spezialisierung innerhalb der Ausbildung, hier Metall/Kunststoff.",
            "UeLU": "Ueberbetriebliche Lehrlingsunterweisung mit praktischen Kursen.",
        },
        category_slugs=_cat(_TITLES[0]),
        source_keys=["ihk-aachen-berufsseite-maf", "bibb-berufsprofil-maf", "maschfueausbv"],
    ),
    unit(
        slug=slugify(_TITLES[1]),
        month=_MONTH,
        position=2,
        title=_TITLES[1],
        subtitle="Vertragsparteien, Inhalte und wichtige Klauseln",
        learning_goals=[
            "Die Pflichtbestandteile eines Ausbildungsvertrags benennen.",
            "Probezeit und Kuendigungsregeln erklaeren.",
            "Unterschied zu Praktikum und Werkstudententätigkeit erkennen.",
        ],
        theory_blocks=[
            theory(
                heading="Was im Vertrag stehen muss",
                body=(
                    "Der Ausbildungsvertrag regelt die Rechte und Pflichten von Betrieb "
                    "und Auszubildendem. Pflichtangaben sind Name und Anschrift beider "
                    "Parteien, Beginn und Dauer der Ausbildung, Art der Ausbildung, "
                    "Ausbildungsberuf, schriftliche Darstellung des Ausbildungsplans "
                    "sowie Dauer der taeglichen und woechentlichen Ausbildungszeit. "
                    "Ohne schriftlichen Vertrag beginnt die Ausbildung nicht ordnungsgemaess."
                ),
                key_points=[
                    "Schriftform ist Pflicht.",
                    "Ausbildungsplan muss dem Rahmenplan entsprechen.",
                    "Dauer und Ausbildungsberuf muessen eindeutig sein.",
                ],
            ),
            theory(
                heading="Probezeit und Beendigung",
                body=(
                    "In den ersten drei Monaten gilt eine Probezeit. Waehrend dieser Zeit "
                    "kann der Vertrag ohne Angabe von Gruenden gekuendigt werden. "
                    "Danach gelten die Regeln des Berufsbildungsgesetzes. Eine "
                    "ordentliche Kuendigung ist nur aus wichtigem Grund oder bei "
                    "Bestehen/Nichtbestehen der Abschlusspruefung moeglich."
                ),
                key_points=[
                    "Probezeit: maximal drei Monate.",
                    "Waehrend Probezeit kuendbar ohne Begruendung.",
                    "Nach Probezeit gelten strengere Kuendigungsregeln.",
                ],
            ),
            theory(
                heading="Verguetung und Urlaub",
                body=(
                    "Auszubildende erhalten eine Ausbildungsverguetung nach Tarif oder "
                    "Vereinbarung. Der Urlaubsanspruch betraegt mindestens 24 Werktage "
                    "pro Jahr. Berufsschule und UeLU zaehlen zur Ausbildungszeit und "
                    "duerfen nicht als freie Tage behandelt werden."
                ),
                key_points=[
                    "Ausbildungsverguetung ist gesetzlich vorgeschrieben.",
                    "Mindestens 24 Werktage Urlaub pro Jahr.",
                    "Berufsschule gehoert zur Ausbildungszeit.",
                ],
            ),
        ],
        practice_task=(
            "Lies deinen Ausbildungsvertrag und markiere Beginn, Dauer, Verguetung "
            "und Probezeit. Vergleiche die Angaben mit dem Ausbildungsrahmenplan "
            "deines Betriebs."
        ),
        glossary={
            "Ausbildungsvertrag": "Schriftlicher Vertrag zwischen Betrieb und Azubi.",
            "Probezeit": "Erste Monate mit vereinfachter Kuendigungsmoeglichkeit.",
            "Ausbildungsrahmenplan": "Vom Gesetzgeber vorgegebener Plan fuer die Ausbildung.",
        },
        category_slugs=_cat(_TITLES[1]),
        source_keys=["maschfueausbv", "ihk-aachen-berufsseite-maf"],
    ),
    unit(
        slug=slugify(_TITLES[2]),
        month=_MONTH,
        position=3,
        title=_TITLES[2],
        subtitle="Taegliche Dokumentation der Ausbildung",
        learning_goals=[
            "Den Zweck des Berichtshefts erklaeren.",
            "Einen fachlich korrekten Tageseintrag formulieren.",
            "Typische Fehler bei der Dokumentation vermeiden.",
        ],
        theory_blocks=[
            theory(
                heading="Warum das Berichtsheft wichtig ist",
                body=(
                    "Das Berichtsheft dokumentiert, was du im Betrieb und in der "
                    "Berufsschule gelernt hast. Es dient der IHK als Nachweis deiner "
                    "Ausbildung und wird bei Pruefungen ausgewertet. Ein lueckenloses "
                    "Berichtsheft zeigt deinem Ausbilder und der Pruefungskommission, "
                    "dass du alle Ausbildungsinhalte durchlaufen hast."
                ),
                key_points=[
                    "Nachweis der betrieblichen Ausbildung fuer die IHK.",
                    "Regelmaessige, wahrheitsgemaesse Eintraege sind Pflicht.",
                    "Wird bei Zwischen- und Abschlusspruefung beruecksichtigt.",
                ],
            ),
            theory(
                heading="Aufbau eines guten Eintrags",
                body=(
                    "Ein Tageseintrag beginnt mit Datum und Abteilung. Beschreibe "
                    "konkret, welche Taetigkeiten du ausgefuehrt hast, welche Maschinen "
                    "oder Werkzeuge im Einsatz waren und was du dabei gelernt hast. "
                    "Vermeide allgemeine Formulierungen wie 'gearbeitet' oder "
                    "'Maschine bedient'. Stattdessen: 'CNC-Drehmaschine geruestet, "
                    "Werkzeug offset eingestellt, Erstteil geprueft'."
                ),
                key_points=[
                    "Datum, Abteilung und konkrete Taetigkeit nennen.",
                    "Lerninhalt und verwendete Mittel dokumentieren.",
                    "Allgemeine Floskeln vermeiden.",
                ],
            ),
            theory(
                heading="Unterschrift und Fristen",
                body=(
                    "Jeder Eintrag muss von deinem Ausbilder oder einer beauftragten "
                    "Person gegenzeichnet werden. Viele Betriebe verlangen woechentliche "
                    "Abgabe. Fehlende Unterschriften koennen bei der Pruefungszulassung "
                    "Probleme verursachen."
                ),
                key_points=[
                    "Ausbilder-Unterschrift ist Pflicht.",
                    "Woechentliche Abgabe ist ueblich.",
                    "Fehlende Eintraege rechtzeitig nachholen.",
                ],
            ),
        ],
        practice_task=(
            "Schreibe einen Muster-Eintrag fuer deinen letzten Ausbildungstag. "
            "Enthalten sein muessen: Datum, Abteilung, mindestens zwei konkrete "
            "Taetigkeiten und ein Lernziel."
        ),
        glossary={
            "Berichtsheft": "Schriftlicher Nachweis der Ausbildungstaetigkeiten.",
            "Ausbilder": "Verantwortliche Person im Betrieb fuer deine Ausbildung.",
            "Gegenzeichnung": "Unterschrift des Ausbilders zur Bestaetigung.",
        },
        category_slugs=_cat(_TITLES[2]),
        source_keys=["ihk-aachen-pruefungs-faq", "maschfueausbv"],
    ),
    unit(
        slug=slugify(_TITLES[3]),
        month=_MONTH,
        position=4,
        title=_TITLES[3],
        subtitle="Ablaeufe, Zustaendigkeiten und Kommunikation im Betrieb",
        learning_goals=[
            "Typische Abteilungen in einem Fertigungsbetrieb benennen.",
            "Informationswege im Team beschreiben.",
            "Schnittstellen zwischen Produktion und Qualitaet erklaeren.",
        ],
        theory_blocks=[
            theory(
                heading="Struktur eines Fertigungsbetriebs",
                body=(
                    "In der Metall- und Kunststofffertigung arbeiten Fertigung, "
                    "Qualitaetssicherung, Arbeitsvorbereitung, Lager und Versand "
                    "zusammen. Der Maschinen- und Anlagenfuehrer ist meist der "
                    "Schnittstelle zwischen Arbeitsvorbereitung und laufender Produktion "
                    "zugeteilt. Auftraege kommen ueber Fertigungsauftraege oder "
                    "Leitstandsysteme in die Fertigung."
                ),
                key_points=[
                    "Fertigung, QS, AV und Logistik sind zentrale Bereiche.",
                    "Auftraege werden ueber Fertigungsauftraege gesteuert.",
                    "Klare Zustaendigkeiten vermeiden Stillstand.",
                ],
            ),
            theory(
                heading="Kommunikation und Uebergabe",
                body=(
                    "Bei Schichtwechsel oder Maschinenuebergabe muessen Stand der "
                    "Fertigung, offene Maengel und Sicherheitsrelevantes muendlich "
                    "und schriftlich uebergeben werden. Kurze, praezise Meldungen "
                    "an Vorgesetzte sparen Zeit und verhindern Fehlproduktion."
                ),
                key_points=[
                    "Schichtuebergabe dokumentieren und muendlich bestaetigen.",
                    "Stoerungen sofort melden, nicht 'mitlaufen lassen'.",
                    "Produktionsdaten aktuell halten.",
                ],
            ),
        ],
        practice_task=(
            "Erstelle fuer deinen Betrieb eine einfache Skizze: Welche Abteilungen "
            "gibt es, und an wen wendest du dich bei einer Maschinenstoerung, "
            "einem Qualitaetsproblem und fehlendem Material?"
        ),
        glossary={
            "Arbeitsvorbereitung": "Plant Auftraege, Werkzeuge und Material.",
            "Leitstand": "System zur Steuerung von Fertigungsauftraegen.",
            "Schichtuebergabe": "Informationsweitergabe zwischen Schichten.",
        },
        category_slugs=_cat(_TITLES[3]),
        source_keys=["bibb-berufsprofil-maf", "bk-eschweiler-maf"],
    ),
    unit(
        slug=slugify(_TITLES[4]),
        month=_MONTH,
        position=5,
        title=_TITLES[4],
        subtitle="Qualifikationsstufen und Anbindung an Berufsausbildung",
        learning_goals=[
            "Die acht DQR-Stufen grob einordnen.",
            "Den Ausbildungsberuf MAF auf dem DQR verorten.",
            "Nutzen des DQR fuer Weiterbildung erklaeren.",
        ],
        theory_blocks=[
            theory(
                heading="Was der DQR abbildet",
                body=(
                    "Der Deutsche Qualifikationsrahmen (DQR) ordnet Bildungsabschluesse "
                    "in acht Niveaustufen ein. Er macht Qualifikationen vergleichbar - "
                    "von einfachen Kenntnissen (Stufe 2) bis zu hochqualifizierten "
                    "Spezialisten (Stufe 8). Die meisten anerkannten Ausbildungsberufe "
                    "liegen auf Stufe 4."
                ),
                key_points=[
                    "Acht Niveaustufen von 2 bis 8.",
                    "Vergleichbarkeit von Abschluessen im In- und Ausland.",
                    "Typische anerkannte Ausbildung: DQR-Stufe 4.",
                ],
            ),
            theory(
                heading="MAF auf dem DQR",
                body=(
                    "Der Abschluss Maschinen- und Anlagenfuehrer wird dem DQR "
                    "Niveau 4 zugeordnet. Damit ist er gleichwertig mit anderen "
                    "anerkannten Ausbildungsberufen. Aufbauqualifikationen wie "
                    "Techniker oder Meister liegen auf hoeheren Stufen."
                ),
                key_points=[
                    "MAF-Abschluss: DQR Niveau 4.",
                    "Grundlage fuer berufliche Weiterbildung.",
                    "Vergleichbar mit anderen IHK-Abschluessen.",
                ],
            ),
        ],
        practice_task=(
            "Ordne drei Berufsabschluesse aus deinem Umfeld (z. B. MAF, Industriemechaniker, "
            "Techniker) den DQR-Stufen zu und begruende kurz deine Einordnung."
        ),
        glossary={
            "DQR": "Deutscher Qualifikationsrahmen zur Einordnung von Bildungsabschluessen.",
            "Niveaustufe": "Qualifikationsniveau von 2 (einfach) bis 8 (hoechstes Niveau).",
        },
        category_slugs=_cat(_TITLES[4]),
        source_keys=["ihk-aachen-berufsseite-maf", "bibb-berufsprofil-maf"],
    ),
    unit(
        slug=slugify(_TITLES[5]),
        month=_MONTH,
        position=6,
        title=_TITLES[5],
        subtitle="So nutzt du den Online-Lerncampus effektiv",
        learning_goals=[
            "Den Lernrhythmus der App verstehen.",
            "Checkpoint-Regeln und Wiederholungslogik anwenden.",
            "Lernfortschritt sinnvoll dokumentieren.",
        ],
        theory_blocks=[
            theory(
                heading="Lernrhythmus und Checkpoints",
                body=(
                    "Jeder Monat enthaelt zehn Lerneinheiten zu den Unterkapiteln "
                    "des Lehrplans. Nach jeder zehnten Einheit folgt ein Checkpoint "
                    "im Format der schriftlichen IHK-Pruefung. Fragen gelten erst "
                    "als gemeistert, wenn du sie mindestens einmal beantwortet und "
                    "zweimal hintereinander richtig geloest hast."
                ),
                key_points=[
                    "10 Einheiten pro Monat, dann Checkpoint.",
                    "Doppelte richtige Loesung fuer Fragen-Meisterung.",
                    "Checkpoint simuliert IHK-Pruefungsformat.",
                ],
            ),
            theory(
                heading="Theorie, Uebung und Selbstkontrolle",
                body=(
                    "Jede Einheit beginnt mit Theoriebloecken und endet mit einer "
                    "Praxisaufgabe. Offene Pruefungsaufgaben kannst du gegen "
                    "Musterloesungen und Bewertungsraster selbst pruefen. Nutze "
                    "das Glossar zum Wiederholen zentraler Fachbegriffe."
                ),
                key_points=[
                    "Theorie zuerst, dann Praxisaufgabe.",
                    "Offene Aufgaben mit Musterloesung selbst bewerten.",
                    "Glossar fuer Begriffe nutzen.",
                ],
            ),
        ],
        practice_task=(
            "Plane deine Lernwoche: Wann lernst du welche Einheit? Trage "
            "mindestens drei feste Lernzeiten ein und lege fest, wann du den "
            "Checkpoint fuer Monat 1 absolvierst."
        ),
        glossary={
            "Checkpoint": "Pruefungssimulation nach jeweils zehn Lerneinheiten.",
            "Lerneinheit": "Theorie, Uebung und Fragen zu einem Unterkapitel.",
        },
        category_slugs=_cat(_TITLES[5]),
        source_keys=["ihk-aachen-pruefungs-faq"],
    ),
    unit(
        slug=slugify(_TITLES[6]),
        month=_MONTH,
        position=7,
        title=_TITLES[6],
        subtitle="Gesetzliche Rechte waehrend der Ausbildung",
        learning_goals=[
            "Wichtige Rechte aus dem Berufsbildungsgesetz benennen.",
            "Anspruch auf Ausbildungsverguetung und Urlaub erklaeren.",
            "Recht auf sachgerechte Ausbildung beschreiben.",
        ],
        theory_blocks=[
            theory(
                heading="Recht auf gute Ausbildung",
                body=(
                    "Du hast Anspruch auf eine Ausbildung, die dem Ausbildungsrahmenplan "
                    "entspricht. Der Betrieb muss dir geeignete Arbeitsmittel, "
                    "fachkundige Anleitung und ausreichend Zeit zum Lernen geben. "
                    "Berufsschule und UeLU sind verbindliche Bestandteile - der Betrieb "
                    "darf dich nicht davon abhalten."
                ),
                key_points=[
                    "Ausbildung muss dem Rahmenplan entsprechen.",
                    "Anleitung durch fachkundige Personen.",
                    "Berufsschule und UeLU sind Pflichttermine.",
                ],
            ),
            theory(
                heading="Verguetung, Urlaub und Arbeitszeit",
                body=(
                    "Auszubildende erhalten eine angemessene Verguetung. Die "
                    "Arbeitszeit darf acht Stunden taeglich nicht ueberschreiten; "
                    "Ueberstunden nur ausnahmsweise. Mindestens 24 Werktage Urlaub "
                    "stehen dir zu. Nacht- und Wochenendarbeit ist fuer Auszubildende "
                    "nur unter engen Voraussetzungen erlaubt."
                ),
                key_points=[
                    "Ausbildungsverguetung ist gesetzlicher Anspruch.",
                    "Maximal acht Stunden taeglich.",
                    "Mindestens 24 Werktage Urlaub.",
                ],
            ),
        ],
        practice_task=(
            "Notiere drei deiner Rechte als Azubi und erklaere, wie du sie "
            "im Betrieb geltend machst, falls sie verletzt werden."
        ),
        glossary={
            "Berufsbildungsgesetz": "Gesetzliche Grundlage der dualen Ausbildung.",
            "Ausbildungsverguetung": "Monatliche Verguetung waehrend der Ausbildung.",
        },
        category_slugs=_cat(_TITLES[6]),
        source_keys=["maschfueausbv", "ihk-aachen-berufsseite-maf"],
    ),
    unit(
        slug=slugify(_TITLES[7]),
        month=_MONTH,
        position=8,
        title=_TITLES[7],
        subtitle="Pflichten und Verhalten in der Ausbildung",
        learning_goals=[
            "Lern- und Arbeitspflichten beschreiben.",
            "Verschwiegenheit und Sorgfaltspflicht einordnen.",
            "Folgen von Pflichtverletzungen benennen.",
        ],
        theory_blocks=[
            theory(
                heading="Lern- und Arbeitspflicht",
                body=(
                    "Du bist verpflichtet, dir die in der Ausbildung vermittelten "
                    "Kenntnisse anzueignen und im Betrieb mitzuarbeiten. Das "
                    "Berichtsheft musst du fuehren. Du hast die Anweisungen deines "
                    "Ausbilders zu befolgen und dich an Betriebsordnung sowie "
                    "Arbeitsschutzvorschriften zu halten."
                ),
                key_points=[
                    "Lernen und Mitwirken im Betrieb.",
                    "Berichtsheft fuehren und vorlegen.",
                    "Betriebsordnung und Arbeitsschutz einhalten.",
                ],
            ),
            theory(
                heading="Sorgfalt und Verschwiegenheit",
                body=(
                    "Du musst Maschinen, Werkzeuge und Material sorgfaeltig behandeln "
                    "und Schaeden unverzueglich melden. Betriebs- und "
                    "Geschaeftsgeheimnisse darfst du nicht weitergeben. "
                    "Alkohol- und Drogenkonsum am Arbeitsplatz ist verboten."
                ),
                key_points=[
                    "Arbeitsmittel schonend nutzen.",
                    "Betriebsgeheimnisse wahren.",
                    "Schaeden sofort melden.",
                ],
            ),
        ],
        practice_task=(
            "Liste fuenf konkrete Pflichten auf, die du in der ersten "
            "Ausbildungswoche erfuellt hast, und erklaere, warum jede "
            "Pflicht wichtig ist."
        ),
        glossary={
            "Lernpflicht": "Verpflichtung, Ausbildungsinhalte anzueignen.",
            "Verschwiegenheitspflicht": "Schutz von Betriebs- und Geschaeftsgeheimnissen.",
        },
        category_slugs=_cat(_TITLES[7]),
        source_keys=["maschfueausbv"],
    ),
    unit(
        slug=slugify(_TITLES[8]),
        month=_MONTH,
        position=9,
        title=_TITLES[8],
        subtitle="Metall- und Kunststofftechnik als Ausbildungsschwerpunkt",
        learning_goals=[
            "Typische Materialien und Verfahren benennen.",
            "UeLU-Schwerpunkte fuer MAF M/K einordnen.",
            "Berufsschulinhalte skizzieren.",
        ],
        theory_blocks=[
            theory(
                heading="Materialien und Verfahren",
                body=(
                    "Im Schwerpunkt Metall/Kunststoff bearbeitest du Stahl, NE-Metalle "
                    "und Kunststoffe. Verfahren umfassen spanende Bearbeitung "
                    "(Drehen, Fraesen), manuelle Fertigung, Fuegen und Pruefen. "
                    "Du lernst Werkstoffe zu unterscheiden, richtig einzusetzen "
                    "und Qualitaet zu sichern."
                ),
                key_points=[
                    "Stahl, NE-Metalle und Kunststoffe.",
                    "Spanende und manuelle Fertigung.",
                    "Pruefverfahren und Qualitaetssicherung.",
                ],
            ),
            theory(
                heading="UeLU und Berufsschule",
                body=(
                    "Die UeLU bei BZE Euskirchen bietet Kurse zu Pneumatik, Drehen, "
                    "Fraesen, Werkstoffkunde, Grundbildung Metall, QM/Kunststoff "
                    "und Blechbearbeitung. In der Berufsschule vertiefst du "
                    "Fertigungs- und Prueftechnik sowie Steuerungs- und "
                    "Regelungstechnik - abhaengig vom regionalen Rahmenlehrplan."
                ),
                key_points=[
                    "UeLU: praktische Blockkurse.",
                    "Berufsschule: Theorie und Fachkunde.",
                    "Beide Teile ergaenzen die Betriebsausbildung.",
                ],
            ),
            theory(
                heading="Typische Betriebstaetigkeiten",
                body=(
                    "Im Betrieb ruestest du Maschinen, stellst Prozessparameter ein, "
                    "ueberwachst den Lauf und pruefst Werkstuecke. Du dokumentierst "
                    "Produktionsdaten und arbeitest bei Stoerungen mit der "
                    "Instandhaltung zusammen."
                ),
                key_points=[
                    "Ruesten, Einstellen, Pruefen, Dokumentieren.",
                    "Stoerungsmanagement im Team.",
                    "Qualitaet von Anfang an mitdenken.",
                ],
            ),
        ],
        practice_task=(
            "Erstelle eine Tabelle mit drei Materialien aus deinem Betrieb, "
            "dem zugehoerigen Bearbeitungsverfahren und dem Pruefmittel, "
            "mit dem du die Qualitaet kontrollierst."
        ),
        glossary={
            "NE-Metall": "Nichteisenmetall wie Aluminium, Kupfer oder Messing.",
            "Spanende Fertigung": "Materialabtrag durch Drehen, Fraesen, Bohren.",
            "Fertigungs- und Prueftechnik": "Berufsschulfach fuer Messen und Pruefen.",
        },
        category_slugs=_cat(_TITLES[8]),
        source_keys=[
            "bze-uelu-maf-metall-kunststoff",
            "kmk-rahmenlehrplan-maf-2023",
            "bk-eschweiler-maf",
        ],
    ),
    unit(
        slug=slugify(_TITLES[9]),
        month=_MONTH,
        position=10,
        title=_TITLES[9],
        subtitle="Erste Schritte zur Zwischen- und Abschlusspruefung",
        learning_goals=[
            "Pruefungsbestandteile von ZP und AP unterscheiden.",
            "Anmeldeprozess bei der IHK skizzieren.",
            "Fruehe Vorbereitungsstrategien anwenden.",
        ],
        theory_blocks=[
            theory(
                heading="Zwischen- und Abschlusspruefung",
                body=(
                    "Die Zwischenpruefung findet zu Beginn des zweiten Ausbildungsjahres "
                    "statt und prueft die Inhalte der ersten 12 Monate. Die "
                    "Abschlusspruefung am Ende umfasst schriftliche Pruefungen in "
                    "Produktionstechnik, Produktionsplanung und WiSo sowie einen "
                    "praktischen Pruefungsteil."
                ),
                key_points=[
                    "ZP nach 12 Monaten, AP am Ende.",
                    "AP: schriftlich und praktisch.",
                    "Schriftliche Teile: Produktionstechnik, Planung, WiSo.",
                ],
            ),
            theory(
                heading="Anmeldung und Zulassung",
                body=(
                    "Die Anmeldung erfolgt ueber den Ausbildungsbetrieb bei der "
                    "zustaendigen IHK. Voraussetzung ist ein ordnungsgemaesses "
                    "Berichtsheft und die Einhaltung der Ausbildungszeit. "
                    "Pruefungsgebuehren und Termine werden von der IHK bekannt gegeben."
                ),
                key_points=[
                    "Anmeldung ueber den Betrieb bei der IHK.",
                    "Berichtsheft und Ausbildungsnachweis noetig.",
                    "Termine und Gebuehren bei IHK erfragen.",
                ],
            ),
            theory(
                heading="Frueh vorbereiten",
                body=(
                    "Wer von Anfang an regelmaessig lernt, Berichtsheft fuehrt und "
                    "Pruefungsaufgaben uebt, hat weniger Stress vor der Pruefung. "
                    "Nutze Checkpoints in dieser App als Fruehwarnsystem fuer "
                    "Wissensluecken."
                ),
                key_points=[
                    "Regelmaessig lernen statt Kurz vor Pruefung.",
                    "Checkpoints als Lueckenanalyse nutzen.",
                    "Berichtsheft lueckenlos fuehren.",
                ],
            ),
        ],
        practice_task=(
            "Erstelle einen persoenlichen Pruefungsplan: Wann ist deine "
            "voraussichtliche Zwischenpruefung? Welche drei Themenbereiche "
            "willst du bis dahin besonders vertiefen?"
        ),
        glossary={
            "Zwischenpruefung": "Pruefung zu Beginn des zweiten Ausbildungsjahres.",
            "Abschlusspruefung": "Abschlusspruefung am Ende der 24 Monate.",
            "WiSo": "Wirtschafts- und Sozialkunde als Pruefungsteil.",
        },
        category_slugs=_cat(_TITLES[9]),
        source_keys=[
            "ihk-aachen-pruefungs-faq",
            "ihk-aachen-pruefungsordnung",
            "maschfueausbv",
        ],
    ),
]
