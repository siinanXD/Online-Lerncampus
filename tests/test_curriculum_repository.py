"""Tests for the seeded curriculum repository."""

from app.services.curriculum_repository import CurriculumRepository


def test_machine_operator_curriculum_has_24_months() -> None:
    """Ensure the first occupation covers the full two-year training duration."""
    repository = CurriculumRepository()
    curriculum = repository.get_curriculum("maschinen-und-anlagenfuehrer")

    assert len(curriculum) == 24
    assert curriculum[0].month == 1
    assert curriculum[-1].month == 24


def test_exam_preparation_months_are_marked() -> None:
    """Ensure exam preparation months are explicitly flagged."""
    repository = CurriculumRepository()
    curriculum = repository.get_curriculum("maschinen-und-anlagenfuehrer")
    exam_months = [entry.month for entry in curriculum if entry.is_exam_preparation]

    assert exam_months == [12, 24]

