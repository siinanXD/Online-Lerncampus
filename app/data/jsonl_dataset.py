"""Load the BZE MAF JSONL/ZIP content dataset into a ContentBundle."""

from __future__ import annotations

import json
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Any

from app.data.content.subchapters import slugify
from app.data.content_bundle import ContentBundle
from app.data.machine_operator import SUPPORTED_OCCUPATIONS
from app.models.domain import (
    AnswerFormat,
    CurriculumMonth,
    GradingCriterion,
    LearningModule,
    LearningUnit,
    OpenQuestion,
    PracticeExam,
    QuestionCategory,
    QuizQuestion,
    ReviewStatus,
    SourceDocument,
    TheoryBlock,
)

JSONL_TABLES = (
    "sources",
    "competencies",
    "worlds",
    "modules",
    "chapters",
    "lessons",
    "learning_objectives",
    "content_blocks",
    "flashcards",
    "questions",
    "interactive_tasks",
    "practical_scenarios",
    "assessments",
    "spaced_repetition",
    "mappings",
)

_BLOCK_LABELS = {
    "fachkunde": "Fachkunde",
    "beispiel_formel": "Beispiel und Formel",
    "merksatz_pruefung": "Merksatz fuer die Pruefung",
}

_TRUST_TIER_BY_TYPE = {
    "official_regulation": 1,
    "official_curriculum": 1,
    "official_exam_information": 1,
    "official_exam_structure": 1,
    "official_exam_template": 1,
    "official_safety_reference": 1,
}


def load_jsonl_dataset(source: Path) -> ContentBundle:
    """Convert a JSONL directory or ZIP into the application content bundle."""
    tables = _read_tables(source)
    modules = tables["modules"]
    chapters = tables["chapters"]
    lessons = tables["lessons"]
    objectives = tables["learning_objectives"]
    blocks = tables["content_blocks"]
    flashcards = tables["flashcards"]
    questions = tables["questions"]
    interactive_tasks = tables["interactive_tasks"]
    scenarios = tables["practical_scenarios"]
    assessments = tables["assessments"]

    modules_by_id = {item["id"]: item for item in modules}
    chapters_by_id = {item["id"]: item for item in chapters}
    lessons_by_id = {item["id"]: item for item in lessons}
    chapter_position = _positions_by_month(chapters)
    lesson_position = _lesson_positions(lessons, chapters_by_id)

    objectives_by_id = {item["id"]: item for item in objectives}
    blocks_by_lesson: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for block in blocks:
        blocks_by_lesson[block["lesson_id"]].append(block)
    flashcards_by_lesson: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for card in flashcards:
        flashcards_by_lesson[card["lesson_id"]].append(card)
    interactive_by_lesson = {item["lesson_id"]: item for item in interactive_tasks}
    scenario_by_module = {item["module_id"]: item for item in scenarios}

    sources = tuple(_hydrate_source(item) for item in tables["sources"])
    curriculum = tuple(_hydrate_curriculum(item, lessons, objectives_by_id) for item in modules)
    learning_modules = tuple(_hydrate_module(item) for item in modules)
    categories = tuple(
        _hydrate_category(item, modules_by_id, chapter_position[item["id"]])
        for item in chapters
    )
    category_slug_by_chapter = {
        item["id"]: _stable_slug(item["id"]) for item in chapters
    }

    units = tuple(
        _hydrate_unit(
            lesson,
            chapters_by_id=chapters_by_id,
            modules_by_id=modules_by_id,
            position=lesson_position[lesson["id"]],
            category_slug=category_slug_by_chapter[lesson["chapter_id"]],
            objectives_by_id=objectives_by_id,
            blocks=sorted(blocks_by_lesson.get(lesson["id"], []), key=lambda item: item["id"]),
            flashcards=flashcards_by_lesson.get(lesson["id"], []),
            interactive=interactive_by_lesson.get(lesson["id"]),
            scenario=scenario_by_module.get(lesson["module_id"])
            if _is_last_lesson_in_module(lesson, lessons)
            else None,
        )
        for lesson in lessons
    )

    quiz_questions: list[QuizQuestion] = []
    open_questions: list[OpenQuestion] = []
    for question in questions:
        lesson = lessons_by_id[question["lesson_id"]]
        category_slug = category_slug_by_chapter[lesson["chapter_id"]]
        if _is_single_correct_quiz(question):
            quiz_questions.append(_hydrate_quiz_question(question, category_slug))
        else:
            open_questions.append(_hydrate_open_question(question, category_slug))

    quiz_ids = {item.question_id for item in quiz_questions}
    open_ids = {item.question_id for item in open_questions}
    exams = tuple(
        _hydrate_exam(item, quiz_ids, open_ids) for item in assessments
    )

    month_subchapters = {
        month: tuple(
            item["title"]
            for item in sorted(
                (chapter for chapter in chapters if chapter["month"] == month),
                key=lambda chapter: chapter["week"],
            )
        )
        for month in sorted({item["month"] for item in chapters})
    }
    first_chapter = _build_first_chapter(
        modules,
        chapters,
        lessons,
        blocks,
        exams,
        category_slug_by_chapter,
    )
    return ContentBundle(
        occupations=tuple(SUPPORTED_OCCUPATIONS),
        curriculum=curriculum,
        modules=learning_modules,
        sources=sources,
        categories=categories,
        questions=tuple(quiz_questions),
        units=units,
        open_questions=tuple(open_questions),
        exams=exams,
        first_chapter=first_chapter,
        month_subchapters=month_subchapters,
    )


def _read_tables(source: Path) -> dict[str, list[dict[str, Any]]]:
    source = source.expanduser().resolve()
    if source.is_dir():
        return {
            name: _parse_jsonl_text((source / f"{name}.jsonl").read_text(encoding="utf-8"))
            if (source / f"{name}.jsonl").exists()
            else []
            for name in JSONL_TABLES
        }
    if source.is_file() and source.suffix.lower() == ".zip":
        with zipfile.ZipFile(source) as archive:
            names = {Path(item).name: item for item in archive.namelist()}
            return {
                name: _parse_jsonl_text(archive.read(names[f"{name}.jsonl"]).decode("utf-8"))
                if f"{name}.jsonl" in names
                else []
                for name in JSONL_TABLES
            }
    raise FileNotFoundError(f"JSONL dataset not found: {source}")


def _parse_jsonl_text(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            records.append(json.loads(stripped))
    return records


def _stable_slug(value: str) -> str:
    return slugify(value.replace("_", "-"))


def _positions_by_month(chapters: list[dict[str, Any]]) -> dict[str, int]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for chapter in chapters:
        grouped[int(chapter["month"])].append(chapter)
    positions: dict[str, int] = {}
    for month_chapters in grouped.values():
        ordered = sorted(month_chapters, key=lambda item: (item["week"], item["id"]))
        for index, chapter in enumerate(ordered, start=1):
            positions[chapter["id"]] = index
    return positions


def _lesson_positions(
    lessons: list[dict[str, Any]],
    chapters_by_id: dict[str, dict[str, Any]],
) -> dict[str, int]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for lesson in lessons:
        month = int(chapters_by_id[lesson["chapter_id"]]["month"])
        grouped[month].append(lesson)
    positions: dict[str, int] = {}
    for month_lessons in grouped.values():
        ordered = sorted(month_lessons, key=lambda item: item["sequence"])
        for index, lesson in enumerate(ordered, start=1):
            positions[lesson["id"]] = index
    return positions


def _is_last_lesson_in_module(lesson: dict[str, Any], lessons: list[dict[str, Any]]) -> bool:
    module_lessons = [item for item in lessons if item["module_id"] == lesson["module_id"]]
    last = max(module_lessons, key=lambda item: item["sequence"])
    return last["id"] == lesson["id"]


def _hydrate_source(item: dict[str, Any]) -> SourceDocument:
    topics = [part.strip() for part in str(item.get("scope") or "").split(",") if part.strip()]
    return SourceDocument(
        key=item["id"],
        title=item["title"],
        publisher=item["publisher"],
        url=item.get("url") or "",
        trust_tier=_TRUST_TIER_BY_TYPE.get(item.get("type"), 1),
        allowed_usage=item.get("usage_note") or "Citation and curriculum alignment.",
        topics=topics,
    )


def _hydrate_curriculum(
    module: dict[str, Any],
    lessons: list[dict[str, Any]],
    objectives_by_id: dict[str, dict[str, Any]],
) -> CurriculumMonth:
    month = int(module["month"])
    goals: list[str] = []
    for lesson in lessons:
        if lesson["module_id"] != module["id"]:
            continue
        for objective_id in lesson.get("learning_objective_ids") or []:
            objective = objectives_by_id.get(objective_id)
            if objective and objective["title"] not in goals:
                goals.append(objective["title"])
    if not goals:
        goals = [module["focus"]]
    exam_orientation = str(module.get("exam_orientation") or "")
    return CurriculumMonth(
        month=month,
        year=1 if month <= 12 else 2,
        title=module["title"],
        focus_area=module.get("focus") or exam_orientation,
        learning_goals=goals[:4],
        source_keys=list(module.get("source_ids") or []),
        is_exam_preparation=month in {12, 23, 24} or "exam" in exam_orientation,
    )


def _hydrate_module(module: dict[str, Any]) -> LearningModule:
    return LearningModule(
        slug=_stable_slug(module["id"]),
        month=int(module["month"]),
        title=module["title"],
        mission_type=module.get("exam_orientation") or "learning_mission",
        lesson_goal=module.get("focus") or module["title"],
        quiz_focus=module.get("exam_orientation") or module["title"],
    )


def _hydrate_category(
    chapter: dict[str, Any],
    modules_by_id: dict[str, dict[str, Any]],
    position: int,
) -> QuestionCategory:
    module = modules_by_id[chapter["module_id"]]
    return QuestionCategory(
        slug=_stable_slug(chapter["id"]),
        month=int(chapter["month"]),
        chapter_title=module["title"],
        subchapter_number=position,
        title=chapter["title"],
        description=(
            f"{module['title']}: {chapter['title']} "
            f"({chapter.get('exam_area') or 'pruefungsnah'})."
        ),
    )


def _hydrate_unit(
    lesson: dict[str, Any],
    *,
    chapters_by_id: dict[str, dict[str, Any]],
    modules_by_id: dict[str, dict[str, Any]],
    position: int,
    category_slug: str,
    objectives_by_id: dict[str, dict[str, Any]],
    blocks: list[dict[str, Any]],
    flashcards: list[dict[str, Any]],
    interactive: dict[str, Any] | None,
    scenario: dict[str, Any] | None,
) -> LearningUnit:
    chapter = chapters_by_id[lesson["chapter_id"]]
    module = modules_by_id[lesson["module_id"]]
    goals = [
        objectives_by_id[item]["title"]
        for item in lesson.get("learning_objective_ids") or []
        if item in objectives_by_id
    ]
    if not goals:
        goals = [lesson["title"]]
    theory_blocks = [
        TheoryBlock(
            heading=block.get("title") or _BLOCK_LABELS.get(block.get("type"), "Lerninhalt"),
            body=block["body"],
            key_points=[_BLOCK_LABELS.get(block.get("type"), str(block.get("type") or "Lerninhalt"))],
            norm_references=[],
        )
        for block in blocks
    ]
    if not theory_blocks:
        theory_blocks = [
            TheoryBlock(
                heading=lesson["title"],
                body=lesson.get("summary") or lesson["title"],
                key_points=[],
            )
        ]
    glossary: dict[str, str] = {}
    for card in flashcards:
        term = str(card["front"]).strip()
        if not term:
            continue
        original = term
        suffix = 2
        while term in glossary:
            term = f"{original} ({suffix})"
            suffix += 1
        glossary[term] = str(card["back"]).strip()
    practice_parts = []
    if interactive:
        practice_parts.append(str(interactive.get("prompt") or interactive.get("title") or "").strip())
    if scenario:
        brief = str(scenario.get("brief") or "").strip()
        title = str(scenario.get("title") or "").strip()
        practice_parts.append(" ".join(part for part in (title, brief) if part))
    return LearningUnit(
        slug=_stable_slug(lesson["id"]),
        month=int(chapter["month"]),
        position=position,
        title=lesson["title"],
        subtitle=lesson.get("summary") or module["title"],
        learning_goals=goals,
        theory_blocks=theory_blocks,
        practice_task=" ".join(part for part in practice_parts if part) or lesson.get("summary") or "",
        glossary=glossary,
        category_slugs=[category_slug],
        source_keys=list(lesson.get("source_ids") or []),
        review_status=ReviewStatus.APPROVED,
        estimated_minutes=int(lesson.get("estimated_minutes") or 12),
    )


def _is_single_correct_quiz(question: dict[str, Any]) -> bool:
    options = question.get("options") or []
    if not options:
        return False
    option_ids = {item["id"] for item in options}
    answer = question.get("correct_answer")
    if isinstance(answer, str):
        return answer in option_ids
    if isinstance(answer, list) and len(answer) == 1:
        return answer[0] in option_ids
    return False


def _clamp_difficulty(value: Any) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 2
    if number <= 2:
        return 1
    if number == 3:
        return 2
    return 3


def _hydrate_quiz_question(question: dict[str, Any], category_slug: str) -> QuizQuestion:
    options = list(question["options"])
    option_texts = [item["text"] for item in options]
    answer = question["correct_answer"]
    correct_id = answer[0] if isinstance(answer, list) else answer
    correct_index = next(
        index for index, item in enumerate(options) if item["id"] == correct_id
    )
    return QuizQuestion(
        question_id=question["id"],
        category_slug=category_slug,
        prompt=question["prompt"],
        options=option_texts,
        correct_option_index=correct_index,
        explanation=question.get("explanation") or "",
        difficulty=_clamp_difficulty(question.get("difficulty")),
        exam_style=str(question.get("type") or "single_choice"),
        source_keys=list(question.get("source_ids") or []),
    )


def _format_answer(answer: Any, question: dict[str, Any]) -> str:
    if isinstance(answer, dict):
        if {"value", "unit"} <= set(answer):
            tolerance = answer.get("tolerance")
            suffix = f" (+/- {tolerance})" if tolerance is not None else ""
            return f"{answer['value']} {answer['unit']}{suffix}"
        return "\n".join(f"{key}: {value}" for key, value in answer.items())
    if isinstance(answer, list):
        option_map = {
            item["id"]: item["text"] for item in question.get("options") or []
        }
        rendered = [option_map.get(item, str(item)) for item in answer]
        return "\n".join(f"{index}. {item}" for index, item in enumerate(rendered, start=1))
    return str(answer)


def _hydrate_open_question(question: dict[str, Any], category_slug: str) -> OpenQuestion:
    question_type = str(question.get("type") or "short_text")
    if question_type in {"calculation", "formula_rearrange"}:
        answer_format = AnswerFormat.CALCULATION
    elif question_type in {"drawing_interpretation"}:
        answer_format = AnswerFormat.SKETCH
    else:
        answer_format = AnswerFormat.SHORT_TEXT
    answer = question.get("correct_answer")
    sample = _format_answer(answer, question)
    if question.get("explanation"):
        sample = f"{sample}\n\n{question['explanation']}".strip()
    criteria = _criteria_for(question_type, answer)
    return OpenQuestion(
        question_id=question["id"],
        category_slug=category_slug,
        prompt=question["prompt"],
        answer_format=answer_format,
        sample_solution=sample,
        criteria=criteria,
        source_keys=list(question.get("source_ids") or []),
    )


def _criteria_for(question_type: str, answer: Any) -> list[GradingCriterion]:
    if question_type == "calculation":
        return [
            GradingCriterion(description="Zahlenwert innerhalb der Toleranz", points=2),
            GradingCriterion(description="Einheit korrekt angegeben", points=1),
        ]
    if question_type == "matching" and isinstance(answer, dict):
        return [
            GradingCriterion(description=f"Zuordnung: {key}", points=1)
            for key in answer
        ] or [GradingCriterion(description="Zuordnung vollstaendig", points=1)]
    if question_type == "sequence" and isinstance(answer, list):
        return [
            GradingCriterion(description="Reihenfolge fachlich korrekt", points=len(answer) or 1)
        ]
    if question_type == "multiple_choice" and isinstance(answer, list):
        return [
            GradingCriterion(description="Alle zutreffenden Aussagen erkannt", points=len(answer) or 1)
        ]
    return [GradingCriterion(description="Musterloesung fachlich nachvollziehbar", points=1)]


def _hydrate_exam(
    assessment: dict[str, Any],
    quiz_ids: set[str],
    open_ids: set[str],
) -> PracticeExam:
    question_ids = [
        item for item in assessment.get("question_ids") or [] if item in quiz_ids
    ]
    open_question_ids = [
        item for item in assessment.get("question_ids") or [] if item in open_ids
    ]
    window = assessment.get("week_window") or {}
    start = window.get("start")
    end = window.get("end")
    window_text = f" Woche {start}-{end}." if start and end else ""
    grading = assessment.get("grading") or {}
    passing = int(grading.get("pass_threshold_percent") or 67)
    return PracticeExam(
        exam_id=assessment["id"],
        title=assessment["title"],
        description=f"{assessment.get('type') or 'assessment'}.{window_text}".strip(),
        question_ids=question_ids,
        passing_score_percent=passing,
        open_question_ids=open_question_ids,
        time_limit_minutes=int(assessment.get("duration_minutes") or 0),
    )


def _build_first_chapter(
    modules: list[dict[str, Any]],
    chapters: list[dict[str, Any]],
    lessons: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
    exams: tuple[PracticeExam, ...],
    category_slug_by_chapter: dict[str, str],
) -> dict[str, Any]:
    month_one_modules = [item for item in modules if int(item["month"]) == 1]
    month_one_chapters = sorted(
        (item for item in chapters if int(item["month"]) == 1),
        key=lambda item: item["week"],
    )
    month_one_lessons = {
        item["id"]
        for item in lessons
        if item["chapter_id"] in {chapter["id"] for chapter in month_one_chapters}
    }
    fachkunde = [
        item["body"]
        for item in blocks
        if item.get("type") == "fachkunde" and item.get("lesson_id") in month_one_lessons
    ][:3]
    title = month_one_modules[0]["title"] if month_one_modules else "Monat 1"
    mission_goal = month_one_modules[0].get("focus") if month_one_modules else title
    checkpoint = exams[0].exam_id if exams else ""
    return {
        "title": f"Monat 1: {title}",
        "mission_goal": mission_goal or title,
        "fachkunde": fachkunde,
        "category_slugs": [
            category_slug_by_chapter[item["id"]] for item in month_one_chapters
        ],
        "checkpoint_exam_id": checkpoint,
    }
