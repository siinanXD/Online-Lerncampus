"""HTTP routes for learning content, sources, and review workflows."""

from fastapi import APIRouter, Header, HTTPException, Query, status

from app.core.config import get_settings
from app.schemas.content import (
    ConsentRequest,
    ConsentResponse,
    ContentGenerationRequest,
    ContentGenerationResponse,
    ContentReviewRequest,
    CurrentLearnerResponse,
    CurriculumMonthResponse,
    DashboardSummaryResponse,
    DataExportResponse,
    DeleteAccountResponse,
    FirstChapterResponse,
    HealthResponse,
    LearningJourneyMonthResponse,
    LearningModuleResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    OccupationResponse,
    PasswordChangeRequest,
    PasswordChangeResponse,
    PracticeExamResponse,
    ProgressAttemptRequest,
    QuestionCategoryResponse,
    QuestionProgressResponse,
    QuizQuestionResponse,
    SourceDocumentResponse,
)
from app.services.auth_service import AuthService, LearnerSession
from app.services.content_factory import ContentFactory
from app.services.curriculum_repository import CurriculumRepository
from app.services.database import Database
from app.services.progress_service import ProgressService
from app.services.question_repository import QuestionRepository
from app.services.source_repository import SourceRepository

api_router = APIRouter()
settings = get_settings()
database = Database(settings.database_url)
curriculum_repository = CurriculumRepository()
source_repository = SourceRepository()
question_repository = QuestionRepository()
auth_service = AuthService(
    database=database,
    app_secret=settings.app_secret,
    session_ttl_hours=settings.session_ttl_hours,
)
progress_service = ProgressService(
    question_repository=question_repository,
    database=database,
)
content_factory = ContentFactory(
    curriculum_repository=curriculum_repository,
    source_repository=source_repository,
)


def raise_bad_request(error: ValueError) -> None:
    """Raise a FastAPI bad-request error from a domain validation error."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=str(error),
    ) from error


def build_exam_response(exam_id: str) -> PracticeExamResponse:
    """Build one practice exam response from repository data."""
    result = question_repository.get_exam(exam_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Practice exam not found.",
        )
    exam, questions = result
    return PracticeExamResponse(
        exam_id=exam.exam_id,
        title=exam.title,
        description=exam.description,
        questions=[
            QuizQuestionResponse(
                question_id=question.question_id,
                category_slug=question.category_slug,
                prompt=question.prompt,
                options=question.options,
                correct_option_index=question.correct_option_index,
                explanation=question.explanation,
                difficulty=question.difficulty,
                exam_style=question.exam_style,
                source_keys=question.source_keys,
            )
            for question in questions
        ],
        passing_score_percent=exam.passing_score_percent,
    )


def get_session(authorization: str | None) -> LearnerSession:
    """Return the current learner session or raise an HTTP error."""
    try:
        return auth_service.authenticate(authorization)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error


@api_router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return a lightweight health check response."""
    return HealthResponse(status="ok")


@api_router.post("/auth/login", response_model=LoginResponse)
def login(request: LoginRequest) -> LoginResponse:
    """Create a pseudonymous learner session."""
    try:
        session = auth_service.login(
            identifier=request.identifier,
            password=request.password,
            cohort_code=request.cohort_code,
        )
    except ValueError as error:
        raise_bad_request(error)
    return LoginResponse(
        access_token=session.token,
        learner_id=session.learner_id,
        display_name=session.display_name,
        cohort_code=session.cohort_code,
        role=session.role,
    )


@api_router.get("/auth/me", response_model=CurrentLearnerResponse)
def get_current_learner(
    authorization: str | None = Header(default=None),
) -> CurrentLearnerResponse:
    """Return the authenticated learner profile."""
    session = get_session(authorization)
    return CurrentLearnerResponse(
        learner_id=session.learner_id,
        display_name=session.display_name,
        cohort_code=session.cohort_code,
        role=session.role,
    )


@api_router.post("/auth/logout", response_model=LogoutResponse)
def logout(authorization: str | None = Header(default=None)) -> LogoutResponse:
    """Revoke the current bearer token."""
    try:
        auth_service.logout(authorization)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        ) from error
    return LogoutResponse(success=True)


@api_router.post("/auth/password", response_model=PasswordChangeResponse)
def change_password(request: PasswordChangeRequest) -> PasswordChangeResponse:
    """Validate a password-change request for onboarding."""
    try:
        checklist = auth_service.validate_password_change(
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
    database.record_consent(
        learner_id=session.learner_id,
        consent_version=consent_version,
        accepted=request.accepted,
    )
    database.record_audit_event(
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


@api_router.get("/privacy/export", response_model=DataExportResponse)
def export_privacy_data(
    authorization: str | None = Header(default=None),
) -> DataExportResponse:
    """Return the authenticated learner's data export."""
    session = get_session(authorization)
    try:
        export = progress_service.export_learner_data(session.learner_id)
    except ValueError as error:
        raise_bad_request(error)
    database.record_audit_event(
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
    progress_service.delete_learner_data(session.learner_id)
    return DeleteAccountResponse(deleted=True)


@api_router.get("/dashboard", response_model=DashboardSummaryResponse)
def get_dashboard(
    authorization: str | None = Header(default=None),
) -> DashboardSummaryResponse:
    """Return dashboard metrics for the authenticated learner."""
    session = get_session(authorization)
    return progress_service.dashboard_summary(session.learner_id)


@api_router.get("/learning/journey", response_model=list[LearningJourneyMonthResponse])
def get_learning_journey(
    authorization: str | None = Header(default=None),
) -> list[LearningJourneyMonthResponse]:
    """Return the authenticated learner's 24-month learning journey."""
    session = get_session(authorization)
    return progress_service.learning_journey(session.learner_id)


@api_router.post("/progress/attempt", response_model=QuestionProgressResponse)
def record_progress_attempt(
    request: ProgressAttemptRequest,
    authorization: str | None = Header(default=None),
) -> QuestionProgressResponse:
    """Record one question answer for the authenticated learner."""
    session = get_session(authorization)
    try:
        progress, question, is_correct = progress_service.record_attempt(
            learner_id=session.learner_id,
            question_id=request.question_id,
            selected_option_index=request.selected_option_index,
        )
    except ValueError as error:
        raise_bad_request(error)
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
    )


@api_router.post("/progress/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_progress(authorization: str | None = Header(default=None)) -> None:
    """Reset all question progress for the authenticated learner."""
    session = get_session(authorization)
    progress_service.reset(session.learner_id)


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
    return question_repository.get_first_chapter()


@api_router.get("/questions/categories", response_model=list[QuestionCategoryResponse])
def list_question_categories(
    month: int | None = Query(default=None, ge=1, le=24),
) -> list[QuestionCategoryResponse]:
    """Return all question categories or categories for one month."""
    categories = question_repository.list_categories()
    if month is not None:
        categories = [category for category in categories if category.month == month]
    return categories


@api_router.get("/questions", response_model=list[QuizQuestionResponse])
def list_questions(
    category_slug: str | None = Query(default=None),
    month: int | None = Query(default=None, ge=1, le=24),
) -> list[QuizQuestionResponse]:
    """Return PAL-style practice questions."""
    return question_repository.list_questions(category_slug=category_slug, month=month)


@api_router.get("/exams", response_model=list[PracticeExamResponse])
def list_practice_exams() -> list[PracticeExamResponse]:
    """Return all practice exams with embedded questions."""
    return [
        build_exam_response(exam.exam_id)
        for exam in question_repository.list_exams()
    ]


@api_router.get("/exams/{exam_id}", response_model=PracticeExamResponse)
def get_practice_exam(exam_id: str) -> PracticeExamResponse:
    """Return one practice exam with embedded questions."""
    return build_exam_response(exam_id)


@api_router.post(
    "/content/generate",
    response_model=ContentGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
def generate_content(
    request: ContentGenerationRequest,
) -> ContentGenerationResponse:
    """Create a draft learning mission from verified curriculum context."""
    try:
        return content_factory.generate_draft(request)
    except ValueError as error:
        raise_bad_request(error)


@api_router.post("/content/review", response_model=ContentGenerationResponse)
def review_content(request: ContentReviewRequest) -> ContentGenerationResponse:
    """Review a draft learning mission and return its updated status."""
    try:
        return content_factory.review_draft(request)
    except ValueError as error:
        raise_bad_request(error)
