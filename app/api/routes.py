"""HTTP routes for learning content, sources, and review workflows."""

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.core.config import get_settings
from app.data.content.helpers import humanize_question_options, humanize_question_prompt
from app.models.domain import LearningUnit
from app.schemas.content import (
    ConsentRequest,
    ConsentResponse,
    ContentStatsResponse,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentReviewRequest,
    CurrentLearnerResponse,
    CurriculumMonthResponse,
    CoachChatRequest,
    CoachChatResponse,
    CoachPlanResponse,
    CoachTipResponse,
    DashboardSummaryResponse,
    DataExportResponse,
    DeleteAccountResponse,
    ExamAnswerSavedResponse,
    ExamChoiceAnswerRequest,
    ExamMarkToggleRequest,
    ExamMarkToggleResponse,
    ExamOpenAnswerRequest,
    ExamSessionProgressResponse,
    ExamSessionStartResponse,
    ExamSessionStateResponse,
    ExamSubmitResponse,
    FirstChapterResponse,
    GamificationResponse,
    GradingCriterionResponse,
    HealthResponse,
    LearningJourneyMonthResponse,
    LearningModuleResponse,
    LearningUnitResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    OccupationResponse,
    OpenQuestionResponse,
    OnboardingCompleteResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    PracticeExamResponse,
    ProgressAttemptRequest,
    QuestionCategoryResponse,
    QuestionProgressItemResponse,
    QuestionProgressResponse,
    QuizQuestionPublicResponse,
    QuizQuestionResponse,
    SourceDocumentResponse,
    TheoryBlockResponse,
    TrainingReportRequest,
    TrainingReportResponse,
    PendingContentReviewResponse,
    ContentReviewDecisionRequest,
    ContentReviewDecisionResponse,
)
from app.services.auth_service import AuthService, LearnerSession
from app.services.content_factory import ContentFactory
from app.services.content_seeder import ContentSeeder
from app.services.exam_session_service import ExamSessionService
from app.services.curriculum_repository import CurriculumRepository
from app.services.database import Database, create_database
from app.services.progress_service import ProgressService
from app.services.question_repository import QuestionRepository
from app.services.source_repository import SourceRepository
from app.services.platform_repository import PlatformRepository

api_router = APIRouter()
settings = get_settings()
database: Database | None = None
curriculum_repository = CurriculumRepository()
source_repository = SourceRepository()
question_repository: QuestionRepository | None = None
progress_service: ProgressService | None = None
exam_session_service: ExamSessionService | None = None
auth_service: AuthService | None = None
content_factory = ContentFactory(
    curriculum_repository=curriculum_repository,
    source_repository=source_repository,
)


def _database() -> Database:
    global database
    if database is None:
        database = create_database(get_settings().database_url)
    return database


def _auth() -> AuthService:
    global auth_service
    if auth_service is None:
        current = get_settings()
        auth_service = AuthService(
            database=_database(),
            app_secret=current.app_secret,
            session_ttl_hours=current.session_ttl_hours,
        )
    return auth_service


def _auth_profile(learner_id: str) -> dict[str, bool]:
    """Return onboarding and password flags for one learner."""
    db = _database()
    learner = db.get_learner(learner_id)
    if learner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lernkonto wurde nicht gefunden.",
        )
    prefs = PlatformRepository(db).get_preferences(learner_id)
    return {
        "requires_password_change": bool(learner.get("requires_password_change")),
        "onboarding_completed": bool(prefs.get("onboarding_completed")),
        "privacy_consent_accepted": db.has_privacy_consent(learner_id),
    }


def _bootstrap_platform_admin() -> None:
    """Provision the configured platform admin once at startup."""
    current = get_settings()
    identifier = current.bootstrap_admin_identifier.strip()
    password = current.bootstrap_admin_password.strip()
    if not identifier or not password:
        return
    try:
        _auth().provision_user(
            identifier=identifier,
            password=password,
            role="admin",
            display_name="Plattform-Admin",
            is_platform_admin=True,
        )
    except ValueError as error:
        if "existiert bereits" not in str(error):
            raise


def bootstrap_content_store() -> None:
    """Load or seed curriculum content and wire dependent services."""
    global question_repository, progress_service, exam_session_service
    current = get_settings()
    source = current.content_source
    if source not in ("db", "memory"):
        raise ValueError("CONTENT_SOURCE must be 'db' or 'memory'.")
    if source == "db" and current.content_seed_on_startup:
        from pathlib import Path

        from app.data.content_bundle import load_json_bundle, load_python_bundle

        if current.content_seed_format == "json":
            bundle = load_json_bundle(Path(current.content_json_bundle_path))
        else:
            bundle = load_python_bundle()
        seeder = ContentSeeder(_database(), bundle=bundle)
        if seeder.is_empty():
            seeder.seed_all()
            if not current.content_review_required:
                _database().approve_all_content()
        from app.services.platform_seeder import PlatformSeeder

        platform_seeder = PlatformSeeder(_database())
        if platform_seeder.is_empty():
            platform_seeder.seed_all()
    _bootstrap_platform_admin()
    question_repository = QuestionRepository(
        database=_database(),
        content_source=source,  # type: ignore[arg-type]
        content_review_required=current.content_review_required,
    )
    progress_service = ProgressService(
        question_repository=question_repository,
        database=_database(),
    )
    exam_session_service = ExamSessionService(
        database=_database(),
        question_repository=question_repository,
    )


def _exams() -> ExamSessionService:
    if exam_session_service is None:
        bootstrap_content_store()
    assert exam_session_service is not None
    return exam_session_service


def _questions() -> QuestionRepository:
    if question_repository is None:
        bootstrap_content_store()
    assert question_repository is not None
    return question_repository


def _progress() -> ProgressService:
    if progress_service is None:
        bootstrap_content_store()
    assert progress_service is not None
    return progress_service


def raise_bad_request(error: ValueError) -> None:
    """Raise a FastAPI bad-request error from a domain validation error."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    ) from error


def build_public_question_response(
    question,
    category_titles: dict[str, str] | None = None,
) -> QuizQuestionPublicResponse:
    """Return a learner-safe question payload without solution fields."""
    category_title = (category_titles or {}).get(question.category_slug)
    return QuizQuestionPublicResponse(
        question_id=question.question_id,
        category_slug=question.category_slug,
        prompt=humanize_question_prompt(question.prompt, category_title),
        options=humanize_question_options(question.options, category_title),
        difficulty=question.difficulty,
        exam_style=question.exam_style,
        source_keys=question.source_keys,
    )


def _category_title_map(month: int | None = None) -> dict[str, str]:
    """Build a slug-to-title lookup for question categories."""
    categories = _questions().list_categories()
    if month is not None:
        categories = [category for category in categories if category.month == month]
    return {category.slug: category.title for category in categories}


def build_exam_response(
    exam_id: str, include_solutions: bool = False
) -> PracticeExamResponse:
    """Build one practice exam response from repository data.

    Sample solutions for open tasks stay hidden unless ``include_solutions``
    is set, so a learner cannot read them out of the exam payload.
    """
    result = _questions().get_exam(exam_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice exam not found.",
        )
    exam, questions = result
    category_titles = _category_title_map()
    return PracticeExamResponse(
        exam_id=exam.exam_id,
        title=exam.title,
        description=exam.description,
        questions=[
            build_public_question_response(question, category_titles)
            for question in questions
        ],
        passing_score_percent=exam.passing_score_percent,
        open_questions=[
            OpenQuestionResponse(
                question_id=question.question_id,
                category_slug=question.category_slug,
                prompt=question.prompt,
                answer_format=question.answer_format,
                criteria=[
                    GradingCriterionResponse(
                        description=criterion.description,
                        points=criterion.points,
                    )
                    for criterion in question.criteria
                ],
                max_points=question.max_points,
                source_keys=question.source_keys,
                sample_solution=(
                    question.sample_solution if include_solutions else None
                ),
            )
            for question in _questions().list_open_questions(
                exam.open_question_ids
            )
        ],
        time_limit_minutes=exam.time_limit_minutes,
        is_checkpoint=exam.is_checkpoint,
    )


def build_learning_unit_response(
    unit: LearningUnit,
    completed: bool = False,
) -> LearningUnitResponse:
    """Build one learning unit response from repository data."""
    return LearningUnitResponse(
        slug=unit.slug,
        month=unit.month,
        position=unit.position,
        title=unit.title,
        subtitle=unit.subtitle,
        learning_goals=unit.learning_goals,
        theory_blocks=[
            TheoryBlockResponse(
                heading=block.heading,
                body=block.body,
                key_points=block.key_points,
                norm_references=block.norm_references,
            )
            for block in unit.theory_blocks
        ],
        practice_task=unit.practice_task,
        glossary=unit.glossary,
        category_slugs=unit.category_slugs,
        source_keys=unit.source_keys,
        review_status=unit.review_status,
        estimated_minutes=unit.estimated_minutes,
        completed=completed,
    )


def require_role(session: LearnerSession, *roles: str) -> None:
    """Raise HTTP 403 when the current session lacks a required role."""
    if session.role not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Keine Berechtigung fuer diese Aktion.",
        )


def get_session(authorization: str | None) -> LearnerSession:
    """Return the current learner session or raise an HTTP error."""
    try:
        return _auth().authenticate(authorization)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error


def _category_title(slug: str) -> str:
    """Turn a category slug into a readable German label."""
    return slug.replace("-", " ").strip().title()


@api_router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a lightweight health check response."""
    return HealthResponse(status="ok")


@api_router.get("/content/stats", response_model=ContentStatsResponse)
def get_content_stats() -> ContentStatsResponse:
    """Return public content counts for landing and marketing pages."""
    questions = _questions()
    units = questions.list_learning_units()
    return ContentStatsResponse(
        quiz_questions=len(questions.list_questions()),
        learning_units=len(units),
        exams=len(questions.list_exams()),
        preview_unit_title=units[0].title if units else "",
    )


@api_router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """Create a pseudonymous learner session."""
    try:
        session = _auth().login(
            identifier=request.identifier,
            password=request.password,
            cohort_code=request.cohort_code,
        )
    except ValueError as error:
        raise_bad_request(error)
    profile = _auth_profile(session.learner_id)
    return LoginResponse(
        access_token=session.token,
        learner_id=session.learner_id,
        display_name=session.display_name,
        cohort_code=session.cohort_code,
        role=session.role,
        tenant_id=session.tenant_id,
        tenant_name=session.tenant_name,
        is_platform_admin=session.is_platform_admin,
        **profile,
    )


@api_router.get("/auth/me", response_model=CurrentLearnerResponse)
def get_current_learner(
    authorization: str | None = Header(default=None),
) -> CurrentLearnerResponse:
    """Return the authenticated learner profile."""
    session = get_session(authorization)
    profile = _auth_profile(session.learner_id)
    return CurrentLearnerResponse(
        learner_id=session.learner_id,
        display_name=session.display_name,
        cohort_code=session.cohort_code,
        role=session.role,
        tenant_id=session.tenant_id,
        tenant_name=session.tenant_name,
        is_platform_admin=session.is_platform_admin,
        **profile,
    )


@api_router.post("/auth/logout", response_model=LogoutResponse)
def logout(authorization: str | None = Header(default=None)) -> LogoutResponse:
    """Revoke the current bearer token."""
    try:
        _auth().logout(authorization)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
    return LogoutResponse(success=True)


@api_router.post("/auth/password", response_model=PasswordChangeResponse)
def change_password(
    request: PasswordChangeRequest,
    authorization: str | None = Header(default=None),
) -> PasswordChangeResponse:
    """Validate and persist a password change for the current learner."""
    try:
        checklist = _auth().change_password(
            authorization_header=authorization,
            current_password=request.current_password,
            new_password=request.new_password,
            repeated_password=request.repeated_password,
        )
    except ValueError as error:
        raise_bad_request(error)
    return PasswordChangeResponse(accepted=True, checklist=checklist)


@api_router.post("/privacy/consent", response_model=ConsentResponse)
def record_privacy_consent(
    request: ConsentRequest,
    authorization: str | None = Header(default=None),
) -> ConsentResponse:
    """Store a privacy notice acknowledgement for the current learner."""
    session = get_session(authorization)
    consent_version = request.consent_version or settings.privacy_notice_version
    _database().record_consent(
        learner_id=session.learner_id,
        consent_version=consent_version,
        accepted=request.accepted,
    )
    _database().record_audit_event(
        event_type="privacy.consent",
        learner_id=session.learner_id,
        metadata={
            "accepted": request.accepted,
            "consent_version": consent_version,
        },
    )
    return ConsentResponse(
        accepted=request.accepted,
        consent_version=consent_version,
    )


@api_router.post("/auth/onboarding/complete", response_model=OnboardingCompleteResponse)
def complete_onboarding(
    authorization: str | None = Header(default=None),
) -> OnboardingCompleteResponse:
    """Mark the welcome onboarding as completed for the current learner."""
    session = get_session(authorization)
    PlatformRepository(_database()).complete_onboarding(session.learner_id)
    _database().record_audit_event(
        event_type="auth.onboarding_completed",
        learner_id=session.learner_id,
    )
    return OnboardingCompleteResponse(onboarding_completed=True)


@api_router.get("/privacy/export", response_model=DataExportResponse)
def export_privacy_data(
    authorization: str | None = Header(default=None),
) -> DataExportResponse:
    """Return the authenticated learner's data export."""
    session = get_session(authorization)
    try:
        export = _progress().export_learner_data(session.learner_id)
    except ValueError as error:
        raise_bad_request(error)
    _database().record_audit_event(
        event_type="privacy.export",
        learner_id=session.learner_id,
    )
    return DataExportResponse(data=export)


@api_router.delete("/privacy/account", response_model=DeleteAccountResponse)
def delete_privacy_account(
    authorization: str | None = Header(default=None),
) -> DeleteAccountResponse:
    """Delete the authenticated learner's account and learning data."""
    session = get_session(authorization)
    _progress().delete_learner_data(session.learner_id)
    return DeleteAccountResponse(deleted=True)


@api_router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard(
    authorization: str | None = Header(default=None),
) -> DashboardSummaryResponse:
    """Return dashboard metrics for the authenticated learner."""
    session = get_session(authorization)
    summary = dict(_progress().dashboard_summary(session.learner_id))
    gamification = _progress().gamification_summary(session.learner_id)
    from app.services.platform_service import PlatformService

    extras = PlatformService(_database(), _progress()).dashboard_extras(
        session.learner_id
    )
    units = _questions().list_learning_units()
    completed = set(extras.get("completed_unit_slugs") or [])
    next_unit = next((unit for unit in units if unit.slug not in completed), None)
    total = int(summary["total_questions"] or 1)
    mastered = int(summary["mastered_questions"])
    weak = list(summary.get("weak_categories") or [])
    review_topic = _category_title(str(weak[0]["category_slug"])) if weak else ""
    summary.update(
        {
            "units_completed": extras["units_completed"],
            "units_total": len(units),
            "daily_lessons_done": extras["daily_lessons_done"],
            "daily_lessons_goal": extras["daily_lessons_goal"],
            "daily_questions_done": extras["daily_questions_done"],
            "study_minutes_today": extras["study_minutes_today"],
            "study_minutes_week": extras["study_minutes_week"],
            "week_minutes": extras["week_minutes"],
            "continue_title": next_unit.title if next_unit else "",
            "continue_answered": mastered,
            "continue_total": total,
            "readiness_percent": round((mastered / total) * 100) if total else 0,
            "review_topic": review_topic,
            "xp_into_level": int(gamification["xp_into_level"]),
            "xp_per_level": int(gamification["xp_per_level"]),
        }
    )
    return DashboardSummaryResponse(**summary)


@api_router.get("/gamification", response_model=GamificationResponse)
def get_gamification(
    authorization: str | None = Header(default=None),
) -> GamificationResponse:
    """Return XP, level, streak, and badges for the authenticated learner."""
    session = get_session(authorization)
    return GamificationResponse(**_progress().gamification_summary(session.learner_id))


@api_router.get("/coach/plan", response_model=CoachPlanResponse)
def get_coach_plan(
    authorization: str | None = Header(default=None),
) -> CoachPlanResponse:
    """Return a rule-based coaching plan from learner progress."""
    session = get_session(authorization)
    plan = _progress().coach_plan(session.learner_id)
    return CoachPlanResponse(
        greeting=str(plan["greeting"]),
        readiness_percent=int(plan["readiness_percent"]),
        focus_month=int(plan["focus_month"]),
        tips=[CoachTipResponse(**tip) for tip in plan["tips"]],
        weak_categories=list(plan["weak_categories"]),
    )


@api_router.post("/coach/chat", response_model=CoachChatResponse)
def post_coach_chat(
    request: CoachChatRequest,
    authorization: str | None = Header(default=None),
) -> CoachChatResponse:
    """Return a rule-based coach reply from the current learning plan."""
    session = get_session(authorization)
    payload = _progress().coach_chat(session.learner_id, request.message)
    return CoachChatResponse(
        reply=str(payload["reply"]),
        href=str(payload["href"]) if payload.get("href") else None,
    )


@api_router.get("/learning/journey", response_model=list[LearningJourneyMonthResponse])
def get_learning_journey(
    authorization: str | None = Header(default=None),
) -> list[LearningJourneyMonthResponse]:
    """Return the authenticated learner's 24-month learning journey."""
    session = get_session(authorization)
    return _progress().learning_journey(session.learner_id)


@api_router.get("/progress", response_model=list[QuestionProgressItemResponse])
def list_progress(
    authorization: str | None = Header(default=None),
) -> list[QuestionProgressItemResponse]:
    """Return the authenticated learner's question progress rows."""
    session = get_session(authorization)
    return [
        QuestionProgressItemResponse(**item)
        for item in _progress().list_question_progress_items(session.learner_id)
    ]


@api_router.post("/progress/attempt", response_model=QuestionProgressResponse)
def record_progress_attempt(
    request: ProgressAttemptRequest,
    authorization: str | None = Header(default=None),
) -> QuestionProgressResponse:
    """Record one question answer for the authenticated learner."""
    session = get_session(authorization)
    before = _progress().gamification_summary(session.learner_id)
    try:
        progress, question, is_correct = _progress().record_attempt(
            learner_id=session.learner_id,
            question_id=request.question_id,
            selected_option_index=request.selected_option_index,
        )
    except ValueError as error:
        raise_bad_request(error)
    from app.services.platform_repository import PlatformRepository

    PlatformRepository(_database()).bump_daily_goal(
        session.learner_id,
        questions=1,
        minutes=1,
    )
    after = _progress().gamification_summary(session.learner_id)
    xp_awarded = max(0, int(after["xp"]) - int(before["xp"]))
    return QuestionProgressResponse(
        question_id=progress.question_id,
        answered_count=progress.answered_count,
        wrong_count=progress.wrong_count,
        correct_streak=progress.correct_streak,
        mastered=progress.mastered,
        selected_option_index=request.selected_option_index,
        correct_option_index=question.correct_option_index,
        is_correct=is_correct,
        explanation=question.explanation,
        xp=int(after["xp"]),
        level=int(after["level"]),
        xp_awarded=xp_awarded,
        leveled_up=int(after["level"]) > int(before["level"]),
    )


@api_router.post("/progress/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_progress(authorization: str | None = Header(default=None)) -> None:
    """Reset all question progress for the authenticated learner."""
    session = get_session(authorization)
    _progress().reset(session.learner_id)


@api_router.get("/occupations", response_model=list[OccupationResponse])
def list_occupations() -> list[OccupationResponse]:
    """Return all supported occupations."""
    return curriculum_repository.list_occupations()


@api_router.get(
    "/occupations/{occupation_slug}/curriculum",
    response_model=list[CurriculumMonthResponse],
)
def get_curriculum(
    occupation_slug: str,
    specialization_slug: str | None = Query(default=None),
) -> list[CurriculumMonthResponse]:
    """Return the curriculum roadmap for an occupation."""
    curriculum = curriculum_repository.get_curriculum(
        occupation_slug=occupation_slug,
        specialization_slug=specialization_slug,
    )
    if not curriculum:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Curriculum not found.",
        )
    return curriculum


@api_router.get(
    "/occupations/{occupation_slug}/modules",
    response_model=list[LearningModuleResponse],
)
def list_learning_modules(
    occupation_slug: str,
    specialization_slug: str | None = Query(default=None),
) -> list[LearningModuleResponse]:
    """Return generated module blueprints for an occupation."""
    modules = curriculum_repository.list_learning_modules(
        occupation_slug=occupation_slug,
        specialization_slug=specialization_slug,
    )
    if not modules:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning modules not found.",
        )
    return modules


@api_router.get("/sources", response_model=list[SourceDocumentResponse])
def list_sources() -> list[SourceDocumentResponse]:
    """Return trusted source documents for content generation."""
    return source_repository.list_sources()


@api_router.get("/learning/first-chapter", response_model=FirstChapterResponse)
def get_first_chapter() -> FirstChapterResponse:
    """Return the first guided chapter for the learning app."""
    return _questions().get_first_chapter()


@api_router.get("/learning/units", response_model=list[LearningUnitResponse])
def list_learning_units(
    month: int | None = Query(default=None, ge=1, le=24),
    authorization: str | None = Header(default=None),
) -> list[LearningUnitResponse]:
    """Return the ausformulierte learning units, optionally filtered by month."""
    completed: set[str] = set()
    if authorization:
        try:
            session = get_session(authorization)
            from app.services.platform_repository import PlatformRepository

            completed = set(
                PlatformRepository(_database()).list_completed_unit_slugs(
                    session.learner_id
                )
            )
        except HTTPException:
            completed = set()
    return [
        build_learning_unit_response(unit, completed=unit.slug in completed)
        for unit in _questions().list_learning_units(month=month)
    ]


@api_router.get("/learning/units/{slug}", response_model=LearningUnitResponse)
def get_learning_unit(slug: str) -> LearningUnitResponse:
    """Return one learning unit with theory, practice task, and glossary."""
    try:
        unit = _questions().get_learning_unit(slug)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lerneinheit nicht gefunden.",
        ) from None
    return build_learning_unit_response(unit)


@api_router.get("/questions/categories", response_model=list[QuestionCategoryResponse])
def list_question_categories(
    month: int | None = Query(default=None, ge=1, le=24),
) -> list[QuestionCategoryResponse]:
    """Return all question categories or categories for one month."""
    categories = _questions().list_categories()
    if month is not None:
        categories = [category for category in categories if category.month == month]
    return categories


@api_router.get("/questions", response_model=list[QuizQuestionPublicResponse])
def list_questions(
    category_slug: str | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=24),
) -> list[QuizQuestionPublicResponse]:
    """Return PAL-style practice questions without solution data."""
    category_titles = _category_title_map(month=month)
    return [
        build_public_question_response(question, category_titles)
        for question in _questions().list_questions(
            category_slug=category_slug,
            month=month,
        )
    ]


@api_router.get("/exams", response_model=list[PracticeExamResponse])
def list_practice_exams() -> list[PracticeExamResponse]:
    """Return all practice exams with embedded questions."""
    return [
        build_exam_response(exam.exam_id)
        for exam in _questions().list_exams()
    ]


@api_router.get("/exams/{exam_id}", response_model=PracticeExamResponse)
def get_practice_exam(exam_id: str) -> PracticeExamResponse:
    """Return one practice exam with embedded questions."""
    return build_exam_response(exam_id)


@api_router.post(
    "/exams/{exam_id}/sessions",
    response_model=ExamSessionStartResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_exam_session(
    exam_id: str,
    authorization: str | None = Header(default=None),
) -> ExamSessionStartResponse:
    """Start a server-side exam session for the authenticated learner."""
    session = get_session(authorization)
    try:
        state = _exams().start_session(session.learner_id, exam_id)
    except ValueError as error:
        raise_bad_request(error)
    return ExamSessionStartResponse(
        session_id=state.session_id,
        exam_id=state.exam_id,
        status=state.status,
        started_at=state.started_at,
        expires_at=state.expires_at,
        passing_score_percent=state.passing_score_percent,
        time_limit_minutes=state.time_limit_minutes,
        exam=build_exam_response(exam_id),
    )


@api_router.get(
    "/exams/sessions/{session_id}",
    response_model=ExamSessionStateResponse,
)
def get_exam_session_state(
    session_id: int,
    authorization: str | None = Header(default=None),
) -> ExamSessionStateResponse:
    """Return the current state of one exam session."""
    session = get_session(authorization)
    try:
        state = _exams().get_session(session.learner_id, session_id)
    except ValueError as error:
        raise_bad_request(error)
    return ExamSessionStateResponse(
        session_id=state.session_id,
        exam_id=state.exam_id,
        status=state.status,
        started_at=state.started_at,
        expires_at=state.expires_at,
        submitted_at=state.submitted_at,
        score_percent=state.score_percent,
        passed=state.passed,
        passing_score_percent=state.passing_score_percent,
        time_limit_minutes=state.time_limit_minutes,
    )


@api_router.get(
    "/exams/sessions/{session_id}/progress",
    response_model=ExamSessionProgressResponse,
)
def get_exam_session_progress(
    session_id: int,
    current_question_id: str | None = Query(default=None),
    authorization: str | None = Header(default=None),
) -> ExamSessionProgressResponse:
    """Return live answer, mark, and navigation progress for one exam session."""
    session = get_session(authorization)
    try:
        payload = _exams().get_progress(
            learner_id=session.learner_id,
            session_id=session_id,
            current_question_id=current_question_id,
        )
    except ValueError as error:
        raise_bad_request(error)
    return ExamSessionProgressResponse(**payload)


@api_router.post(
    "/exams/sessions/{session_id}/marks",
    response_model=ExamMarkToggleResponse,
)
def toggle_exam_question_mark(
    session_id: int,
    request: ExamMarkToggleRequest,
    authorization: str | None = Header(default=None),
) -> ExamMarkToggleResponse:
    """Toggle a review mark for one question in an active exam session."""
    session = get_session(authorization)
    try:
        payload = _exams().toggle_mark(
            learner_id=session.learner_id,
            session_id=session_id,
            question_id=request.question_id,
        )
    except ValueError as error:
        raise_bad_request(error)
    return ExamMarkToggleResponse(**payload)


@api_router.post(
    "/exams/sessions/{session_id}/answers",
    response_model=ExamAnswerSavedResponse,
)
def save_exam_choice_answer(
    session_id: int,
    request: ExamChoiceAnswerRequest,
    authorization: str | None = Header(default=None),
) -> ExamAnswerSavedResponse:
    """Save one single-choice answer for an active exam session."""
    session = get_session(authorization)
    try:
        payload = _exams().record_choice_answer(
            learner_id=session.learner_id,
            session_id=session_id,
            question_id=request.question_id,
            selected_option_index=request.selected_option_index,
        )
    except ValueError as error:
        raise_bad_request(error)
    return ExamAnswerSavedResponse(
        question_id=str(payload["question_id"]),
        saved=bool(payload["saved"]),
    )


@api_router.post(
    "/exams/sessions/{session_id}/open-answers",
    response_model=ExamAnswerSavedResponse,
)
def save_exam_open_answer(
    session_id: int,
    request: ExamOpenAnswerRequest,
    authorization: str | None = Header(default=None),
) -> ExamAnswerSavedResponse:
    """Save one open task answer for an active exam session."""
    session = get_session(authorization)
    try:
        payload = _exams().record_open_answer(
            learner_id=session.learner_id,
            session_id=session_id,
            question_id=request.question_id,
            learner_answer=request.learner_answer,
            self_score=request.self_score,
        )
    except ValueError as error:
        raise_bad_request(error)
    return ExamAnswerSavedResponse(
        question_id=str(payload["question_id"]),
        saved=bool(payload["saved"]),
    )


@api_router.post(
    "/exams/sessions/{session_id}/submit",
    response_model=ExamSubmitResponse,
)
def submit_exam_session(
    session_id: int,
    authorization: str | None = Header(default=None),
) -> ExamSubmitResponse:
    """Submit and grade one exam session."""
    session = get_session(authorization)
    try:
        payload = _exams().submit_session(session.learner_id, session_id)
    except ValueError as error:
        raise_bad_request(error)
    return ExamSubmitResponse(**payload)


@api_router.post(
    "/content/generate",
    response_model=ContentGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_content(
    request: ContentGenerationRequest,
    authorization: str | None = Header(default=None),
) -> ContentGenerationResponse:
    """Create a draft learning mission from verified curriculum context."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    try:
        return content_factory.generate_draft(request)
    except ValueError as error:
        raise_bad_request(error)


@api_router.post("/content/review", response_model=ContentGenerationResponse)
def review_content(
    request: ContentReviewRequest,
    authorization: str | None = Header(default=None),
) -> ContentGenerationResponse:
    """Review a draft learning mission and return its updated status."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    try:
        return content_factory.review_draft(request)
    except ValueError as error:
        raise_bad_request(error)


@api_router.get(
    "/content/review/pending",
    response_model=list[PendingContentReviewResponse],
)
def list_pending_content_reviews(
    authorization: str | None = Header(default=None),
) -> list[PendingContentReviewResponse]:
    """Return draft content awaiting reviewer approval."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    rows = _database().list_pending_reviews()
    return [PendingContentReviewResponse(**row) for row in rows]


@api_router.post(
    "/content/review/decision",
    response_model=ContentReviewDecisionResponse,
)
def decide_content_review(
    request: ContentReviewDecisionRequest,
    authorization: str | None = Header(default=None),
) -> ContentReviewDecisionResponse:
    """Apply one review transition to DB-backed content."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    try:
        payload = _database().apply_content_review(
            entity_type=request.entity_type,
            entity_key=request.entity_key,
            to_status=request.to_status,
            reviewer_learner_id=session.learner_id,
            notes=request.notes,
        )
    except ValueError as error:
        raise_bad_request(error)
    _database().record_audit_event(
        event_type="content.review",
        learner_id=session.learner_id,
        metadata=payload,
    )
    return ContentReviewDecisionResponse(**payload)


@api_router.get(
    "/training-reports",
    response_model=list[TrainingReportResponse],
)
def list_training_reports(
    authorization: str | None = Header(default=None),
) -> list[TrainingReportResponse]:
    """Return Berichtsheft entries for the authenticated learner."""
    session = get_session(authorization)
    rows = _database().list_training_reports(session.learner_id)
    return [TrainingReportResponse(**row) for row in rows]


@api_router.post(
    "/training-reports",
    response_model=TrainingReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_training_report(
    request: TrainingReportRequest,
    authorization: str | None = Header(default=None),
) -> TrainingReportResponse:
    """Create one Berichtsheft entry."""
    session = get_session(authorization)
    row = _database().create_training_report(
        learner_id=session.learner_id,
        report_date=request.report_date,
        activities=request.activities,
        hours=request.hours,
    )
    return TrainingReportResponse(**row)


@api_router.put(
    "/training-reports/{report_id}",
    response_model=TrainingReportResponse,
)
def update_training_report(
    report_id: int,
    request: TrainingReportRequest,
    authorization: str | None = Header(default=None),
) -> TrainingReportResponse:
    """Update one Berichtsheft entry."""
    session = get_session(authorization)
    row = _database().update_training_report(
        session.learner_id,
        report_id,
        report_date=request.report_date,
        activities=request.activities,
        hours=request.hours,
        status=request.status,
    )
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Eintrag nicht gefunden.")
    return TrainingReportResponse(**row)
