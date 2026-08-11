"""Repository for seeded vocational curriculum data."""

from app.data.machine_operator import (
    MACHINE_OPERATOR_CURRICULUM,
    MACHINE_OPERATOR_MODULES,
    SUPPORTED_OCCUPATIONS,
)
from app.models.domain import CurriculumMonth, LearningModule, Occupation


class CurriculumRepository:
    """Read-only repository for occupation and curriculum seed data."""

    def list_occupations(self) -> list[Occupation]:
        """Return all currently supported occupations."""
        return SUPPORTED_OCCUPATIONS

    def get_curriculum(
        self,
        occupation_slug: str,
        specialization_slug: str | None = None,
    ) -> list[CurriculumMonth]:
        """Return curriculum entries for an occupation and optional specialization."""
        if occupation_slug != "maschinen-und-anlagenfuehrer":
            return []
        if specialization_slug not in (None, "metall-und-kunststofftechnik"):
            return []
        return MACHINE_OPERATOR_CURRICULUM

    def get_month(
        self,
        occupation_slug: str,
        month: int,
        specialization_slug: str | None = None,
    ) -> CurriculumMonth | None:
        """Return one curriculum month or None when it does not exist."""
        curriculum = self.get_curriculum(occupation_slug, specialization_slug)
        for entry in curriculum:
            if entry.month == month:
                return entry
        return None

    def list_learning_modules(
        self,
        occupation_slug: str,
        specialization_slug: str | None = None,
    ) -> list[LearningModule]:
        """Return module blueprints for an occupation."""
        if occupation_slug != "maschinen-und-anlagenfuehrer":
            return []
        if specialization_slug not in (None, "metall-und-kunststofftechnik"):
            return []
        return MACHINE_OPERATOR_MODULES

