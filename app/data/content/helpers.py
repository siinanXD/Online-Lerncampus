"""Shared builders for curriculum content seed data."""

import re

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


def _quoted_title_pattern(title: str) -> str:
    """Return a regex-safe quoted title pattern."""
    return rf"['\"]{re.escape(title.strip())}['\"]"


def humanize_question_prompt(prompt: str, category_title: str | None = None) -> str:
    """Remove redundant category titles from templated JSONL prompts."""
    if not prompt or not category_title:
        return prompt
    title = category_title.strip()
    if not title:
        return prompt

    quoted = _quoted_title_pattern(title)
    result = prompt

    result = re.sub(
        rf"\s+(?:zu|für|zum Thema|im Thema)\s+{quoted}\s*\?",
        "?",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        rf"^Bei\s+{quoted}\s+",
        "",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(rf"\s+{quoted}", "", result, flags=re.IGNORECASE)
    result = re.sub(r"\s+\?", "?", result)
    result = re.sub(r"\?\?+", "?", result)

    if result and result[0].islower():
        result = result[0].upper() + result[1:]
    return result.strip()


def humanize_question_options(
    options: list[str],
    category_title: str | None = None,
) -> list[str]:
    """Remove redundant category titles from templated answer options."""
    if not category_title:
        return list(options)
    title = category_title.strip()
    if not title:
        return list(options)

    quoted = _quoted_title_pattern(title)
    cleaned: list[str] = []
    for option in options:
        text = re.sub(
            rf"^(?:Zum Thema|Im Thema|Für das Thema|Beim Thema)\s+{quoted}\s+",
            "",
            option,
            flags=re.IGNORECASE,
        )
        text = re.sub(rf"\s+{quoted}\s+", " ", text, flags=re.IGNORECASE)
        text = text.strip()
        if text and text[0].islower():
            text = text[0].upper() + text[1:]
        cleaned.append(text)
    return cleaned


def rotate_question_options(question: QuizQuestion) -> QuizQuestion:
    """Shift options so the correct answer is not always the first choice."""
    options = list(question.options)
    count = len(options)
    if count < 2:
        return question
    correct = options[question.correct_option_index]
    shift = 1 + (sum(ord(char) for char in question.question_id) % (count - 1))
    rotated = options[shift:] + options[:shift]
    return QuizQuestion(
        question_id=question.question_id,
        category_slug=question.category_slug,
        prompt=question.prompt,
        options=rotated,
        correct_option_index=rotated.index(correct),
        explanation=question.explanation,
        difficulty=question.difficulty,
        exam_style=question.exam_style,
        source_keys=list(question.source_keys),
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
