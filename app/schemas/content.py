"""Pydantic schemas for learning content API payloads."""

from pydantic import BaseModel, Field, HttpUrl

from app.models.domain import AnswerFormat, ReviewStatus


class HealthResponse(BaseModel):
    """Response schema for service health."""

    status: str


class ContentStatsResponse(BaseModel):
    """Public content inventory for marketing and landing pages."""

    quiz_questions: int
    learning_units: int
    exams: int
    preview_unit_title: str = ""


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
    requires_password_change: bool = False
    onboarding_completed: bool = False
    privacy_consent_accepted: bool = False


class CurrentLearnerResponse(BaseModel):
    """Response schema for the authenticated learner profile."""

    learner_id: str
    display_name: str
    cohort_code: str | None
    role: str
    requires_password_change: bool = False
    onboarding_completed: bool = False
    privacy_consent_accepted: bool = False


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


class OnboardingCompleteResponse(BaseModel):
    """Response schema after finishing the welcome onboarding."""

    onboarding_completed: bool = True


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


class QuestionProgressItemResponse(BaseModel):
    """Progress for one question without solution data."""

    question_id: str
    answered_count: int
    wrong_count: int
    correct_streak: int
    mastered: bool


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
    xp: int = 0
    level: int = 1
    xp_awarded: int = 0
    leveled_up: bool = False


class DashboardSummaryResponse(BaseModel):
    """Serializable learner dashboard metrics."""

    learner_id: str
    answered_questions: int
    mastered_questions: int
    total_questions: int
    wrong_answers: int
    open_questions: int = 0
    correct_once_questions: int = 0
    wrong_questions: int = 0
    xp: int
    level: int
    streak_days: int = 0
    badges: list[str] = Field(default_factory=list)
    mastery_rule: str
    weak_categories: list[dict[str, object]]
    units_completed: int = 0
    units_total: int = 0
    daily_lessons_done: int = 0
    daily_lessons_goal: int = 5
    daily_questions_done: int = 0
    study_minutes_today: int = 0
    study_minutes_week: int = 0
    continue_title: str = ""
    continue_answered: int = 0
    continue_total: int = 0
    readiness_percent: int = 0
    review_topic: str = ""
    xp_into_level: int = 0
    xp_per_level: int = 120
    week_minutes: list[int] = Field(default_factory=lambda: [0, 0, 0, 0, 0, 0, 0])


class GamificationResponse(BaseModel):
    """XP, level, streak, and badge summary derived from progress."""

    learner_id: str
    xp: int
    level: int
    xp_into_level: int
    xp_per_level: int
    streak_days: int
    longest_streak_days: int
    badges: list[str]
    answered_questions: int
    mastered_questions: int


class CoachTipResponse(BaseModel):
    """One rule-based coaching tip for the learner."""

    title: str
    body: str
    category_slug: str | None = None
    action_href: str | None = None


class CoachPlanResponse(BaseModel):
    """Simple coaching plan derived from weak categories and journey state."""

    greeting: str
    readiness_percent: int
    focus_month: int
    tips: list[CoachTipResponse]
    weak_categories: list[dict[str, object]]


class CoachChatRequest(BaseModel):
    """Learner message to the rule-based coach."""

    message: str = Field(min_length=1, max_length=2000)


class CoachChatResponse(BaseModel):
    """Coach reply plus an optional follow-up screen."""

    reply: str
    href: str | None = None


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


class QuizQuestionPublicResponse(BaseModel):
    """Practice question without solution data for learner-facing endpoints."""

    question_id: str
    category_slug: str
    prompt: str
    options: list[str]
    difficulty: int
    exam_style: str
    source_keys: list[str]


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


class GradingCriterionResponse(BaseModel):
    """One awardable point in an open task's marking scheme."""

    description: str
    points: int


class OpenQuestionResponse(BaseModel):
    """Serializable ungebundene Aufgabe.

    ``sample_solution`` stays out of the payload while the learner is still
    working; the exam endpoints only include it once the attempt is submitted.
    """

    question_id: str
    category_slug: str
    prompt: str
    answer_format: AnswerFormat
    criteria: list[GradingCriterionResponse]
    max_points: int
    source_keys: list[str]
    sample_solution: str | None = None


class TheoryBlockResponse(BaseModel):
    """One teaching step inside a learning unit."""

    heading: str
    body: str
    key_points: list[str]
    norm_references: list[str]


class LearningUnitResponse(BaseModel):
    """Serializable learning unit with theory, practice, and glossary."""

    slug: str
    month: int
    position: int
    title: str
    subtitle: str
    learning_goals: list[str]
    theory_blocks: list[TheoryBlockResponse]
    practice_task: str
    glossary: dict[str, str]
    category_slugs: list[str]
    source_keys: list[str]
    review_status: ReviewStatus
    estimated_minutes: int
    completed: bool = False


class PracticeExamResponse(BaseModel):
    """Serializable practice exam with embedded questions."""

    exam_id: str
    title: str
    description: str
    questions: list[QuizQuestionPublicResponse]
    passing_score_percent: int
    open_questions: list[OpenQuestionResponse] = Field(default_factory=list)
    time_limit_minutes: int = 0
    is_checkpoint: bool = False


class FirstChapterResponse(BaseModel):
    """Serializable first chapter content for the MVP learning path."""

    title: str
    mission_goal: str
    fachkunde: list[str]
    subchapters: list[QuestionCategoryResponse]
    checkpoint_exam_id: str


class ExamSessionStartResponse(BaseModel):
    """Response after starting a timed or untimed exam session."""

    session_id: int
    exam_id: str
    status: str
    started_at: str
    expires_at: str | None
    passing_score_percent: int
    time_limit_minutes: int
    exam: PracticeExamResponse


class ExamSessionStateResponse(BaseModel):
    """Current state of one learner exam session."""

    session_id: int
    exam_id: str
    status: str
    started_at: str
    expires_at: str | None
    submitted_at: str | None
    score_percent: float | None
    passed: bool | None
    passing_score_percent: int
    time_limit_minutes: int


class ExamChoiceAnswerRequest(BaseModel):
    """Request body for one exam single-choice answer."""

    question_id: str = Field(min_length=3, max_length=40)
    selected_option_index: int = Field(ge=0, le=10)


class ExamOpenAnswerRequest(BaseModel):
    """Request body for one open exam task answer."""

    question_id: str = Field(min_length=3, max_length=40)
    learner_answer: str = Field(min_length=1, max_length=4000)
    self_score: int | None = Field(default=None, ge=0)


class ExamAnswerSavedResponse(BaseModel):
    """Generic save acknowledgement for exam answers."""

    question_id: str
    saved: bool


class ExamSubmitResponse(BaseModel):
    """Final grading result for one submitted exam session."""

    session_id: int
    exam_id: str
    exam_title: str
    status: str
    score_percent: float
    passed: bool
    passing_score_percent: int
    choice_correct: int
    choice_total: int
    wrong_count: int
    unanswered_count: int
    duration_seconds: int
    xp_awarded: int
    open_score: int
    open_max_points: int
    weak_categories: list[dict[str, object]]
    category_breakdown: list[dict[str, object]] = Field(default_factory=list)


class ExamQuestionProgressItem(BaseModel):
    """Progress state for one exam question."""

    index: int
    question_id: str
    answered: bool
    marked: bool
    is_current: bool
    selected_option_index: int | None = None


class ExamSessionProgressResponse(BaseModel):
    """Live progress for an active exam session."""

    session_id: int
    exam_id: str
    exam_title: str
    expires_at: str | None
    total_questions: int
    answered_count: int
    open_count: int
    marked_count: int
    current_index: int
    current_question_id: str | None
    current_prompt: str | None
    progress_percent: int
    questions: list[ExamQuestionProgressItem]


class ExamMarkToggleRequest(BaseModel):
    """Request body to toggle a question mark."""

    question_id: str = Field(min_length=3, max_length=40)


class ExamMarkToggleResponse(BaseModel):
    """Response after toggling a question mark."""

    question_id: str
    marked: bool
    marked_count: int


class ContentReviewDecisionRequest(BaseModel):
    """Reviewer decision for one content entity."""

    entity_type: str = Field(pattern="^(learning_unit|quiz_question|open_question)$")
    entity_key: str = Field(min_length=2, max_length=80)
    to_status: str = Field(
        pattern="^(source_checked|approved|needs_revision|draft)$"
    )
    notes: str = Field(min_length=3, max_length=1000)


class ContentReviewDecisionResponse(BaseModel):
    """Result of one review workflow transition."""

    entity_type: str
    entity_key: str
    from_status: str
    to_status: str


class PendingContentReviewResponse(BaseModel):
    """One queue item awaiting reviewer action."""

    entity_type: str
    entity_id: int
    entity_key: str
    title: str
    review_status: str


class TrainingReportRequest(BaseModel):
    """Create or update one Berichtsheft entry."""

    report_date: str = Field(min_length=10, max_length=10)
    activities: str = Field(min_length=10, max_length=4000)
    hours: float = Field(default=8.0, gt=0, le=60)
    status: str | None = Field(default=None, pattern="^(draft|submitted)$")


class TrainingReportResponse(BaseModel):
    """Serializable Berichtsheft entry."""

    id: int
    report_date: str
    activities: str
    hours: float
    status: str
    signed_at: str | None = None
    trainer_status: str | None = None
    created_at: str
    updated_at: str
