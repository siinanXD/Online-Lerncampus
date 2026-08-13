"""Curriculum content for Maschinen- und Anlagenfuehrer Metall/Kunststoff."""

from app.data.content.aggregate import ALL_LEARNING_UNITS, ALL_OPEN_QUESTIONS, ALL_QUESTIONS
from app.data.content.pillars import PRIMARY_PILLAR_BY_MONTH, pillar_for_month
from app.data.content.subchapters import MONTH_SUBCHAPTERS, slugify

__all__ = [
    "ALL_LEARNING_UNITS",
    "ALL_OPEN_QUESTIONS",
    "ALL_QUESTIONS",
    "MONTH_SUBCHAPTERS",
    "PRIMARY_PILLAR_BY_MONTH",
    "pillar_for_month",
    "slugify",
]
