"""Question categories, exams, and first-chapter package for MAF."""

from app.data.content.questions import ALL_QUESTIONS
from app.data.content.subchapters import MONTH_SUBCHAPTERS, slugify
from app.data.content.units import ALL_OPEN
from app.data.machine_operator import MACHINE_OPERATOR_CURRICULUM
from app.models.domain import PracticeExam, QuestionCategory, QuizQuestion

CURRICULUM_BY_MONTH = {entry.month: entry for entry in MACHINE_OPERATOR_CURRICULUM}


def _build_categories() -> list[QuestionCategory]:
    """Build ten question categories for every curriculum month."""
    categories: list[QuestionCategory] = []
    for month in MACHINE_OPERATOR_CURRICULUM:
        for index, title in enumerate(MONTH_SUBCHAPTERS[month.month], start=1):
            categories.append(
                QuestionCategory(
                    slug=f"m{month.month:02d}-{slugify(title)}",
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
    "title": "Monat 1: Einstieg, Berufsbild und Arbeitsrecht",
    "mission_goal": (
        "Du verstehst das Berufsbild Maschinen- und Anlagenfuehrer mit Schwerpunkt "
        "Metall- und Kunststofftechnik, kennst Rechte und Pflichten in der "
        "Ausbildung und weisst, wie die Lernapp deinen Fortschritt trackt."
    ),
    "fachkunde": [
        (
            "Maschinen- und Anlagenfuehrer richten Produktionsmaschinen ein, "
            "bedienen sie, ueberwachen den Prozess und reagieren bei Stoerungen. "
            "Im Schwerpunkt Metall- und Kunststofftechnik arbeitest du mit "
            "spanenden Verfahren, Pneumatik, Werkstoffen und Qualitaetspruefung."
        ),
        (
            "Die Ausbildung dauert 24 Monate. Der Ausbildungsvertrag regelt "
            "Verguetung, Urlaub, Probezeit und Kuendigung. Das Berichtsheft "
            "dokumentiert taeglich deine Taetigkeiten und wird regelmaessig "
            "vom Ausbilder gegengezeichnet."
        ),
        (
            "Die Zwischenpruefung findet zu Beginn des zweiten Ausbildungsjahres "
            "statt, die Abschlusspruefung am Ende. In dieser App gilt: Jede Frage "
            "muss mindestens einmal beantwortet und zweimal hintereinander richtig "
            "geloest werden, bevor sie als gemeistert gilt."
        ),
    ],
    "category_slugs": [
        f"m01-{slugify(title)}" for title in MONTH_SUBCHAPTERS[1]
    ],
    "checkpoint_exam_id": "exam-01",
}

QUESTION_BANK: list[QuizQuestion] = ALL_QUESTIONS


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


CHECKPOINT_CHOICE_QUESTIONS = 50
CHECKPOINT_OPEN_QUESTIONS = 15
CHECKPOINT_TIME_LIMIT_MINUTES = 120
UNITS_PER_CHECKPOINT = 10
MAX_CURRICULUM_MONTH = 24


def _open_ids_for_month(month: int, open_ids: list[str]) -> list[str]:
    """Return authored open-task ids for one curriculum month."""
    prefix = f"open-m{month:02d}-"
    return [question_id for question_id in open_ids if question_id.startswith(prefix)]


def _open_ids_for_checkpoint(number: int, open_ids: list[str]) -> list[str]:
    """Prefer the checkpoint month, then neighbours, so year-2 exams stay in year 2."""
    selected: list[str] = []
    seen: set[str] = set()
    for offset in (0, -1, 1, -2, 2, -3, 3):
        month = number + offset
        if month < 1 or month > MAX_CURRICULUM_MONTH:
            continue
        for question_id in _open_ids_for_month(month, open_ids):
            if question_id in seen:
                continue
            selected.append(question_id)
            seen.add(question_id)
            if len(selected) >= CHECKPOINT_OPEN_QUESTIONS:
                return selected
    for question_id in open_ids:
        if question_id in seen:
            continue
        selected.append(question_id)
        seen.add(question_id)
        if len(selected) >= CHECKPOINT_OPEN_QUESTIONS:
            break
    return selected[:CHECKPOINT_OPEN_QUESTIONS]


def _build_checkpoint_exams() -> list[PracticeExam]:
    """Build full-length checkpoint exams in the format of the written IHK exam."""
    question_ids = [question.question_id for question in QUESTION_BANK]
    open_ids = [question.question_id for question in ALL_OPEN]
    if not open_ids:
        return []

    exams: list[PracticeExam] = []
    checkpoint_count = max(1, len(QUESTION_CATEGORIES) // UNITS_PER_CHECKPOINT)
    for number in range(1, checkpoint_count + 1):
        start = (number - 1) * CHECKPOINT_CHOICE_QUESTIONS
        selected = [
            question_ids[(start + offset) % len(question_ids)]
            for offset in range(CHECKPOINT_CHOICE_QUESTIONS)
        ]
        selected_open = _open_ids_for_checkpoint(number, open_ids)
        month = min(number, len(MACHINE_OPERATOR_CURRICULUM))
        month_title = CURRICULUM_BY_MONTH[month].title
        exams.append(
            PracticeExam(
                exam_id=f"checkpoint-{number:02d}",
                title=f"Checkpoint {number:02d}: {month_title}",
                description=(
                    "Volle Pruefungssimulation: 50 gebundene Single-Choice-Aufgaben "
                    "und 15 ungebundene Aufgaben (Text, Rechnung, Skizze)."
                ),
                question_ids=selected,
                open_question_ids=selected_open,
                passing_score_percent=60,
                time_limit_minutes=CHECKPOINT_TIME_LIMIT_MINUTES,
            )
        )
    return exams


PRACTICE_EXAMS = _build_exams() + _build_checkpoint_exams()
