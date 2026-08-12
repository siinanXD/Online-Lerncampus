"""Authoring bundle abstraction for Python and JSON seed sources."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any

from app.data.content.questions import ALL_QUESTIONS
from app.data.content.subchapters import MONTH_SUBCHAPTERS
from app.data.learning_units import LEARNING_UNITS, OPEN_QUESTIONS
from app.data.machine_operator import (
    MACHINE_OPERATOR_CURRICULUM,
    MACHINE_OPERATOR_MODULES,
    SUPPORTED_OCCUPATIONS,
)
from app.data.question_bank import FIRST_CHAPTER, PRACTICE_EXAMS, QUESTION_CATEGORIES
from app.data.sources import TRUSTED_SOURCES
from app.models.domain import (
    AnswerFormat,
    CurriculumMonth,
    GradingCriterion,
    LearningModule,
    LearningUnit,
    Occupation,
    OpenQuestion,
    PracticeExam,
    QuestionCategory,
    QuizQuestion,
    ReviewStatus,
    SourceDocument,
    TheoryBlock,
)


@dataclass(frozen=True)
class ContentBundle:
    """Portable MAF content bundle independent of import format."""

    occupations: tuple[Any, ...]
    curriculum: tuple[Any, ...]
    modules: tuple[LearningModule, ...]
    sources: tuple[SourceDocument, ...]
    categories: tuple[QuestionCategory, ...]
    questions: tuple[QuizQuestion, ...]
    units: tuple[LearningUnit, ...]
    open_questions: tuple[OpenQuestion, ...]
    exams: tuple[PracticeExam, ...]
    first_chapter: dict[str, Any]
    month_subchapters: dict[int, tuple[str, ...]]


def load_python_bundle() -> ContentBundle:
    """Build a bundle from the in-repo Python seed modules."""
    return ContentBundle(
        occupations=tuple(SUPPORTED_OCCUPATIONS),
        curriculum=tuple(MACHINE_OPERATOR_CURRICULUM),
        modules=tuple(MACHINE_OPERATOR_MODULES),
        sources=tuple(TRUSTED_SOURCES),
        categories=tuple(QUESTION_CATEGORIES),
        questions=tuple(ALL_QUESTIONS),
        units=tuple(LEARNING_UNITS),
        open_questions=tuple(OPEN_QUESTIONS),
        exams=tuple(PRACTICE_EXAMS),
        first_chapter=dict(FIRST_CHAPTER),
        month_subchapters={
            month: tuple(titles) for month, titles in MONTH_SUBCHAPTERS.items()
        },
    )


def _serialize_value(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, tuple):
        return [_serialize_value(item) for item in value]
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _serialize_value(item) for key, item in value.items()}
    if hasattr(value, "__dataclass_fields__"):
        return _serialize_value(asdict(value))
    return value


def bundle_to_json(bundle: ContentBundle) -> dict[str, Any]:
    """Convert one bundle into JSON-serializable data."""
    return _serialize_value(bundle)


def _hydrate_theory_block(data: dict[str, Any]) -> TheoryBlock:
    return TheoryBlock(
        heading=data["heading"],
        body=data["body"],
        key_points=list(data["key_points"]),
        norm_references=list(data.get("norm_references") or []),
    )


def _hydrate_unit(data: dict[str, Any]) -> LearningUnit:
    return LearningUnit(
        slug=data["slug"],
        month=data["month"],
        position=data["position"],
        title=data["title"],
        subtitle=data["subtitle"],
        learning_goals=list(data["learning_goals"]),
        theory_blocks=[_hydrate_theory_block(item) for item in data["theory_blocks"]],
        practice_task=data["practice_task"],
        glossary=dict(data["glossary"]),
        category_slugs=list(data["category_slugs"]),
        source_keys=list(data["source_keys"]),
        review_status=ReviewStatus(data["review_status"]),
        estimated_minutes=data["estimated_minutes"],
    )


def _hydrate_question(data: dict[str, Any]) -> QuizQuestion:
    return QuizQuestion(
        question_id=data["question_id"],
        category_slug=data["category_slug"],
        prompt=data["prompt"],
        options=list(data["options"]),
        correct_option_index=data["correct_option_index"],
        explanation=data["explanation"],
        difficulty=data["difficulty"],
        exam_style=data["exam_style"],
        source_keys=list(data["source_keys"]),
    )


def _hydrate_open_question(data: dict[str, Any]) -> OpenQuestion:
    return OpenQuestion(
        question_id=data["question_id"],
        category_slug=data["category_slug"],
        prompt=data["prompt"],
        answer_format=AnswerFormat(data["answer_format"]),
        criteria=[
            GradingCriterion(description=item["description"], points=item["points"])
            for item in data["criteria"]
        ],
        sample_solution=data["sample_solution"],
        source_keys=list(data["source_keys"]),
    )


def _hydrate_exam(data: dict[str, Any]) -> PracticeExam:
    return PracticeExam(
        exam_id=data["exam_id"],
        title=data["title"],
        description=data["description"],
        question_ids=list(data["question_ids"]),
        open_question_ids=list(data.get("open_question_ids") or []),
        passing_score_percent=data["passing_score_percent"],
        time_limit_minutes=data.get("time_limit_minutes") or 0,
    )


def load_json_bundle(bundle_path: Path) -> ContentBundle:
    """Load one exported JSON bundle from disk."""
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    return ContentBundle(
        occupations=tuple(
            Occupation(**occupation) if isinstance(occupation, dict) else occupation
            for occupation in payload["occupations"]
        ),
        curriculum=tuple(
            CurriculumMonth(**entry) if isinstance(entry, dict) else entry
            for entry in payload["curriculum"]
        ),
        modules=tuple(
            LearningModule(**module) for module in payload["modules"]
        ),
        sources=tuple(
            SourceDocument(**source) for source in payload["sources"]
        ),
        categories=tuple(
            QuestionCategory(**category) for category in payload["categories"]
        ),
        questions=tuple(_hydrate_question(item) for item in payload["questions"]),
        units=tuple(_hydrate_unit(item) for item in payload["units"]),
        open_questions=tuple(
            _hydrate_open_question(item) for item in payload["open_questions"]
        ),
        exams=tuple(_hydrate_exam(item) for item in payload["exams"]),
        first_chapter=dict(payload["first_chapter"]),
        month_subchapters={
            int(month): tuple(titles)
            for month, titles in payload["month_subchapters"].items()
        },
    )


def default_json_bundle_path() -> Path:
    """Return the default JSON bundle path for MAF v1."""
    return Path(__file__).resolve().parents[1] / "content" / "maf" / "v1" / "bundle.json"
