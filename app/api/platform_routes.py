"""HTTP routes for learner tools, preferences, trainer and admin APIs."""

from fastapi import APIRouter, Header, Query
from fastapi.responses import Response

from app.api.routes import (
    _database,
    _progress,
    get_session,
    raise_bad_request,
    require_role,
)
from app.schemas.platform import (
    AppSettingsResponse,
    AppSettingUpdateRequest,
    AuditEventResponse,
    CohortLearnerResponse,
    ContentFlagRequest,
    ContentFlagResponse,
    DailyGoalResponse,
    DiagnosisCaseResponse,
    DiagnosisSolveRequest,
    DiagnosisSolveResponse,
    DuplicatePromptResponse,
    FormulaPracticeRequest,
    FormulaResponse,
    LeaderboardEntryResponse,
    MediaAssetRequest,
    MediaAssetResponse,
    MonitoringResponse,
    NotificationItemResponse,
    NotificationSettingsResponse,
    NotificationSettingsUpdateRequest,
    PreferencesResponse,
    PreferencesUpdateRequest,
    ReportExportResponse,
    ReportSuggestResponse,
    RiskRowResponse,
    RoleUpdateRequest,
    TrainerReportDecisionRequest,
    TrainerReportResponse,
    TranslationResponse,
    UnitCompleteResponse,
    VideoLessonResponse,
    VideoProgressRequest,
)
from app.services.platform_service import PlatformService

platform_router = APIRouter()


def _platform() -> PlatformService:
    """Return a platform service bound to the live database."""
    return PlatformService(
        database=_database(),
        progress_service=_progress(),
    )


def _public_diagnosis(case: dict) -> DiagnosisCaseResponse:
    """Hide solutions until the learner has solved the case."""
    solved = bool(case.get("solved"))
    return DiagnosisCaseResponse(
        id=int(case["id"]),
        slug=str(case["slug"]),
        topic=str(case["topic"]),
        title=str(case["title"]),
        symptom=str(case["symptom"]),
        options=list(case["options"]),
        difficulty=str(case["difficulty"]),
        estimated_minutes=int(case["estimated_minutes"]),
        solved=solved,
        correct_option_index=(
            int(case["correct_option_index"]) if solved else None
        ),
        explanation=str(case["explanation"]) if solved else None,
    )


@platform_router.get("/me/preferences", response_model=PreferencesResponse)
def get_preferences(
    authorization: str | None = Header(default=None),
) -> PreferencesResponse:
    """Return language, theme, and daily-goal preferences."""
    session = get_session(authorization)
    return PreferencesResponse(**_platform().repository.get_preferences(session.learner_id))


@platform_router.put("/me/preferences", response_model=PreferencesResponse)
def update_preferences(
    request: PreferencesUpdateRequest,
    authorization: str | None = Header(default=None),
) -> PreferencesResponse:
    """Update language, theme, accessibility, or daily goal size."""
    session = get_session(authorization)
    payload = _platform().repository.update_preferences(
        session.learner_id,
        language=request.language,
        theme=request.theme,
        high_contrast=request.high_contrast,
        reduce_motion=request.reduce_motion,
        daily_goal_lessons=request.daily_goal_lessons,
    )
    return PreferencesResponse(**payload)


@platform_router.get(
    "/me/notifications/settings",
    response_model=NotificationSettingsResponse,
)
def get_notification_settings(
    authorization: str | None = Header(default=None),
) -> NotificationSettingsResponse:
    """Return notification toggles."""
    session = get_session(authorization)
    return NotificationSettingsResponse(
        **_platform().repository.get_notification_settings(session.learner_id)
    )


@platform_router.put(
    "/me/notifications/settings",
    response_model=NotificationSettingsResponse,
)
def update_notification_settings(
    request: NotificationSettingsUpdateRequest,
    authorization: str | None = Header(default=None),
) -> NotificationSettingsResponse:
    """Update notification toggles."""
    session = get_session(authorization)
    updates = request.model_dump(exclude_none=True)
    return NotificationSettingsResponse(
        **_platform().repository.update_notification_settings(
            session.learner_id,
            updates,
        )
    )


@platform_router.get("/notifications", response_model=list[NotificationItemResponse])
def list_notifications(
    authorization: str | None = Header(default=None),
) -> list[NotificationItemResponse]:
    """Return the learner inbox."""
    session = get_session(authorization)
    return [
        NotificationItemResponse(**row)
        for row in _platform().repository.list_notifications(session.learner_id)
    ]


@platform_router.post("/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: int,
    authorization: str | None = Header(default=None),
) -> dict[str, bool]:
    """Mark one notification as read."""
    session = get_session(authorization)
    read = _platform().repository.mark_notification_read(
        session.learner_id,
        notification_id,
    )
    return {"read": read}


@platform_router.get("/daily-goal", response_model=DailyGoalResponse)
def get_daily_goal(
    authorization: str | None = Header(default=None),
) -> DailyGoalResponse:
    """Return today's lesson target."""
    session = get_session(authorization)
    return DailyGoalResponse(**_platform().repository.get_daily_goal(session.learner_id))


@platform_router.get("/formulas", response_model=list[FormulaResponse])
def list_formulas(
    topic: str | None = Query(default=None),
) -> list[FormulaResponse]:
    """Return Formeltrainer entries."""
    return [FormulaResponse(**row) for row in _platform().repository.list_formulas(topic)]


@platform_router.get("/formulas/{slug}", response_model=FormulaResponse)
def get_formula(slug: str) -> FormulaResponse:
    """Return one formula."""
    formula = _platform().repository.get_formula(slug)
    if formula is None:
        raise_bad_request(ValueError("Formel nicht gefunden."))
    return FormulaResponse(**formula)


@platform_router.post("/formulas/{slug}/practice")
def practice_formula(
    slug: str,
    request: FormulaPracticeRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    """Record one Formeltrainer practice check."""
    session = get_session(authorization)
    try:
        return _platform().repository.record_formula_practice(
            session.learner_id,
            slug,
            request.correct,
        )
    except ValueError as error:
        raise_bad_request(error)
        raise


@platform_router.get("/diagnosis", response_model=list[DiagnosisCaseResponse])
def list_diagnosis(
    authorization: str | None = Header(default=None),
) -> list[DiagnosisCaseResponse]:
    """Return Fehlerdiagnose cases without unsolved solutions."""
    learner_id = None
    if authorization:
        learner_id = get_session(authorization).learner_id
    return [
        _public_diagnosis(case)
        for case in _platform().repository.list_diagnosis_cases(learner_id)
    ]


@platform_router.post(
    "/diagnosis/{slug}/solve",
    response_model=DiagnosisSolveResponse,
)
def solve_diagnosis(
    slug: str,
    request: DiagnosisSolveRequest,
    authorization: str | None = Header(default=None),
) -> DiagnosisSolveResponse:
    """Score one diagnosis case."""
    session = get_session(authorization)
    try:
        payload = _platform().repository.solve_diagnosis_case(
            session.learner_id,
            slug,
            request.selected_option_index,
        )
    except ValueError as error:
        raise_bad_request(error)
        raise
    return DiagnosisSolveResponse(**payload)


@platform_router.get("/videos", response_model=list[VideoLessonResponse])
def list_videos(
    authorization: str | None = Header(default=None),
) -> list[VideoLessonResponse]:
    """Return videolections."""
    learner_id = None
    if authorization:
        learner_id = get_session(authorization).learner_id
    return [
        VideoLessonResponse(**row)
        for row in _platform().repository.list_videos(learner_id)
    ]


@platform_router.post("/videos/{slug}/progress")
def record_video_progress(
    slug: str,
    request: VideoProgressRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    """Store watch progress for one video."""
    session = get_session(authorization)
    try:
        return _platform().repository.record_video_progress(
            session.learner_id,
            slug,
            request.watched_seconds,
            request.completed,
        )
    except ValueError as error:
        raise_bad_request(error)
        raise


@platform_router.get("/glossary", response_model=list[TranslationResponse])
def search_glossary(
    q: str | None = Query(default=None),
    language: str | None = Query(default=None),
) -> list[TranslationResponse]:
    """Search translations for the Uebersetzungshilfe."""
    return [
        TranslationResponse(**row)
        for row in _platform().repository.search_translations(q, language)
    ]


@platform_router.post("/content/flags", response_model=ContentFlagResponse)
def flag_content(
    request: ContentFlagRequest,
    authorization: str | None = Header(default=None),
) -> ContentFlagResponse:
    """Report a content problem from the Melden screen."""
    session = get_session(authorization)
    payload = _platform().repository.create_content_flag(
        learner_id=session.learner_id,
        entity_type=request.entity_type,
        entity_key=request.entity_key,
        reason=request.reason,
        notes=request.notes,
    )
    _database().record_audit_event(
        event_type="content.flag",
        learner_id=session.learner_id,
        metadata={"entity_type": request.entity_type, "entity_key": request.entity_key},
    )
    return ContentFlagResponse(**payload)


@platform_router.post(
    "/learning/units/{slug}/complete",
    response_model=UnitCompleteResponse,
)
def complete_learning_unit(
    slug: str,
    authorization: str | None = Header(default=None),
) -> UnitCompleteResponse:
    """Mark one learning unit as completed."""
    session = get_session(authorization)
    try:
        payload = _platform().complete_unit(session.learner_id, slug)
    except ValueError as error:
        raise_bad_request(error)
        raise
    return UnitCompleteResponse(**payload)


@platform_router.get("/leaderboard", response_model=list[LeaderboardEntryResponse])
def get_leaderboard(
    authorization: str | None = Header(default=None),
) -> list[LeaderboardEntryResponse]:
    """Return a privacy-safe XP ranking for the current cohort."""
    session = get_session(authorization)
    rows = _platform().repository.xp_leaderboard(session.cohort_code)
    result = []
    for row in rows:
        is_self = row.pop("learner_id") == session.learner_id
        row.pop("is_self", None)
        result.append(LeaderboardEntryResponse(**row, is_self=is_self))
    return result


@platform_router.get("/media", response_model=list[MediaAssetResponse])
def list_media(
    authorization: str | None = Header(default=None),
) -> list[MediaAssetResponse]:
    """Return media metadata for trainer/admin screens."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    return [MediaAssetResponse(**row) for row in _platform().repository.list_media()]


@platform_router.post("/media", response_model=MediaAssetResponse)
def create_media(
    request: MediaAssetRequest,
    authorization: str | None = Header(default=None),
) -> MediaAssetResponse:
    """Register a media URL (binary uploads stay out of the MVP)."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    try:
        payload = _platform().repository.create_media(
            slug=request.slug,
            title=request.title,
            media_type=request.media_type,
            url=request.url,
            uploaded_by=session.learner_id,
        )
    except Exception as error:  # noqa: BLE001
        raise_bad_request(ValueError(str(error)))
        raise
    return MediaAssetResponse(**payload)


@platform_router.get("/trainer/learners", response_model=list[CohortLearnerResponse])
def list_trainer_learners(
    authorization: str | None = Header(default=None),
) -> list[CohortLearnerResponse]:
    """Return apprentices in the trainer cohort."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    return [
        CohortLearnerResponse(**row)
        for row in _platform().repository.list_cohort_learners(session.cohort_code)
        if row["role"] == "learner" or session.role == "admin"
    ]


@platform_router.get("/trainer/risk", response_model=list[RiskRowResponse])
def list_trainer_risk(
    authorization: str | None = Header(default=None),
) -> list[RiskRowResponse]:
    """Return a risk table derived from mastery and error counts."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    return [
        RiskRowResponse(**row)
        for row in _platform().learner_risk_rows(session.cohort_code)
    ]


@platform_router.get("/trainer/reports", response_model=list[TrainerReportResponse])
def list_trainer_reports(
    authorization: str | None = Header(default=None),
) -> list[TrainerReportResponse]:
    """Return Berichtsheft entries for trainer review."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    return [
        TrainerReportResponse(**row)
        for row in _platform().repository.list_all_training_reports()
    ]


@platform_router.post(
    "/trainer/reports/{report_id}/decision",
    response_model=TrainerReportResponse,
)
def decide_trainer_report(
    report_id: int,
    request: TrainerReportDecisionRequest,
    authorization: str | None = Header(default=None),
) -> TrainerReportResponse:
    """Approve or reject one Berichtsheft entry."""
    session = get_session(authorization)
    require_role(session, "reviewer", "trainer", "admin")
    try:
        row = _platform().repository.trainer_update_report(
            report_id,
            request.trainer_status,
        )
    except ValueError as error:
        raise_bad_request(error)
        raise
    if row is None:
        raise_bad_request(ValueError("Eintrag nicht gefunden."))
    _database().record_audit_event(
        event_type="training_report.decision",
        learner_id=session.learner_id,
        metadata={"report_id": report_id, "status": request.trainer_status},
    )
    # Trainer payload includes learner fields; merge from list if needed.
    inbox = _platform().repository.list_all_training_reports()
    match = next((item for item in inbox if int(item["id"]) == report_id), None)
    if match is None:
        raise_bad_request(ValueError("Eintrag nicht gefunden."))
    return TrainerReportResponse(**match)


@platform_router.post(
    "/training-reports/{report_id}/sign",
    response_model=TrainerReportResponse,
)
def sign_training_report(
    report_id: int,
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    """Submit a Berichtsheft entry for trainer signature."""
    session = get_session(authorization)
    row = _platform().repository.sign_training_report(session.learner_id, report_id)
    if row is None:
        raise_bad_request(ValueError("Eintrag nicht gefunden."))
    row.setdefault("learner_id", session.learner_id)
    row.setdefault("display_name", session.display_name)
    row.setdefault("cohort_code", session.cohort_code)
    row.setdefault("trainer_status", "pending")
    row.setdefault("signed_at", None)
    return row


@platform_router.get("/training-reports/suggest", response_model=ReportSuggestResponse)
def suggest_training_report(
    authorization: str | None = Header(default=None),
) -> ReportSuggestResponse:
    """Return a rule-based Berichtsheft draft (no LLM)."""
    session = get_session(authorization)
    return ReportSuggestResponse(**_platform().suggest_training_report(session.learner_id))


@platform_router.get(
    "/training-reports/export",
    response_model=ReportExportResponse,
)
def export_training_reports(
    authorization: str | None = Header(default=None),
) -> ReportExportResponse:
    """Return a printable Berichtsheft export."""
    session = get_session(authorization)
    body = _platform().repository.export_training_reports_text(session.learner_id)
    return ReportExportResponse(
        filename="berichtsheft-export.txt",
        content_type="text/plain",
        body=body,
    )


@platform_router.get("/training-reports/export.pdf")
def export_training_reports_pdf(
    authorization: str | None = Header(default=None),
) -> Response:
    """Download the Berichtsheft as a PDF file."""
    session = get_session(authorization)
    payload = _platform().repository.export_training_reports_pdf(session.learner_id)
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={
            "Content-Disposition": 'attachment; filename="berichtsheft.pdf"',
        },
    )


@platform_router.get("/admin/users", response_model=list[CohortLearnerResponse])
def list_admin_users(
    authorization: str | None = Header(default=None),
) -> list[CohortLearnerResponse]:
    """Return all active accounts for the admin user list."""
    session = get_session(authorization)
    require_role(session, "admin")
    return [
        CohortLearnerResponse(**row)
        for row in _platform().repository.list_cohort_learners(None)
    ]


@platform_router.post("/admin/users/{learner_id}/role")
def update_admin_user_role(
    learner_id: str,
    request: RoleUpdateRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, object]:
    """Change an account role."""
    session = get_session(authorization)
    require_role(session, "admin")
    try:
        row = _platform().repository.update_learner_role(learner_id, request.role)
    except ValueError as error:
        raise_bad_request(error)
        raise
    if row is None:
        raise_bad_request(ValueError("Konto nicht gefunden."))
    _database().record_audit_event(
        event_type="admin.role_change",
        learner_id=session.learner_id,
        metadata={"target": learner_id, "role": request.role},
    )
    return {
        "learner_id": row["learner_id"],
        "display_name": row["display_name"],
        "role": row["role"],
        "cohort_code": row["cohort_code"],
    }


@platform_router.get("/admin/audit", response_model=list[AuditEventResponse])
def list_admin_audit(
    authorization: str | None = Header(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AuditEventResponse]:
    """Return recent audit events."""
    session = get_session(authorization)
    require_role(session, "admin")
    return [
        AuditEventResponse(**row)
        for row in _platform().repository.list_audit_events(limit)
    ]


@platform_router.get("/admin/monitoring", response_model=MonitoringResponse)
def get_admin_monitoring(
    authorization: str | None = Header(default=None),
) -> MonitoringResponse:
    """Return monitoring counters."""
    session = get_session(authorization)
    require_role(session, "admin")
    return MonitoringResponse(**_platform().repository.monitoring_snapshot())


@platform_router.get("/admin/duplicates", response_model=list[DuplicatePromptResponse])
def list_admin_duplicates(
    authorization: str | None = Header(default=None),
) -> list[DuplicatePromptResponse]:
    """Return duplicate quiz prompts."""
    session = get_session(authorization)
    require_role(session, "admin")
    return [
        DuplicatePromptResponse(**row)
        for row in _platform().repository.list_duplicate_prompts()
    ]


@platform_router.get("/admin/settings", response_model=AppSettingsResponse)
def get_admin_settings(
    authorization: str | None = Header(default=None),
) -> AppSettingsResponse:
    """Return app settings."""
    session = get_session(authorization)
    require_role(session, "admin")
    return AppSettingsResponse(settings=_platform().repository.get_app_settings())


@platform_router.put("/admin/settings", response_model=AppSettingsResponse)
def update_admin_settings(
    request: AppSettingUpdateRequest,
    authorization: str | None = Header(default=None),
) -> AppSettingsResponse:
    """Update one app setting."""
    session = get_session(authorization)
    require_role(session, "admin")
    settings = _platform().repository.update_app_setting(request.key, request.value)
    _database().record_audit_event(
        event_type="admin.settings",
        learner_id=session.learner_id,
        metadata={"key": request.key},
    )
    return AppSettingsResponse(settings=settings)
