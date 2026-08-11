"""Content generation workflow with source and review safeguards."""

from hashlib import sha256

from app.models.domain import GeneratedContent, ReviewStatus
from app.schemas.content import ContentGenerationRequest, ContentReviewRequest
from app.services.curriculum_repository import CurriculumRepository
from app.services.privacy_guard import assert_no_personal_data
from app.services.source_repository import SourceRepository


class ContentFactory:
    """Generate and review learning content from verified curriculum context."""

    def __init__(
        self,
        curriculum_repository: CurriculumRepository,
        source_repository: SourceRepository,
    ) -> None:
        """Initialize the content factory with required repositories."""
        self.curriculum_repository = curriculum_repository
        self.source_repository = source_repository
        self._drafts: dict[str, GeneratedContent] = {}

    def generate_draft(
        self,
        request: ContentGenerationRequest,
    ) -> GeneratedContent:
        """Generate a deterministic draft mission for a curriculum month."""
        prompt_context = (
            f"{request.occupation_slug}:{request.specialization_slug}:"
            f"{request.month}:{request.learner_level}"
        )
        assert_no_personal_data(prompt_context)
        month = self.curriculum_repository.get_month(
            occupation_slug=request.occupation_slug,
            specialization_slug=request.specialization_slug,
            month=request.month,
        )
        if month is None:
            raise ValueError("No curriculum month found for request.")
        sources = self.source_repository.get_sources_by_keys(month.source_keys)
        draft_id = self._build_draft_id(prompt_context)
        source_titles = ", ".join(source.title for source in sources[:3])
        content = GeneratedContent(
            draft_id=draft_id,
            title=f"Mission {month.month:02d}: {month.title}",
            learning_goal=month.learning_goals[0],
            fachkunde=(
                f"In dieser Mission geht es um {month.focus_area}. "
                f"Du lernst die Grundlagen zuerst fachlich, danach als "
                f"praxisnahe Aufgabe an einer Produktionsanlage."
            ),
            practice_task=(
                "Bearbeite einen kurzen Produktionsfall: Lies die Vorgabe, "
                "waehle das passende Werkzeug oder Verfahren und begruende "
                "deine Entscheidung."
            ),
            quiz_question=f"Was ist bei '{month.title}' besonders wichtig?",
            quiz_options=[
                month.learning_goals[0],
                "Alle Arbeitsschritte ohne Dokumentation ausfuehren.",
                "Sicherheitsregeln nur bei der Abschlusspruefung beachten.",
                "Quellen und technische Unterlagen ignorieren.",
            ],
            correct_option=month.learning_goals[0],
            explanation=(
                "Die richtige Antwort ist direkt aus dem Lernziel abgeleitet. "
                f"Der Entwurf muss gegen diese Quellen geprueft werden: "
                f"{source_titles}."
            ),
            source_keys=month.source_keys,
            review_status=ReviewStatus.DRAFT,
            review_notes=[
                "Automatisch erzeugt.",
                "Fachreview vor Veroeffentlichung erforderlich.",
            ],
        )
        self._drafts[draft_id] = content
        return content

    def review_draft(self, request: ContentReviewRequest) -> GeneratedContent:
        """Update a generated draft based on human review feedback."""
        if request.draft_id not in self._drafts:
            raise ValueError("Draft not found.")
        assert_no_personal_data(request.reviewer_notes)
        current = self._drafts[request.draft_id]
        status = (
            ReviewStatus.APPROVED
            if request.approved
            else ReviewStatus.NEEDS_REVISION
        )
        reviewed = GeneratedContent(
            draft_id=current.draft_id,
            title=current.title,
            learning_goal=current.learning_goal,
            fachkunde=current.fachkunde,
            practice_task=current.practice_task,
            quiz_question=current.quiz_question,
            quiz_options=current.quiz_options,
            correct_option=current.correct_option,
            explanation=current.explanation,
            source_keys=current.source_keys,
            review_status=status,
            review_notes=[*current.review_notes, request.reviewer_notes],
        )
        self._drafts[request.draft_id] = reviewed
        return reviewed

    @staticmethod
    def _build_draft_id(seed: str) -> str:
        """Build a stable draft id from generation context."""
        digest = sha256(seed.encode("utf-8")).hexdigest()
        return f"draft_{digest[:16]}"
