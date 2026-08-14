"""Pydantic schemas for learner tools, preferences, trainer and admin APIs."""

from pydantic import BaseModel, Field


class PreferencesResponse(BaseModel):
    """Stored UI and language preferences."""

    language: str
    theme: str
    high_contrast: bool
    reduce_motion: bool
    daily_goal_lessons: int


class PreferencesUpdateRequest(BaseModel):
    """Partial update for learner preferences."""

    language: str | None = Field(default=None, min_length=2, max_length=8)
    theme: str | None = Field(default=None, pattern="^(light|dark|system)$")
    high_contrast: bool | None = None
    reduce_motion: bool | None = None
    daily_goal_lessons: int | None = Field(default=None, ge=1, le=12)


class NotificationSettingsResponse(BaseModel):
    """Per-learner notification toggles."""

    daily_reminder: bool
    streak_risk: bool
    daily_goal_missed: bool
    level_up: bool
    new_badges: bool
    exam_ready: bool
    missing_reports: bool
    report_approved: bool
    new_content: bool
    maintenance: bool


class NotificationSettingsUpdateRequest(BaseModel):
    """Partial update for notification toggles."""

    daily_reminder: bool | None = None
    streak_risk: bool | None = None
    daily_goal_missed: bool | None = None
    level_up: bool | None = None
    new_badges: bool | None = None
    exam_ready: bool | None = None
    missing_reports: bool | None = None
    report_approved: bool | None = None
    new_content: bool | None = None
    maintenance: bool | None = None


class NotificationItemResponse(BaseModel):
    """One inbox notification."""

    id: int
    kind: str
    title: str
    body: str
    href: str | None
    read: bool
    created_at: str


class DailyGoalResponse(BaseModel):
    """Today's lesson target and progress."""

    goal_date: str
    lessons_completed: int
    lessons_goal: int
    lessons_remaining: int
    questions_answered: int
    minutes_studied: int
    minutes_studied_week: int
    completed: bool


class FormulaLegendItem(BaseModel):
    """One symbol in a formula legend."""

    symbol: str
    meaning: str


class FormulaResponse(BaseModel):
    """Formeltrainer entry."""

    id: int
    slug: str
    topic: str
    title: str
    expression: str
    legend: list[FormulaLegendItem]
    example: str
    difficulty: str
    source_keys: list[str]


class FormulaPracticeRequest(BaseModel):
    """Record a Formeltrainer practice check."""

    correct: bool = True


class DiagnosisCaseResponse(BaseModel):
    """Fehlerdiagnose scenario. Solution fields stay hidden until solved."""

    id: int
    slug: str
    topic: str
    title: str
    symptom: str
    options: list[str]
    difficulty: str
    estimated_minutes: int
    solved: bool = False
    correct_option_index: int | None = None
    explanation: str | None = None


class DiagnosisSolveRequest(BaseModel):
    """Selected option for one diagnosis case."""

    selected_option_index: int = Field(ge=0, le=10)


class DiagnosisSolveResponse(BaseModel):
    """Result of one diagnosis attempt."""

    slug: str
    is_correct: bool
    correct_option_index: int
    explanation: str


class VideoChapterResponse(BaseModel):
    """One chapter marker inside a video lesson."""

    start_seconds: int
    title: str


class VideoLessonResponse(BaseModel):
    """Videolektion metadata and watch progress."""

    id: int
    slug: str
    title: str
    description: str
    instructor: str
    duration_seconds: int
    topic: str
    thumbnail_url: str
    video_url: str
    chapters: list[VideoChapterResponse]
    next_slug: str | None
    watched_seconds: int = 0
    completed: bool = False


class VideoProgressRequest(BaseModel):
    """Watch progress for one video."""

    watched_seconds: int = Field(ge=0)
    completed: bool = False


class TranslationResponse(BaseModel):
    """One glossary translation row."""

    term: str
    language: str
    translation: str
    definition: str


class ContentFlagRequest(BaseModel):
    """Learner report for a content item."""

    entity_type: str = Field(min_length=3, max_length=40)
    entity_key: str = Field(min_length=1, max_length=80)
    reason: str = Field(min_length=3, max_length=80)
    notes: str = Field(default="", max_length=1000)


class ContentFlagResponse(BaseModel):
    """Stored content flag acknowledgement."""

    id: int
    entity_type: str
    entity_key: str
    reason: str
    created_at: str


class UnitCompleteResponse(BaseModel):
    """Result of marking a learning unit complete."""

    slug: str
    completed: bool
    completed_at: str


class LeaderboardEntryResponse(BaseModel):
    """Privacy-safe cohort ranking row."""

    rank: int
    alias: str
    xp: int
    level: int
    mastered_questions: int
    is_self: bool = False


class MediaAssetResponse(BaseModel):
    """Media metadata row."""

    id: int
    slug: str
    title: str
    media_type: str
    url: str
    uploaded_by: str | None = None
    created_at: str


class MediaAssetRequest(BaseModel):
    """Register a media URL (no binary upload in the MVP)."""

    slug: str = Field(min_length=3, max_length=80)
    title: str = Field(min_length=3, max_length=160)
    media_type: str = Field(pattern="^(image|video|pdf|audio|other)$")
    url: str = Field(min_length=3, max_length=500)


class CohortLearnerResponse(BaseModel):
    """Staff-visible learner row without login identifiers."""

    learner_id: str
    display_name: str
    role: str
    cohort_code: str | None
    tenant_id: str | None = None
    created_at: str


class RiskRowResponse(BaseModel):
    """Trainer risk overview for one apprentice."""

    learner_id: str
    display_name: str
    alias: str
    cohort_code: str | None
    tenant_id: str | None = None
    readiness_percent: int
    wrong_answers: int
    mastered_questions: int
    risk: str


class TrainerReportResponse(BaseModel):
    """Berichtsheft row in the trainer inbox."""

    id: int
    learner_id: str
    display_name: str
    cohort_code: str | None = None
    tenant_id: str | None = None
    report_date: str
    activities: str
    hours: float
    status: str
    trainer_status: str | None = None
    signed_at: str | None = None
    created_at: str
    updated_at: str


class TrainerReportDecisionRequest(BaseModel):
    """Approve or reject a Berichtsheft entry."""

    trainer_status: str = Field(pattern="^(pending|approved|rejected)$")


class ReportSuggestResponse(BaseModel):
    """Rule-based Berichtsheft draft."""

    report_date: str | None
    hours: float
    activities: str
    source: str


class ReportExportResponse(BaseModel):
    """Printable Berichtsheft export."""

    filename: str
    content_type: str
    body: str


class AuditEventResponse(BaseModel):
    """Admin audit log row."""

    id: int
    learner_id: str | None
    event_type: str
    metadata: dict[str, object]
    created_at: str


class MonitoringResponse(BaseModel):
    """Admin monitoring counters."""

    learners: int
    quiz_questions: int
    learning_units: int
    pending_reviews: int
    exam_sessions: int
    training_reports: int
    content_flags: int


class DuplicatePromptResponse(BaseModel):
    """Quiz prompt that exists more than once."""

    prompt: str
    copies: int
    question_ids: list[str]


class AppSettingsResponse(BaseModel):
    """Serializable app settings map."""

    settings: dict[str, object]


class AppSettingUpdateRequest(BaseModel):
    """Update one app setting."""

    key: str = Field(min_length=2, max_length=80)
    value: object


class RoleUpdateRequest(BaseModel):
    """Change a learner role."""

    role: str = Field(pattern="^(learner|reviewer|trainer|admin)$")


class TenantResponse(BaseModel):
    """One Bildungsbetrieb / organisation."""

    tenant_id: str
    name: str
    slug: str
    status: str
    created_at: str
    learner_count: int = 0
    cohort_count: int = 0


class TenantCreateRequest(BaseModel):
    """Create a new organisation."""

    name: str = Field(min_length=2, max_length=120)
    slug: str = Field(min_length=3, max_length=80)


class CohortResponse(BaseModel):
    """One class group inside an organisation."""

    cohort_id: str
    tenant_id: str
    code: str
    name: str
    created_at: str
    learner_count: int = 0


class CohortCreateRequest(BaseModel):
    """Create a class group."""

    code: str = Field(min_length=3, max_length=40)
    name: str = Field(min_length=2, max_length=120)


class AdminUserCreateRequest(BaseModel):
    """Provision a learner or staff account."""

    identifier: str = Field(min_length=3, max_length=120)
    password: str = Field(min_length=8, max_length=120)
    role: str = Field(pattern="^(learner|reviewer|trainer|admin)$")
    display_name: str | None = Field(default=None, max_length=80)
    cohort_code: str | None = Field(default=None, max_length=40)
    tenant_id: str | None = Field(default=None, max_length=80)
    is_platform_admin: bool = False


class TrainerHotspotResponse(BaseModel):
    """Weak topic aggregated for the trainer heatmap."""

    category_slug: str
    title: str
    wrong_count: int
    learner_count: int


class TrainerCockpitResponse(BaseModel):
    """Live Ausbilder cockpit payload."""

    tenant_id: str | None = None
    tenant_name: str | None = None
    cohort_code: str | None = None
    learner_count: int
    avg_readiness_percent: int
    high_risk_count: int
    pending_reports: int
    learners: list[RiskRowResponse]
