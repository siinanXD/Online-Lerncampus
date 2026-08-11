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


class AnswerFormat(StrEnum):
    """How an open (ungebundene) exam task must be answered."""

    SHORT_TEXT = "short_text"
    CALCULATION = "calculation"
    SKETCH = "sketch"


@dataclass(frozen=True)
class GradingCriterion:
    """One awardable point in an open task's marking scheme."""

    description: str
    points: int


@dataclass(frozen=True)
class OpenQuestion:
    """An ungebundene Aufgabe: free text, a calculation, or a sketch.

    These mirror the open part of the IHK/PAL written exam. They are not
    auto-scored; the learner self-assesses against ``criteria`` and an
    Ausbilder can override the result later.
    """

    question_id: str
    category_slug: str
    prompt: str
    answer_format: AnswerFormat
    sample_solution: str
    criteria: list[GradingCriterion]
    source_keys: list[str]

    @property
    def max_points(self) -> int:
        """Total points obtainable for this task."""
        return sum(criterion.points for criterion in self.criteria)


@dataclass(frozen=True)
class TheoryBlock:
    """One teaching step inside a learning unit."""

    heading: str
    body: str
    key_points: list[str] = field(default_factory=list)
    norm_references: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class LearningUnit:
    """A Duolingo-style learning unit on a single topic, e.g. Messschieber.

    A unit teaches one topic end to end (theory, norms, practice) and then
    hands over to its own question categories. Ten completed units unlock a
    checkpoint exam.
    """

    slug: str
    month: int
    position: int
    title: str
    subtitle: str
    learning_goals: list[str]
    theory_blocks: list[TheoryBlock]
    practice_task: str
    glossary: dict[str, str]
    category_slugs: list[str]
    source_keys: list[str]
    review_status: ReviewStatus = ReviewStatus.DRAFT
    estimated_minutes: int = 12


@dataclass(frozen=True)
class PracticeExam:
    """A generated practice exam composed from question ids.

    ``question_ids`` are single-choice (gebundene) tasks. ``open_question_ids``
    are ungebundene tasks that the learner writes or sketches.
    """

    exam_id: str
    title: str
    description: str
    question_ids: list[str]
    passing_score_percent: int
    open_question_ids: list[str] = field(default_factory=list)
    time_limit_minutes: int = 0
    points_per_choice_question: int = 1

    @property
    def is_checkpoint(self) -> bool:
        """True for full-length exams that also contain open tasks."""
        return bool(self.open_question_ids)
