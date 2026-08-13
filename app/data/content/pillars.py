"""Didactic pillars for MAF Metall- und Kunststofftechnik content.

Pillars classify curriculum months and (later) categories so content production,
quizzes, and deficit reports stay aligned with the BZE / IHK Aachen MVP scope.

A = Querschnitt & Grundlagen
B = Metalltechnik
C = Kunststofftechnik & Anlagenfuehrung
"""

from __future__ import annotations

from typing import Literal

Pillar = Literal["A", "B", "C"]

PILLAR_TITLES: dict[Pillar, str] = {
    "A": "Querschnitt und Grundlagen",
    "B": "Metalltechnik",
    "C": "Kunststofftechnik und Anlagenfuehrung",
}

# Primary pillar per curriculum month. Mixed exam months list the dominant mix
# via PRIMARY_PILLAR; EXAM_MIX marks multi-pillar sprints.
PRIMARY_PILLAR_BY_MONTH: dict[int, Pillar] = {
    1: "A",
    2: "A",
    3: "A",
    4: "A",
    5: "A",
    6: "A",
    7: "B",
    8: "C",
    9: "B",
    10: "B",
    11: "A",
    12: "A",  # ZP mix; treated as cross-cutting sprint
    13: "B",
    14: "A",
    15: "B",
    16: "A",
    17: "C",
    18: "C",
    19: "C",
    20: "C",
    21: "C",
    22: "C",
    23: "B",
    24: "A",  # AP mix; treated as cross-cutting sprint
}

EXAM_MIX_MONTHS: frozenset[int] = frozenset({12, 24})

# Months where both metal and plastics deepen together.
DUAL_METAL_PLASTICS_MONTHS: frozenset[int] = frozenset({3, 13, 15})

EXAM_LENSES = (
    "produktionstechnik",
    "produktionsplanung",
    "wiso",
    "praxis",
)


def pillar_for_month(month: int) -> Pillar:
    """Return the primary didactic pillar for a curriculum month."""
    if month not in PRIMARY_PILLAR_BY_MONTH:
        raise KeyError(f"No pillar mapping for month {month}")
    return PRIMARY_PILLAR_BY_MONTH[month]


def is_exam_mix_month(month: int) -> bool:
    """Return True for ZP/AP sprint months that mix all pillars."""
    return month in EXAM_MIX_MONTHS
