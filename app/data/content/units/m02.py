"""Learning units for curriculum month 2 - Arbeitsschutz und Umwelt."""

from app.data.content.helpers import theory, unit
from app.data.content.subchapters import MONTH_SUBCHAPTERS, slugify

_MONTH = 2
_TITLES = MONTH_SUBCHAPTERS[_MONTH]


def _cat(title: str) -> list[str]:
    return [f"m{_MONTH:02d}-{slugify(title)}"]


UNITS = [
    unit(
        slug=slugify(_TITLES[0]),
        month=_MONTH,
        position=i + 1,
        title=title,
        subtitle=subtitle,
        learning_goals=goals,
        theory_blocks=blocks,
        practice_task=task,
        glossary=glossary,
        category_slugs=_cat(title),
        source_keys=sources,
    )
    for i, (title, subtitle, goals, blocks, task, glossary, sources) in enumerate([
        (
            _TITLES[0],
            "Gefahren erkennen und Schutzmassnahmen anwenden",
            [
                "Gefaehrdungen in der Fertigung benennen.",
                "Fuenf Regeln des Arbeitsschutzes anwenden.",
                "Betriebliche Unterweisung einordnen.",
            ],
            [
                theory(
                    heading="Gefaehrdungen in der Fertigung",
                    body=(
                        "In der Metallbearbeitung drohen Schnittverletzungen, "
                        "Quetschungen an Maschinen, Laerm, heisse Spane und "
                        "Stolpergefahren. Arbeitsschutz beginnt mit der Erkennung "
                        "konkreter Gefahren an deinem Arbeitsplatz."
                    ),
                    key_points=["Maschinen, Werkzeuge, Material und Umgebung bewerten.", "Gefaehrdungsbeurteilung ist Betriebspflicht."],
                ),
                theory(
                    heading="Grundregeln des Arbeitsschutzes",
                    body=(
                        "Technische Schutzmassnahmen (Schutzhaube, Not-Halt), "
                        "organisatorische Regeln (Freigabe, Unterweisung) und "
                        "persoenliche Schutzausruestung ergaenzen sich. Vor "
                        "Arbeitsbeginn pruefst du den sicheren Zustand deines "
                        "Arbeitsplatzes."
                    ),
                    key_points=["Technik, Organisation und PSA zusammen.", "Unterweisung dokumentieren und befolgen."],
                ),
            ],
            "Erstelle fuer deinen Arbeitsplatz eine Gefaehrdungsliste mit mindestens fuenf Punkten und nenne die jeweilige Schutzmassnahme.",
            {"Arbeitsschutz": "Gesamtheit aller Massnahmen zum Schutz der Beschaeftigten.", "Gefaehrdungsbeurteilung": "Systematische Bewertung von Arbeitsrisiken."},
            ["maschfueausbv", "bibb-berufsprofil-maf"],
        ),
        (
            _TITLES[1],
            "Brandschutz und Feuerloescher im Betrieb",
            ["Brandklassen unterscheiden.", "Verhalten bei Brand kennen.", "Feuerloescher richtig waehlen."],
            [
                theory(
                    heading="Brandklassen",
                    body="Brand A: Feststoffe. Brand B: Fluessigkeiten. Brand C: Gase. Brand D: Metalle. Im Betrieb sind Brand A und B am haeufigsten. Falscher Loescher kann Brand verstaerken.",
                    key_points=["Loescher muss zur Brandklasse passen.", "Metallbraende brauchen Spezialloescher."],
                ),
                theory(
                    heading="Verhalten bei Brand",
                    body="Alarm ausloesen, Personen in Sicherheit bringen, Brandbekaempfung nur wenn ungefaehrlich moeglich, Fluchtwege nutzen, Sammelplatz aufsuchen. Niemals Aufzug bei Brand benutzen.",
                    key_points=["Menschenrettung hat Vorrang.", "Fluchtwege freihalten."],
                ),
            ],
            "Pruefe am Feuerloescher in deinem Betrieb Typ und Pruefdatum. Notiere Brandklasse und naechsten Prueftermin.",
            {"Brandklasse": "Einteilung nach brennbarem Material.", "Sammelplatz": "Aufenthaltsort nach Evakuierung."},
            ["maschfueausbv"],
        ),
        (
            _TITLES[2],
            "Gefahrstoffe sicher handhaben",
            ["GHS-Piktogramme lesen.", "Sicherheitsdatenblatt nutzen.", "Lagerung und Kennzeichnung beachten."],
            [
                theory(
                    heading="Kennzeichnung nach GHS",
                    body="Gefahrstoffe tragen Piktogramme fuer Gesundheits- und Umweltgefahren, H- und P-Saetze. Kuehlmittel, Reiniger und Schmierstoffe im Betrieb sind oft Gefahrstoffe.",
                    key_points=["Piktogramm warnt vor Gefahr.", "H-Saetze beschreiben Gefahr, P-Saetze Schutzmassnahmen."],
                ),
                theory(
                    heading="Sicherheitsdatenblatt",
                    body="Das SDB liefert Informationen zu Eigenschaften, Schutzmassnahmen, Erste Hilfe und Entsorgung. Es muss am Arbeitsplatz verfuegbar sein.",
                    key_points=["SDB vor Erstgebrauch lesen.", "Lagerung und Entsorgung laut SDB."],
                ),
            ],
            "Finde ein SDB fuer ein Betriebsmittel in deinem Arbeitsbereich. Notiere zwei H-Saetze und die passenden P-Saetze.",
            {"GHS": "Global harmonisiertes System zur Kennzeichnung.", "SDB": "Sicherheitsdatenblatt mit Gefahrstoffinformationen."},
            ["maschfueausbv", "bze-uelu-maf-metall-kunststoff"],
        ),
        (
            _TITLES[3],
            "Abfall und Betriebsstoffe entsorgen",
            ["Abfallarten trennen.", "Entsorgungswege im Betrieb kennen.", "Umweltrechtliche Grundregeln anwenden."],
            [
                theory(
                    heading="Getrennte Entsorgung",
                    body="Metallspane, Kunststoffreste, Oele und Verpackungen werden getrennt gesammelt. Vermischung erschwert Recycling und kann kostenpflichtig sein.",
                    key_points=["Trennung nach Material und Gefahrstoff.", "Behaelterbeschriftung beachten."],
                ),
                theory(
                    heading="Betriebliche Vorgaben",
                    body="Jeder Betrieb hat Entsorgungsplaene. Als Azubi entsorgst du nur in vorgesehene Behaelter und dokumentierst ggf. Gefahrstoffmengen.",
                    key_points=["Nur vorgesehene Behaelter nutzen.", "Bei Unsicherheit Ausbilder fragen."],
                ),
            ],
            "Erkunde die Entsorgungsstellen in deinem Betrieb und ordne Span, Alt-oel und Kunststoffreste den richtigen Behaeltern zu.",
            {"Altstoff": "Abfall aus Produktion und Wartung.", "Recycling": "Wiederverwertung von Material."},
            ["maschfueausbv"],
        ),
        (
            _TITLES[4],
            "Richtiges Verhalten bei Unfaellen",
            ["Erste Hilfe Grundregeln kennen.", "Unfall melden und absichern.", "Notfallnummern parat haben."],
            [
                theory(
                    heading="Erste Hilfe am Arbeitsplatz",
                    body="Bei Unfall: Gefahren absichern, Notruf 112, Erste Hilfe leisten, Wundversorgung, stabile Seitenlage bei Bewusstlosigkeit. Ersthelfer und Verbandkaesten sind ausgeschildert.",
                    key_points=["Eigenschutz zuerst.", "112 mit genauem Standort waehlen."],
                ),
                theory(
                    heading="Unfall melden",
                    body="Jeder Arbeitsunfall muss dem Vorgesetzten gemeldet werden. Auch Beinahe-Unfaelle dokumentieren - sie zeigen Gefahrenquellen.",
                    key_points=["Sofort melden, auch kleine Verletzungen.", "Beinahe-Unfaelle ernst nehmen."],
                ),
            ],
            "Notiere den Weg zum naechsten Ersthelfer und Verbandkasten von deinem Arbeitsplatz. Miss die Zeit zum Erreichen.",
            {"Ersthelfer": "Im Betrieb ausgebildete Person fuer Erste Hilfe.", "Beinahe-Unfall": "Ereignis ohne Verletzung, aber mit Gefahr."},
            ["maschfueausbv"],
        ),
        (
            _TITLES[5],
            "Umweltschutz in der Produktion",
            ["Ressourcen sparsam nutzen.", "Emissionen und Laerm reduzieren.", "Betriebliche Umweltziele unterstuetzen."],
            [
                theory(
                    heading="Ressourceneffizienz",
                    body="Materialverschnitt, Energieverbrauch und Kuehlmittelverluste belasten Umwelt und Kosten. Richtiges Ruesten und saubere Prozesse sparen Ressourcen.",
                    key_points=["Erst ausrichten, dann produzieren.", "Leckagen sofort melden."],
                ),
                theory(
                    heading="Laerm und Abwaerme",
                    body="Maschinen erzeugen Laerm und Waerme. Gehoerschutz, geschlossene Kuehlkreislaeufe und Wartung reduzieren Belastung fuer Mensch und Umwelt.",
                    key_points=["Gehoerschutz bei Dauerlaerm.", "Kuehlkreislauf pruefen."],
                ),
            ],
            "Nenne drei Massnahmen in deinem Betrieb, die Material oder Energie sparen.",
            {"Ressourceneffizienz": "Moeglichst wenig Material und Energie verbrauchen.", "Emission": "Stoffausstoss in Luft, Wasser oder Boden."},
            ["maschfueausbv", "bibb-berufsprofil-maf"],
        ),
        (
            _TITLES[6],
            "Persoenliche Schutzausruestung",
            ["PSA-Arten zuordnen.", "PSA richtig anlegen.", "Pflege und Ersatz kennen."],
            [
                theory(
                    heading="Arten der PSA",
                    body="Schutzbrille, Gehoerschutz, Sicherheitsschuhe, Handschuhe und Atemschutz schuetzen vor spezifischen Gefahren. PSA ist letzte Schutzebene nach Technik und Organisation.",
                    key_points=["PSA passend zur Gefaehrdung.", "Sicherheitsschuhe im Produktionsbereich Pflicht."],
                ),
                theory(
                    heading="Richtige Anwendung",
                    body="PSA muss passen, sauber und unbeschaedigt sein. Handschuhe an rotierenden Maschinen koennen gefaehrlich sein - oft ohne Handschuhe arbeiten.",
                    key_points=["Passform pruefen.", "Bei Schaeden sofort ersetzen."],
                ),
            ],
            "Pruefe deine heute getragene PSA: Ist sie vollstaendig, sauber und fuer deine Taetigkeit geeignet?",
            {"PSA": "Persoenliche Schutzausruestung.", "Gehoerschutz": "Schutz vor Laermbelastung."},
            ["maschfueausbv"],
        ),
        (
            _TITLES[7],
            "Gefahren frueh erkennen",
            ["Typische Gefahrensymbole deuten.", "Unsichere Situationen melden.", "Praeventives Handeln ueben."],
            [
                theory(
                    heading="Warnzeichen und Symbole",
                    body="Piktogramme fuer Spannung, Laser, Quetschgefahr und Gefahrstoffe muessen erkannt werden. Blockierte Not-Aus-Taster und fehlende Abdeckungen sind sofort zu melden.",
                    key_points=["Symbole am Arbeitsplatz kennen.", "Maengel nicht ignorieren."],
                ),
                theory(
                    heading="Praevention",
                    body="Aufraeumen, Werkzeuge sichern, Leitungen fuehren und Maschinen nur im freigegebenen Zustand nutzen - das verhindert Unfaelle.",
                    key_points=["Ordnung und Sauberkeit (5S).", "Freigabe vor Inbetriebnahme."],
                ),
            ],
            "Gehe deinen Arbeitsplatz ab und finde drei potenzielle Gefahrenquellen. Beschreibe die Gegenmassnahme.",
            {"Not-Halt": "Sofortiges Abschalten der Anlage in Gefahr.", "Praevention": "Vorbeugende Massnahmen gegen Unfaelle."},
            ["maschfueausbv"],
        ),
        (
            _TITLES[8],
            "Notfallmassnahmen und Alarmplan",
            ["Alarmplan lesen.", "Sammelplatz und Fluchtwege kennen.", "Rollen bei Evakuierung verstehen."],
            [
                theory(
                    heading="Alarmplan im Betrieb",
                    body="Der Alarmplan regelt Verhalten bei Brand, Unfall, Gefahrstoffaustritt oder Stromausfall. Fluchtwege sind gruen markiert, Sammelplaetze ausgeschildert.",
                    key_points=["Alarmplan vor Arbeitsbeginn kennen.", "Fluchtwege nie blockieren."],
                ),
                theory(
                    heading="Evakuierung",
                    body="Bei Alarm ruhig aber zuegig den kuerzesten Fluchtweg nutzen, Aufzug meiden, am Sammelplatz melden und auf Anweisungen warten.",
                    key_points=["Keine persoenlichen Gegenstaende holen.", "Kopfzaehlung am Sammelplatz."],
                ),
            ],
            "Lies den Alarmplan deines Betriebs und zeichne den kuerzesten Fluchtweg von deinem Arbeitsplatz zum Sammelplatz.",
            {"Evakuierung": "Geraumtes Verlassen des Gebaeudes.", "Alarmplan": "Betriebliche Notfallanweisung."},
            ["maschfueausbv"],
        ),
        (
            _TITLES[9],
            "Typische IHK-Fragen zu SHU trainieren",
            ["SHU-Fragen sicher loesen.", "Gefaehrdungsbeurteilung erklaeren.", "PSA und Erste Hilfe pruefungsreif wiederholen."],
            [
                theory(
                    heading="Typische Pruefungsthemen",
                    body="In schriftlichen Pruefungen kommen Fragen zu Gefahrstoffen, PSA, Erste Hilfe, Brandschutz und Jugendarbeitsschutz. Antworten basieren auf gesetzlichen Regeln, nicht auf Betriebsgewohnheiten.",
                    key_points=["Gesetz vor Betriebsregel.", "Jugendarbeitsschutz fuer unter 18."],
                ),
                theory(
                    heading="Lernstrategie",
                    body="Wiederhole Piktogramme, H/P-Saetze und die fuenf Sicherheitsregeln. Uebe mit Single-Choice und offenen Kurzantworten.",
                    key_points=["Piktogramme auswendig erkennen.", "Notfallnummern kennen."],
                ),
            ],
            "Beantworte schriftlich: Nenne drei Pflichten des Auszubildenden im Arbeitsschutz und eine Recht des Auszubildenden.",
            {"Jugendarbeitsschutz": "Besondere Schutzregeln fuer Auszubildende unter 18.", "SHU": "Sicherheit und Gesundheitsschutz bei der Arbeit."},
            ["ihk-aachen-pruefungs-faq", "maschfueausbv"],
        ),
    ])
]
