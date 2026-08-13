"""Shared builder for month unit files."""

from app.data.content.helpers import theory, unit
from app.data.content.subchapters import slugify


def cat(month: int, title: str) -> list[str]:
    return [f"m{month:02d}-{slugify(title)}"]


def build_unit(
    month: int,
    position: int,
    title: str,
    subtitle: str,
    goals: list[str],
    blocks: list,
    task: str,
    glossary: dict[str, str],
    sources: list[str],
    minutes: int = 12,
):
    slug = slugify(title)
    if month >= 13:
        slug = f"m{month:02d}-{slug}"
    return unit(
        slug=slug,
        month=month,
        position=position,
        title=title,
        subtitle=subtitle,
        learning_goals=goals,
        theory_blocks=blocks,
        practice_task=task,
        glossary=glossary,
        category_slugs=cat(month, title),
        source_keys=sources,
        estimated_minutes=minutes,
    )


def tb(heading: str, body: str, points: list[str], norms: list[str] | None = None):
    return theory(heading=heading, body=body, key_points=points, norm_references=norms or [])
