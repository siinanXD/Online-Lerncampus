"""Seed curriculum for Maschinen- und Anlagenfuehrer."""

from app.models.domain import CurriculumMonth, LearningModule, Occupation

SUPPORTED_OCCUPATIONS: list[Occupation] = [
    Occupation(
        slug="maschinen-und-anlagenfuehrer",
        title="Maschinen- und Anlagenfuehrer/-in",
        duration_months=24,
        specializations=["metall-und-kunststofftechnik"],
    )
]

COMMON_SOURCES = [
    "ihk-aachen-berufsseite-maf",
    "bibb-berufsprofil-maf",
    "maschfueausbv",
]

BZE_SOURCES = [
    "bze-uelu-maf-metall-kunststoff",
    "maschfueausbv",
]

EXAM_SOURCES = [
    "ihk-aachen-pruefungs-faq",
    "ihk-aachen-berufsseite-maf",
    "maschfueausbv",
]

MACHINE_OPERATOR_CURRICULUM: list[CurriculumMonth] = [
    CurriculumMonth(
        month=1,
        year=1,
        title="Einstieg, Berufsbild und Arbeitsrecht",
        focus_area="Berufsstart und betriebliche Orientierung",
        learning_goals=[
            "Rechte und Pflichten aus dem Ausbildungsvertrag erklaeren.",
            "Das Berufsbild in eigenen Worten beschreiben.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=2,
        year=1,
        title="Sicherheit, Gesundheit und Umweltschutz",
        focus_area="Sichere Arbeit in Produktionsumgebungen",
        learning_goals=[
            "Gefahren erkennen und passende Schutzmassnahmen nennen.",
            "Umweltgerechten Umgang mit Stoffen und Abfaellen begruenden.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=3,
        year=1,
        title="Werk-, Betriebs- und Hilfsstoffe",
        focus_area="Werkstoffe identifizieren und sicher einsetzen",
        learning_goals=[
            "Werkstoffe nach Verwendungszweck unterscheiden.",
            "Betriebs- und Hilfsstoffe vorschriftsgerecht verwenden.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=4,
        year=1,
        title="Technische Kommunikation",
        focus_area="Technische Unterlagen lesen und anwenden",
        learning_goals=[
            "Informationen aus Zeichnungen und Tabellen entnehmen.",
            "Produktionsdaten nachvollziehbar dokumentieren.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=5,
        year=1,
        title="Arbeitsablaeufe planen",
        focus_area="Arbeitsplanung und Materialbereitstellung",
        learning_goals=[
            "Arbeitsschritte sinnvoll ordnen.",
            "Werkzeuge und Materialien passend vorbereiten.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=6,
        year=1,
        title="Pruefen und Messen",
        focus_area="Pruefmittel, Pruefverfahren und Dokumentation",
        learning_goals=[
            "Geeignete Pruefmittel auswaehlen.",
            "Pruefergebnisse bewerten und dokumentieren.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=7,
        year=1,
        title="Fertigungstechniken I",
        focus_area="Manuelle Fertigungstechniken",
        learning_goals=[
            "Manuelle Fertigungstechniken unterscheiden.",
            "Arbeitsergebnisse pruefen und bewerten.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=8,
        year=1,
        title="Pneumatik Grundlagen",
        focus_area="Druckluft, Ventile und Zylinder",
        learning_goals=[
            "Pneumatische Grundkomponenten benennen.",
            "Einfache pneumatische Funktionen erklaeren.",
        ],
        source_keys=BZE_SOURCES,
    ),
    CurriculumMonth(
        month=9,
        year=1,
        title="Drehen und Fraesen",
        focus_area="Maschinelle Fertigungstechniken",
        learning_goals=[
            "Spanende Verfahren unterscheiden.",
            "Werkzeugauswahl fachlich begruenden.",
        ],
        source_keys=BZE_SOURCES,
    ),
    CurriculumMonth(
        month=10,
        year=1,
        title="Grundbildung Metall",
        focus_area="Metallbearbeitung und Basisprozesse",
        learning_goals=[
            "Metallische Werkstoffe bearbeiten.",
            "Bearbeitungsergebnisse kontrollieren.",
        ],
        source_keys=BZE_SOURCES,
    ),
    CurriculumMonth(
        month=11,
        year=1,
        title="Materialfluss",
        focus_area="Transport, Lagerung und Produktionsfluss",
        learning_goals=[
            "Materialfluss im Arbeitsbereich sicherstellen.",
            "Stoerungen im Materialfluss beschreiben.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=12,
        year=1,
        title="Zwischenpruefung Sprint",
        focus_area="Pruefungsvorbereitung Theorie und Praxis",
        learning_goals=[
            "Praktische Aufgaben strukturiert planen.",
            "Pruefungsnahe Fragen sicher bearbeiten.",
        ],
        source_keys=EXAM_SOURCES,
        is_exam_preparation=True,
    ),
    CurriculumMonth(
        month=13,
        year=2,
        title="Werkstoffeigenschaften",
        focus_area="Metall- und Kunststofftechnik",
        learning_goals=[
            "Werkstoffeigenschaften beurteilen.",
            "Werkstoffe nach Verwendungszweck auswaehlen.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=14,
        year=2,
        title="Arbeitsablaeufe abstimmen",
        focus_area="Koordination mit vor- und nachgelagerten Bereichen",
        learning_goals=[
            "Arbeitsablaeufe wirtschaftlich planen.",
            "Uebergaben nachvollziehbar dokumentieren.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=15,
        year=2,
        title="Fuegen, Spanen und Umformen",
        focus_area="Branchenspezifische Fertigungstechniken",
        learning_goals=[
            "Fertigungsverfahren produktbezogen auswaehlen.",
            "Bauteile nach technischen Unterlagen herstellen.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=16,
        year=2,
        title="Toleranzen und Oberflaechen",
        focus_area="Mass-, Form- und Lagetoleranzen",
        learning_goals=[
            "Toleranzen technischen Anforderungen zuordnen.",
            "Oberflaechenbeschaffenheit fachlich einordnen.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=17,
        year=2,
        title="Steuerungs- und Regelungstechnik",
        focus_area="Bedienen von Steuerungs- und Regelungseinrichtungen",
        learning_goals=[
            "Steuerungs- und Regelungseinrichtungen unterscheiden.",
            "Sicherheitsvorschriften beim Bedienen beachten.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=18,
        year=2,
        title="Anlagen ruesten",
        focus_area="Produktionsmaschinen vorbereiten",
        learning_goals=[
            "Maschinen nach Vorgabe ruesten und umruesten.",
            "Inbetriebnahme fachgerecht vorbereiten.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=19,
        year=2,
        title="Prozessdaten optimieren",
        focus_area="Produktionsprozesse einstellen und ueberwachen",
        learning_goals=[
            "Prozessdaten einstellen und bewerten.",
            "Abweichungen im Produktionsprozess erkennen.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=20,
        year=2,
        title="Stoerungen beheben",
        focus_area="Stoerungssuche und Prozesssicherung",
        learning_goals=[
            "Stoerungsursachen systematisch eingrenzen.",
            "Geeignete Korrekturmassnahmen einleiten.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=21,
        year=2,
        title="Wartung und Inspektion",
        focus_area="Betriebsbereitschaft sicherstellen",
        learning_goals=[
            "Wartungsarbeiten nach Vorgabe durchfuehren.",
            "Verschleissteile erkennen und Austausch veranlassen.",
        ],
        source_keys=COMMON_SOURCES,
    ),
    CurriculumMonth(
        month=22,
        year=2,
        title="Qualitaetsmanagement und Kunststoffe",
        focus_area="Qualitaetssicherung und Kunststofftechnik",
        learning_goals=[
            "Qualitaetsabweichungen erkennen.",
            "Korrekturmassnahmen fachlich begruenden.",
        ],
        source_keys=BZE_SOURCES,
    ),
    CurriculumMonth(
        month=23,
        year=2,
        title="Blechkurs und Praxisfall",
        focus_area="Praxisnahe Fertigungs- und Pruefaufgabe",
        learning_goals=[
            "Blechbearbeitung als Prozess planen.",
            "Arbeitsergebnisse pruefen und dokumentieren.",
        ],
        source_keys=BZE_SOURCES,
    ),
    CurriculumMonth(
        month=24,
        year=2,
        title="Abschlusspruefung Sprint",
        focus_area="Praktische und schriftliche Abschlusspruefung",
        learning_goals=[
            "Praktische Pruefungsaufgaben strukturiert bearbeiten.",
            "Produktionstechnik und Produktionsplanung wiederholen.",
        ],
        source_keys=EXAM_SOURCES,
        is_exam_preparation=True,
    ),
]

MACHINE_OPERATOR_MODULES: list[LearningModule] = [
    LearningModule(
        slug=f"mission-{entry.month:02d}",
        month=entry.month,
        title=entry.title,
        mission_type="exam_sprint" if entry.is_exam_preparation else "learning_mission",
        lesson_goal=entry.learning_goals[0],
        quiz_focus=entry.focus_area,
    )
    for entry in MACHINE_OPERATOR_CURRICULUM
]

