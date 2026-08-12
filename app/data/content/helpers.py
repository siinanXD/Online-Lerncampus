"""Shared builders for curriculum content seed data."""

from app.models.domain import (
    GradingCriterion,
    LearningUnit,
    OpenQuestion,
    QuizQuestion,
    ReviewStatus,
    TheoryBlock,
)


def theory(
    heading: str,
    body: str,
    key_points: list[str],
    norm_references: list[str] | None = None,
) -> TheoryBlock:
    """Build one theory block."""
    return TheoryBlock(
        heading=heading,
        body=body,
        key_points=key_points,
        norm_references=norm_references or [],
    )


def unit(
    *,
    slug: str,
    month: int,
    position: int,
    title: str,
    subtitle: str,
    learning_goals: list[str],
    theory_blocks: list[TheoryBlock],
    practice_task: str,
    glossary: dict[str, str],
    category_slugs: list[str],
    source_keys: list[str],
    estimated_minutes: int = 12,
) -> LearningUnit:
    """Build one learning unit in draft status."""
    return LearningUnit(
        slug=slug,
        month=month,
        position=position,
        title=title,
        subtitle=subtitle,
        learning_goals=learning_goals,
        theory_blocks=theory_blocks,
        practice_task=practice_task,
        glossary=glossary,
        category_slugs=category_slugs,
        source_keys=source_keys,
        review_status=ReviewStatus.DRAFT,
        estimated_minutes=estimated_minutes,
    )


def quiz(
    *,
    question_id: str,
    category_slug: str,
    prompt: str,
    correct: str,
    distractors: list[str],
    explanation: str,
    source_keys: list[str],
    difficulty: int = 2,
    exam_style: str = "single_choice",
) -> QuizQuestion:
    """Build one PAL-style question with rotated options."""
    options = [correct, *distractors[:4]]
    rotation = sum(ord(char) for char in question_id) % len(options)
    rotated = options[rotation:] + options[:rotation]
    return QuizQuestion(
        question_id=question_id,
        category_slug=category_slug,
        prompt=prompt,
        options=rotated,
        correct_option_index=rotated.index(correct),
        explanation=explanation,
        difficulty=difficulty,
        exam_style=exam_style,
        source_keys=source_keys,
    )


def open_task(
    *,
    question_id: str,
    category_slug: str,
    prompt: str,
    answer_format,
    sample_solution: str,
    criteria: list[tuple[str, int]],
    source_keys: list[str],
) -> OpenQuestion:
    """Build one open exam task with a marking scheme."""
    return OpenQuestion(
        question_id=question_id,
        category_slug=category_slug,
        prompt=prompt,
        answer_format=answer_format,
        sample_solution=sample_solution,
        criteria=[GradingCriterion(description=desc, points=pts) for desc, pts in criteria],
        source_keys=source_keys,
    )
