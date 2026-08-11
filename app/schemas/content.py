"""Pydantic schemas for learning content API payloads."""

from pydantic import BaseModel, Field, HttpUrl

from app.models.domain import ReviewStatus


class HealthResponse(BaseModel):
    """Response schema for service health."""

    status: str


class LoginRequest(BaseModel):
    """Request schema for pseudonymous login."""

    identifier: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=4, max_length=120)
    cohort_code: str | None = Field(default=None, max_length=40)


class LoginResponse(BaseModel):
    """Response schema for pseudonymous login."""

    access_token: str
    token_type: str = "bearer"
    learner_id: str
    display_name: str
    cohort_code: str | None
    role: str


class CurrentLearnerResponse(BaseModel):
    """Response schema for the authenticated learner profile."""

    learner_id: str
    display_name: str
    cohort_code: str | None
    role: str


class LogoutResponse(BaseModel):
    """Response schema for session logout."""

    success: bool


class ConsentRequest(BaseModel):
    """Request schema for privacy notice acknowledgement."""

    accepted: bool
    consent_version: str | None = Field(default=None, max_length=80)


class ConsentResponse(BaseModel):
    """Response schema for stored privacy notice acknowledgement."""

    accepted: bool
    consent_version: str


class DataExportResponse(BaseModel):
    """Response schema for learner data export."""

    export_version: str = "1.0"
    data: dict[str, object]


class DeleteAccountResponse(BaseModel):
    """Response schema for learner account deletion."""

    deleted: bool


class PasswordChangeRequest(BaseModel):
    """Request schema for password change validation."""

    current_password: str = Field(min_length=1, max_length=120)
    new_password: str = Field(min_length=8, max_length=120)
    repeated_password: str = Field(min_length=8, max_length=120)


class PasswordChangeResponse(BaseModel):
    """Response schema for password change validation."""

    accepted: bool
    checklist: dict[str, bool]


class ProgressAttemptRequest(BaseModel):
    """Request schema for recording a question attempt."""

    question_id: str = Field(min_length=3, max_length=40)
    selected_option_index: int = Field(ge=0, le=10)


class QuestionProgressResponse(BaseModel):
    """Serializable question progress state."""

    question_id: str
    answered_count: int
    wrong_count: int
    correct_streak: int
    mastered: bool
    selected_option_index: int
    correct_option_index: int
    is_correct: bool
    explanation: str


class DashboardSummaryResponse(BaseModel):
    """Serializable learner dashboard metrics."""

    learner_id: str
    answered_questions: int
    mastered_questions: int
    total_questions: int
    wrong_answers: int
    xp: int
    level: int
    mastery_rule: str
    weak_categories: list[dict[str, object]]


class LearningJourneyMonthResponse(BaseModel):
    """Serializable learning journey month state."""

    month: int
    title: str
    completed_categories: int
    total_categories: int
    locked: bool
    checkpoint: bool


class OccupationResponse(BaseModel):
    """Serializable occupation response."""

    slug: str
    title: str
    duration_months: int
    specializations: list[str]


class CurriculumMonthResponse(BaseModel):
    """Serializable monthly curriculum roadmap entry."""

    month: int
    year: int
    title: str
    focus_area: str
    learning_goals: list[str]
    source_keys: list[str]
    is_exam_preparation: bool


class LearningModuleResponse(BaseModel):
    """Serializable learning module blueprint."""

    slug: str
    month: int
    title: str
    mission_type: str
    lesson_goal: str
    quiz_focus: str
    required_review: bool


class SourceDocumentResponse(BaseModel):
    """Serializable trusted source metadata."""

    key: str
    title: str
    publisher: str
    url: HttpUrl
    trust_tier: int
    allowed_usage: str
    topics: list[str]


class ContentGenerationRequest(BaseModel):
    """Request schema for generating a draft learning mission."""

    occupation_slug: str = Field(min_length=2)
    month: int = Field(ge=1, le=48)
    specialization_slug: str | None = None
    learner_level: str = Field(default="azubi", min_length=2, max_length=40)


class ContentReviewRequest(BaseModel):
    """Request schema for reviewing generated learning content."""

    draft_id: str = Field(min_length=8)
    approved: bool
    reviewer_notes: str = Field(min_length=3, max_length=1000)


class ContentGenerationResponse(BaseModel):
    """Response schema for a generated learning mission."""

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


class QuestionCategoryResponse(BaseModel):
    """Serializable question category."""

    slug: str
    month: int
    chapter_title: str
    subchapter_number: int
    title: str
    description: str


class QuizQuestionResponse(BaseModel):
    """Serializable practice question."""

    question_id: str
    category_slug: str
    prompt: str
    options: list[str]
    correct_option_index: int
    explanation: str
    difficulty: int
    exam_style: str
    source_keys: list[str]


class PracticeExamResponse(BaseModel):
    """Serializable practice exam with embedded questions."""

    exam_id: str
    title: str
    description: str
    questions: list[QuizQuestionResponse]
    passing_score_percent: int


class FirstChapterResponse(BaseModel):
    """Serializable first chapter content for the MVP learning path."""

    title: str
    mission_goal: str
    fachkunde: list[str]
    subchapters: list[QuestionCategoryResponse]
    checkpoint_exam_id: str
