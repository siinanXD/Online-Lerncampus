"""Ausformulierte Lerneinheiten fuer Maschinen- und Anlagenfuehrer/-in.

Jede Lerneinheit behandelt genau ein Thema von der Theorie ueber die Normen bis
zur Uebung und uebergibt danach an ihre Fragekategorien. Nach zehn Einheiten
folgt eine Checkpoint-Pruefung im Format der schriftlichen IHK-Pruefung.

Fachlicher Stand: Die Inhalte sind eigenstaendig formuliert und stuetzen sich
auf die in ``app/data/sources.py`` gefuehrten Quellen sowie die genannten
Normen. Sie stehen bewusst auf ``ReviewStatus.DRAFT`` und muessen vor dem
Einsatz in der Ausbildung fachlich freigegeben werden - siehe
``docs/content-governance.md``.
"""

from app.models.domain import (
    AnswerFormat,
    GradingCriterion,
    LearningUnit,
    OpenQuestion,
    ReviewStatus,
    TheoryBlock,
)

MESSSCHIEBER = LearningUnit(
    slug="messschieber",
    month=1,
    position=7,
    title="Messschieber",
    subtitle="Aufbau, Nonius und normgerechtes Messen nach DIN 862",
    learning_goals=[
        "Die Bauteile eines Messschiebers benennen und ihre Funktion erklaeren.",
        "Einen Nonius mit 0,05 mm und 0,02 mm Ablesung sicher ablesen.",
        "Aussen-, Innen- und Tiefenmass fachgerecht aufnehmen.",
        "Typische Messabweichungen erkennen und vermeiden.",
    ],
    theory_blocks=[
        TheoryBlock(
            heading="Wozu der Messschieber dient",
            body=(
                "Der Messschieber ist das Universalmessmittel in der Fertigung. Mit "
                "einem einzigen Geraet nimmst du Aussenmasse, Innenmasse und "
                "Tiefenmasse auf. Er arbeitet nach dem Prinzip einer festen "
                "Hauptskala auf der Schiene und einer beweglichen Hilfsskala, dem "
                "Nonius, auf dem Schieber. Der Messschieber ist schnell und "
                "vielseitig, aber weniger genau als eine Buegelmessschraube - "
                "fuer Toleranzen unter etwa 0,05 mm greifst du zum Mikrometer."
            ),
            key_points=[
                "Ein Messmittel fuer Aussen-, Innen- und Tiefenmass.",
                "Hauptskala auf der Schiene, Nonius auf dem Schieber.",
                "Fuer enge Toleranzen nimmst du die Buegelmessschraube.",
            ],
            norm_references=["DIN 862"],
        ),
        TheoryBlock(
            heading="Aufbau und Bauteile",
            body=(
                "Die Schiene traegt die Hauptskala in Millimetern. Der Schieber "
                "laeuft darauf und traegt den Nonius. Die grossen Messschenkel "
                "unten greifen das Werkstueck von aussen. Die kleinen Messschnaebel "
                "oben messen Bohrungen und Nuten von innen. Hinten schiebt sich die "
                "Tiefenmessstange aus der Schiene heraus. Die Feststellschraube "
                "klemmt den Schieber, damit sich der Messwert beim Ablesen nicht "
                "verschiebt."
            ),
            key_points=[
                "Schiene mit Hauptskala, Schieber mit Nonius.",
                "Messschenkel = aussen, Messschnaebel = innen,"
                " Tiefenmassstange = Tiefe.",
                "Feststellschraube sichert den Messwert vor dem Ablesen.",
            ],
            norm_references=["DIN 862"],
        ),
        TheoryBlock(
            heading="Den Nonius ablesen",
            body=(
                "Der Nonius macht Bruchteile eines Millimeters sichtbar. Bei einem "
                "Nonius mit 0,05 mm sind 20 Noniusstriche auf einer Laenge von 19 mm "
                "aufgetragen; jeder Noniusstrich liegt also 0,05 mm vor dem "
                "zugehoerigen Millimeterstrich. Bei 0,02 mm sind es 50 Striche auf "
                "49 mm.\n\n"
                "So liest du ab: Zuerst nimmst du am Nullstrich des Nonius den "
                "vollen Millimeterwert von der Hauptskala. Dann suchst du den "
                "einen Noniusstrich, der genau mit einem Strich der Hauptskala "
                "fluchtet. Seine Nummer mal dem Noniuswert ergibt die "
                "Nachkommastelle. Beispiel: Nullstrich steht hinter 24 mm, der "
                "7. Noniusstrich fluchtet, Nonius 0,05 mm - das Mass betraegt "
                "24 mm + 7 x 0,05 mm = 24,35 mm."
            ),
            key_points=[
                "0,05 mm: 20 Striche auf 19 mm. 0,02 mm: 50 Striche auf 49 mm.",
                "Ganze Millimeter am Nullstrich des Nonius ablesen.",
                "Nachkommastelle am fluchtenden Noniusstrich ablesen.",
            ],
            norm_references=["DIN 862"],
        ),
        TheoryBlock(
            heading="Richtig messen - und was schiefgeht",
            body=(
                "Pruefe vor jeder Messung den Nullpunkt: Messschenkel schliessen, "
                "Nullstriche muessen fluchten. Messflaechen und Werkstueck muessen "
                "sauber und gratfrei sein - ein Span unter dem Messschenkel "
                "verfaelscht das Mass sofort.\n\n"
                "Messe mit gleichmaessiger, geringer Messkraft. Druckst du zu "
                "stark, federt der Schieber und das Mass faellt zu klein aus. "
                "Setze den Messschieber rechtwinklig an; ein verkantetes Geraet "
                "misst zu gross (Kippfehler). Miss moeglichst nah an der Schiene, "
                "denn der Messschieber verletzt das Abbesche Komparatorprinzip: "
                "Massstab und Messstrecke liegen nicht auf einer Linie, weshalb "
                "sich ein Kippen direkt als Abweichung auswirkt.\n\n"
                "Bezugstemperatur fuer Laengenmessungen ist 20 Grad Celsius. Ein "
                "frisch bearbeitetes, warmes Werkstueck misst du zu gross."
            ),
            key_points=[
                "Immer zuerst den Nullpunkt pruefen.",
                "Sauber, gratfrei, rechtwinklig und gefuehlvoll messen.",
                "Kippfehler: Der Messschieber haelt das Abbesche Prinzip nicht ein.",
                "Bezugstemperatur 20 Grad Celsius.",
            ],
            norm_references=["DIN 862", "DIN EN ISO 1"],
        ),
    ],
    practice_task=(
        "Nimm einen Messschieber mit 0,05 mm Nonius. Pruefe den Nullpunkt. Miss an "
        "einem Drehteil den Aussendurchmesser an drei Stellen, den "
        "Bohrungsdurchmesser und die Bohrungstiefe. Notiere alle fuenf Messwerte "
        "auf zwei Nachkommastellen und begruende, warum die drei "
        "Durchmesserwerte voneinander abweichen koennen."
    ),
    glossary={
        "Nonius": (
            "Hilfsskala auf dem Schieber, die Bruchteile eines Millimeters "
            "ablesbar macht."
        ),
        "Messschenkel": "Die grossen Backen fuer die Aussenmessung.",
        "Messschnaebel": "Die kleinen Backen oben fuer die Innenmessung.",
        "Kippfehler": (
            "Messabweichung durch verkantetes Ansetzen; das Mass faellt zu gross aus."
        ),
        "Abbesches Komparatorprinzip": (
            "Massstab und Messstrecke sollen auf einer Linie liegen. Der "
            "Messschieber erfuellt das nicht, die Buegelmessschraube schon."
        ),
        "Bezugstemperatur": (
            "20 Grad Celsius, die Normtemperatur fuer Laengenmessungen."
        ),
    },
    category_slugs=["m01-messen-und-pruefen"],
    source_keys=["bze-uelu-maf-metall-kunststoff", "din-862"],
    review_status=ReviewStatus.DRAFT,
    estimated_minutes=14,
)

MESSSCHIEBER_OPEN_QUESTIONS = [
    OpenQuestion(
        question_id="open-messschieber-01",
        category_slug="m01-messen-und-pruefen",
        prompt=(
            "Benennen Sie vier Bauteile eines Messschiebers und geben Sie zu jedem "
            "Bauteil an, wofuer es beim Messen gebraucht wird."
        ),
        answer_format=AnswerFormat.SHORT_TEXT,
        sample_solution=(
            "Schiene mit Hauptskala: traegt die Millimeterteilung. Schieber mit "
            "Nonius: macht die Nachkommastellen ablesbar. Messschenkel: "
            "Aussenmessung. Messschnaebel: Innenmessung. Tiefenmassstange: "
            "Messung von Bohrungs- und Nuttiefen. Feststellschraube: sichert den "
            "Schieber vor dem Ablesen."
        ),
        criteria=[
            GradingCriterion(f"Bauteil {i} mit richtiger Funktion", 1)
            for i in range(1, 5)
        ],
        source_keys=["din-862"],
    ),
    OpenQuestion(
        question_id="open-messschieber-02",
        category_slug="m01-messen-und-pruefen",
        prompt=(
            "An einem Messschieber mit einem Nonius von 0,05 mm steht der "
            "Nullstrich des Nonius zwischen 24 mm und 25 mm. Der 7. Noniusstrich "
            "fluchtet mit einem Strich der Hauptskala. Ermitteln Sie das Messergebnis "
            "und stellen Sie den Rechenweg dar."
        ),
        answer_format=AnswerFormat.CALCULATION,
        sample_solution=(
            "Ganze Millimeter am Nullstrich: 24 mm. Nachkommaanteil: 7 x 0,05 mm "
            "= 0,35 mm. Messergebnis: 24 mm + 0,35 mm = 24,35 mm."
        ),
        criteria=[
            GradingCriterion("Ganze Millimeter korrekt abgelesen (24 mm)", 1),
            GradingCriterion("Nachkommaanteil korrekt berechnet (7 x 0,05 mm)", 2),
            GradingCriterion("Ergebnis mit Einheit angegeben (24,35 mm)", 1),
        ],
        source_keys=["din-862"],
    ),
    OpenQuestion(
        question_id="open-messschieber-03",
        category_slug="m01-messen-und-pruefen",
        prompt=(
            "Skizzieren Sie einen Messschieber in der Seitenansicht. Beschriften Sie "
            "Schiene, Schieber, Nonius, Messschenkel, Messschnaebel und "
            "Tiefenmassstange. Kennzeichnen Sie durch einen Pfeil, an welcher Stelle "
            "ein Aussendurchmesser aufgenommen wird."
        ),
        answer_format=AnswerFormat.SKETCH,
        sample_solution=(
            "Erwartet wird eine Seitenansicht mit waagerechter Schiene, "
            "aufgesetztem Schieber, den grossen Messschenkeln unten, den kleinen "
            "Messschnaebeln oben, der hinten austretenden Tiefenmassstange sowie "
            "einem Pfeil zwischen den Messflaechen der grossen Messschenkel."
        ),
        criteria=[
            GradingCriterion("Grundform mit Schiene und Schieber erkennbar", 2),
            GradingCriterion("Alle sechs Bauteile korrekt beschriftet", 3),
            GradingCriterion("Messstelle fuer das Aussenmass gekennzeichnet", 1),
        ],
        source_keys=["din-862"],
    ),
]

LEARNING_UNITS: list[LearningUnit] = [MESSSCHIEBER]
OPEN_QUESTIONS: list[OpenQuestion] = [*MESSSCHIEBER_OPEN_QUESTIONS]

LEARNING_UNITS_BY_SLUG = {unit.slug: unit for unit in LEARNING_UNITS}
OPEN_QUESTIONS_BY_ID = {question.question_id: question for question in OPEN_QUESTIONS}
