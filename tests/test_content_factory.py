"""Tests for content generation and review safeguards."""

import pytest

from app.schemas.content import ContentGenerationRequest, ContentReviewRequest
from app.services.content_factory import ContentFactory
from app.services.curriculum_repository import CurriculumRepository
from app.services.source_repository import SourceRepository


def build_factory() -> ContentFactory:
    """Create a content factory for tests."""
    return ContentFactory(
        curriculum_repository=CurriculumRepository(),
        source_repository=SourceRepository(),
    )


def test_generate_draft_for_curriculum_month() -> None:
    """Generate a draft content item from a seeded curriculum month."""
    factory = build_factory()
    response = factory.generate_draft(
        ContentGenerationRequest(
            occupation_slug="maschinen-und-anlagenfuehrer",
            specialization_slug="metall-und-kunststofftechnik",
            month=8,
        )
    )

    assert response.title == "Mission 08: Pneumatik Grundlagen"
    assert "bze-uelu-maf-metall-kunststoff" in response.source_keys
    assert response.review_status == "draft"


def test_review_rejects_personal_data_in_notes() -> None:
    """Ensure obvious personal data is blocked from review notes."""
    factory = build_factory()
    draft = factory.generate_draft(
        ContentGenerationRequest(
            occupation_slug="maschinen-und-anlagenfuehrer",
            month=1,
        )
    )

    with pytest.raises(ValueError):
        factory.review_draft(
            ContentReviewRequest(
                draft_id=draft.draft_id,
                approved=False,
                reviewer_notes="Bitte sinan@example.com kontaktieren.",
            )
        )

