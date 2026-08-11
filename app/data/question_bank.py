"""Generated question categories and original PAL-style practice questions."""

from app.data.machine_operator import MACHINE_OPERATOR_CURRICULUM
from app.models.domain import PracticeExam, QuestionCategory, QuizQuestion

SUBCHAPTER_TITLES = [
    "Grundbegriffe",
    "Sicherheit",
    "Technische Kommunikation",
    "Werkzeuge und Hilfsmittel",
    "Material und Werkstoffe",
    "Prozess und Arbeitsplanung",
    "Messen und Pruefen",
    "Qualitaet",
    "Stoerungen",
    "Pruefungsaufgaben",
]


def _slug(value: str) -> str:
    """Return an ASCII slug for deterministic seed ids."""
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        " ": "-",
        ",": "",
        "/": "-",
    }
    slug = value.lower()
    for source, target in replacements.items():
        slug = slug.replace(source, target)
    return "".join(char for char in slug if char.isalnum() or char == "-")


def _build_categories() -> list[QuestionCategory]:
    """Build ten question categories for every curriculum month."""
    categories: list[QuestionCategory] = []
    for month in MACHINE_OPERATOR_CURRICULUM:
        for index, title in enumerate(SUBCHAPTER_TITLES, start=1):
            categories.append(
                QuestionCategory(
                    slug=f"m{month.month:02d}-{_slug(title)}",
                    month=month.month,
                    chapter_title=month.title,
                    subchapter_number=index,
                    title=title,
                    description=(
                        f"{month.title}: {title} als Fragekategorie fuer "
                        "Lernkarten, Trainingsfragen und Checkpoints."
                    ),
                )
            )
    return categories


QUESTION_CATEGORIES = _build_categories()


FIRST_CHAPTER = {
    "title": "Kapitel 1: Einstieg, Berufsbild und Arbeitsrecht",
    "mission_goal": (
        "Du verstehst, was Maschinen- und Anlagenfuehrer tun, welche Pflichten "
        "in der Ausbildung wichtig sind und warum Sicherheit von Anfang an zaehlt."
    ),
    "fachkunde": [
        (
            "Maschinen- und Anlagenfuehrer richten Produktionsmaschinen ein, "
            "bedienen sie, ueberwachen den Prozess und reagieren bei Stoerungen."
        ),
        (
            "Im Betrieb arbeitest du nach technischen Unterlagen, "
            "Sicherheitsregeln und Qualitaetsvorgaben. Gute Dokumentation ist "
            "ein Teil der Arbeit, nicht nur Papierkram."
        ),
        (
            "In der Pruefung werden typische Situationen als Multiple-Choice-"
            "Aufgaben abgefragt. Trainiert werden Fachwissen, Lesen technischer "
            "Darstellungen und sichere Entscheidungen."
        ),
    ],
    "category_slugs": [
        "m01-grundbegriffe",
        "m01-sicherheit",
        "m01-technische-kommunikation",
        "m01-werkzeuge-und-hilfsmittel",
        "m01-material-und-werkstoffe",
        "m01-prozess-und-arbeitsplanung",
        "m01-messen-und-pruefen",
        "m01-qualitaet",
        "m01-stoerungen",
        "m01-pruefungsaufgaben",
    ],
    "checkpoint_exam_id": "exam-01",
}


QUESTION_TEMPLATES = [
    {
        "prompt": "Welche Aussage passt am besten zum Thema {topic}?",
        "correct": "{goal}",
        "distractors": [
            "Alle Arbeitsschritte ohne technische Unterlagen ausfuehren.",
            "Sicherheitsregeln erst nach einer Stoerung beachten.",
            "Pruefergebnisse nicht dokumentieren.",
            "Werkzeuge unabhaengig vom Werkstoff auswaehlen.",
        ],
        "explanation": (
            "Die richtige Antwort folgt aus dem Lernziel: {goal}. In der "
            "Pruefung wird meist die fachlich sichere und dokumentierte "
            "Vorgehensweise gesucht."
        ),
        "style": "single_choice",
    },
    {
        "prompt": (
            "Eine Anlage soll fuer {topic} vorbereitet werden. Was ist der "
            "sinnvollste erste Schritt?"
        ),
        "correct": "Auftrag, Zeichnung, Material und Sicherheitsvorgaben pruefen.",
        "distractors": [
            "Maschine sofort starten und danach messen.",
            "Nur die Geschwindigkeit erhoehen.",
            "Werkstueck ohne Pruefung einspannen.",
            "Abweichungen erst am Schichtende melden.",
        ],
        "explanation": (
            "Vor dem Bedienen oder Ruesten muessen Vorgaben, Material, "
            "Werkzeuge und Schutzmassnahmen klar sein."
        ),
        "style": "situation",
    },
    {
        "prompt": (
            "Bei einer PAL-aehnlichen Aufgabe zu {topic} sind fuenf Antworten "
            "gegeben. Welche Antwort beschreibt korrektes Pruefungsverhalten?"
        ),
        "correct": (
            "Antworten vergleichen, Fachbegriff pruefen und eindeutig markieren."
        ),
        "distractors": [
            "Mehrere Antworten markieren, wenn man unsicher ist.",
            "Die laengste Antwort immer auswaehlen.",
            "Zeichnungen ignorieren und nur raten.",
            "Korrekturen ohne klare Markierung vornehmen.",
        ],
        "explanation": (
            "PAL-Aufgaben erfordern genaues Lesen, eindeutige Markierung und "
            "fachliche Begruendung."
        ),
        "style": "exam_strategy",
    },
    {
        "prompt": (
            "Welche Handlung hilft am meisten, Defizite im Bereich {topic} "
            "zu erkennen?"
        ),
        "correct": (
            "Falsche Antworten nach Kategorie auswerten und gezielt wiederholen."
        ),
        "distractors": [
            "Nur bereits richtige Fragen trainieren.",
            "Schwierige Fragen ausblenden.",
            "Lernstand ohne Kategorien speichern.",
            "Nach einem Fehler sofort das Thema wechseln.",
        ],
        "explanation": (
            "Defizite werden sichtbar, wenn Fehler je Kategorie getrackt und "
            "wiederholt werden."
        ),
        "style": "learning_strategy",
    },
]

FIRST_CHAPTER_QUESTIONS = [
    {
        "prompt": (
            "Welche Aufgabe gehoert typischerweise zum Beruf "
            "Maschinen- und Anlagenfuehrer?"
        ),
        "correct": "Maschinen einrichten, bedienen und den Prozess ueberwachen.",
        "distractors": [
            "Kundenfahrzeuge im Strassenverkehr pruefen.",
            "Gebaeudeinstallationen abnehmen.",
            "Lohnabrechnungen fuer Mitarbeitende erstellen.",
            "Ausschliesslich technische Zeichnungen archivieren.",
        ],
        "explanation": (
            "Der Beruf ist auf Produktionsanlagen ausgerichtet: einrichten, "
            "bedienen, ueberwachen, warten und Qualitaet sichern."
        ),
        "style": "occupation_basics",
    },
    {
        "prompt": "Was ist vor dem Start einer Produktionsmaschine zuerst zu pruefen?",
        "correct": (
            "Arbeitsauftrag, Schutzvorrichtungen und sichere Betriebsbereitschaft."
        ),
        "distractors": [
            "Nur die spaetere Stueckzahl.",
            "Nur die Farbe des Werkstuecks.",
            "Ob die Maschine moeglichst laut laeuft.",
            "Ob die Dokumentation nach Schichtende ausgefuellt werden kann.",
        ],
        "explanation": (
            "Sicherheit und Auftrag muessen vor dem Start klar sein. Das ist "
            "Grundlage fuer sichere und nachvollziehbare Produktion."
        ),
        "style": "safety",
    },
    {
        "prompt": "Wofuer werden technische Zeichnungen in der Fertigung genutzt?",
        "correct": "Sie liefern Masse, Formen, Toleranzen und Bearbeitungshinweise.",
        "distractors": [
            "Sie ersetzen alle Sicherheitsregeln.",
            "Sie zeigen nur den Verkaufspreis.",
            "Sie sind nur fuer die Personalabteilung wichtig.",
            "Sie duerfen bei der Pruefung nicht beachtet werden.",
        ],
        "explanation": (
            "Technische Zeichnungen sind Arbeitsgrundlage. Sie helfen, Bauteile "
            "richtig herzustellen und zu pruefen."
        ),
        "style": "technical_communication",
    },
    {
        "prompt": "Welches Verhalten ist bei der Werkzeugauswahl fachlich richtig?",
        "correct": "Werkstoff, Verfahren, Maschine und Arbeitsschutz beruecksichtigen.",
        "distractors": [
            "Immer das groesste Werkzeug verwenden.",
            "Werkzeuge ohne Sichtpruefung einsetzen.",
            "Nur nach Farbe des Werkzeugs entscheiden.",
            "Verschlissene Werkzeuge weiterverwenden, bis sie brechen.",
        ],
        "explanation": (
            "Werkzeuge werden nach Aufgabe, Werkstoff, Maschine und Sicherheit "
            "ausgewaehlt."
        ),
        "style": "tools",
    },
    {
        "prompt": "Warum ist die Werkstoffkenntnis fuer diesen Beruf wichtig?",
        "correct": "Werkstoffe beeinflussen Bearbeitung, Werkzeugwahl und Qualitaet.",
        "distractors": [
            "Werkstoffe haben keinen Einfluss auf die Fertigung.",
            "Alle Kunststoffe und Metalle werden gleich bearbeitet.",
            "Werkstoffangaben sind nur fuer den Einkauf relevant.",
            "Werkstoffe muessen in Pruefungen nicht unterschieden werden.",
        ],
        "explanation": (
            "Metalle und Kunststoffe verhalten sich unterschiedlich. Das wirkt "
            "sich auf Verfahren, Parameter und Pruefung aus."
        ),
        "style": "materials",
    },
    {
        "prompt": "Was gehoert zu einer guten Arbeitsplanung?",
        "correct": "Arbeitsschritte, Material, Werkzeuge und Pruefpunkte festlegen.",
        "distractors": [
            "Ohne Plan beginnen und Fehler spaeter suchen.",
            "Nur die Pause planen.",
            "Pruefmittel erst nach Fertigstellung suchen.",
            "Arbeitsunterlagen nicht lesen.",
        ],
        "explanation": (
            "Arbeitsplanung reduziert Fehler und macht die Produktion "
            "nachvollziehbar."
        ),
        "style": "process_planning",
    },
    {
        "prompt": "Wann ist ein Messergebnis besonders brauchbar?",
        "correct": (
            "Wenn geeignetes Pruefmittel und korrekte Messmethode verwendet werden."
        ),
        "distractors": [
            "Wenn das Ergebnis nur geschaetzt wird.",
            "Wenn ein defektes Pruefmittel benutzt wird.",
            "Wenn die Einheit weggelassen wird.",
            "Wenn nur einmal ungenau gemessen wird.",
        ],
        "explanation": (
            "Pruefen und Messen erfordert passende Pruefmittel, saubere Methode "
            "und nachvollziehbare Dokumentation."
        ),
        "style": "measurement",
    },
    {
        "prompt": "Was ist ein typisches Ziel der Qualitaetssicherung?",
        "correct": (
            "Abweichungen erkennen und gleichbleibende Produktqualitaet sichern."
        ),
        "distractors": [
            "Fehler absichtlich nicht dokumentieren.",
            "Pruefungen nur bei Reklamationen durchfuehren.",
            "Maschinen ohne Vorgaben betreiben.",
            "Messwerte nach Gefuehl veraendern.",
        ],
        "explanation": (
            "Qualitaetssicherung soll Fehler vermeiden, Abweichungen erkennen "
            "und Prozesse verbessern."
        ),
        "style": "quality",
    },
    {
        "prompt": "Wie sollte man bei einer Stoerung an einer Anlage zuerst reagieren?",
        "correct": (
            "Sicher handeln, Anlage nach Vorgabe stoppen und Ursache eingrenzen."
        ),
        "distractors": [
            "Schutzeinrichtungen ueberbruecken.",
            "Weiterproduzieren, bis Ausschuss entsteht.",
            "Bauteile ohne Freigabe ausbauen.",
            "Die Stoerung nicht melden.",
        ],
        "explanation": (
            "Bei Stoerungen haben Sicherheit, Vorgaben und systematische "
            "Fehlersuche Vorrang."
        ),
        "style": "troubleshooting",
    },
    {
        "prompt": (
            "Wie gilt eine Frage in dieser Lernapp als abgeschlossen?"
        ),
        "correct": (
            "Sie wurde beantwortet und danach zweimal hintereinander richtig geloest."
        ),
        "distractors": [
            "Sie wurde nur angesehen.",
            "Sie wurde einmal falsch beantwortet.",
            "Sie wurde uebersprungen.",
            "Sie gehoert zu einer leichten Kategorie.",
        ],
        "explanation": (
            "Wie in einer Fuehrerschein-App zaehlt echte Sicherheit: mindestens "
            "einmal beantworten und zweimal in Folge richtig loesen."
        ),
        "style": "learning_rule",
    },
]


def _build_questions() -> list[QuizQuestion]:
    """Build original questions for categories and exams."""
    questions: list[QuizQuestion] = []
    source_by_month = {
        month.month: month.source_keys for month in MACHINE_OPERATOR_CURRICULUM
    }
    goal_by_month = {
        month.month: month.learning_goals[0] for month in MACHINE_OPERATOR_CURRICULUM
    }
    for index, category in enumerate(QUESTION_CATEGORIES[:120], start=1):
        if category.month == 1:
            template = FIRST_CHAPTER_QUESTIONS[category.subchapter_number - 1]
        else:
            template = QUESTION_TEMPLATES[(index - 1) % len(QUESTION_TEMPLATES)]
        correct = template["correct"].format(goal=goal_by_month[category.month])
        options = [correct, *template["distractors"]]
        rotation = index % len(options)
        rotated_options = options[rotation:] + options[:rotation]
        correct_index = rotated_options.index(correct)
        questions.append(
            QuizQuestion(
                question_id=f"q-{index:04d}",
                category_slug=category.slug,
                prompt=template["prompt"].format(topic=category.title),
                options=rotated_options,
                correct_option_index=correct_index,
                explanation=template["explanation"].format(
                    goal=goal_by_month[category.month]
                ),
                difficulty=1 + ((index - 1) % 3),
                exam_style=template["style"],
                source_keys=source_by_month[category.month],
            )
        )
    return questions


QUESTION_BANK = _build_questions()


def _build_exams() -> list[PracticeExam]:
    """Build twenty PAL-style practice exams with ten questions each."""
    exams: list[PracticeExam] = []
    question_ids = [question.question_id for question in QUESTION_BANK]
    for exam_number in range(1, 21):
        start = (exam_number - 1) * 5
        selected = [
            question_ids[(start + offset * 3) % len(question_ids)]
            for offset in range(10)
        ]
        exams.append(
            PracticeExam(
                exam_id=f"exam-{exam_number:02d}",
                title=f"Zwischenpruefung Training {exam_number:02d}",
                description=(
                    "Zehn eigene PAL-aehnliche Single-Choice-Fragen mit "
                    "fuenf Antwortmoeglichkeiten."
                ),
                question_ids=selected,
                passing_score_percent=80,
            )
        )
    return exams


PRACTICE_EXAMS = _build_exams()
