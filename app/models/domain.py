"""Domain models for curriculum, source, and content review data."""

from dataclasses import dataclass, field
from enum import StrEnum


class ReviewStatus(StrEnum):
    """Possible lifecycle states for generated learning content."""

    DRAFT = "draft"
    SOURCE_CHECKED = "source_checked"
    NEEDS_REVISION = "needs_revision"
    APPROVED = "approved"


@dataclass(frozen=True)
class Occupation:
    """A supported vocational occupation."""

    slug: str
    title: str
    duration_months: int
    specializations: list[str]


@dataclass(frozen=True)
class CurriculumMonth:
    """One month in a vocational curriculum roadmap."""

    month: int
    year: int
    title: str
    focus_area: str
    learning_goals: list[str]
    source_keys: list[str]
    is_exam_preparation: bool = False


@dataclass(frozen=True)
class LearningModule:
    """A generated module blueprint derived from a curriculum month."""

    slug: str
    month: int
    title: str
    mission_type: str
    lesson_goal: str
    quiz_focus: str
    required_review: bool = True


@dataclass(frozen=True)
class SourceDocument:
    """Trusted source metadata for generation and fact checking."""

    key: str
    title: str
    publisher: str
    url: str
    trust_tier: int
    allowed_usage: str
    topics: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class GeneratedContent:
    """Draft or reviewed learning content."""

    draft_id: str
    title: str
    learning_goal: str
    fachkunde: str
    practice_task: str
    quiz_question: str
    quiz_options: list[str]
    correct_option: str
    explanation: str
    source_keys: list[str]
    review_status: ReviewStatus
    review_notes: list[str]


@dataclass(frozen=True)
class QuestionCategory:
    """A question category mapped to one curriculum subchapter."""

    slug: str
    month: int
    chapter_title: str
    subchapter_number: int
    title: str
    description: str


@dataclass(frozen=True)
class QuizQuestion:
    """A PAL-style single-choice practice question."""

    question_id: str
    category_slug: str
    prompt: str
    options: list[str]
    correct_option_index: int
    explanation: str
    difficulty: int
    exam_style: str
    source_keys: list[str]


@dataclass(frozen=True)
class PracticeExam:
    """A generated practice exam composed from question ids."""

    exam_id: str
    title: str
    description: str
    question_ids: list[str]
    passing_score_percent: int
