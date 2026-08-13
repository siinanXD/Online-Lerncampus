"""Business logic for learner tools, daily goals, trainer and admin APIs."""

from __future__ import annotations

from typing import Any

from app.services.database import Database
from app.services.platform_repository import PlatformRepository
from app.services.progress_service import ProgressService


class PlatformService:
    """Facade over platform tables plus progress-derived staff views."""

    def __init__(
        self,
        database: Database,
        progress_service: ProgressService | None = None,
    ) -> None:
        """Attach repositories used by learner and staff endpoints."""
        self.database = database
        self.progress_service = progress_service
        self.repository = PlatformRepository(database)

    def complete_unit(self, learner_id: str, slug: str) -> dict[str, Any]:
        """Persist unit completion and count it toward the daily goal."""
        result = self.repository.complete_unit(learner_id, slug)
        self.repository.bump_daily_goal(learner_id, lessons=1, minutes=12)
        self.database.record_audit_event(
            event_type="learning.unit_completed",
            learner_id=learner_id,
            metadata={"slug": slug},
        )
        return result

    def learner_risk_rows(self, cohort_code: str | None) -> list[dict[str, Any]]:
        """Build a trainer risk table from mastery and wrong-answer counts."""
        if self.progress_service is None:
            return []
        rows: list[dict[str, Any]] = []
        for learner in self.repository.list_cohort_learners(cohort_code):
            if learner["role"] != "learner":
                continue
            summary = self.progress_service.dashboard_summary(learner["learner_id"])
            total = int(summary["total_questions"] or 1)
            mastered = int(summary["mastered_questions"])
            readiness = round((mastered / total) * 100) if total else 0
            wrong = int(summary["wrong_answers"])
            if readiness < 40 or wrong >= 8:
                level = "hoch"
            elif readiness < 60 or wrong >= 3:
                level = "mittel"
            else:
                level = "niedrig"
            rows.append(
                {
                    "learner_id": learner["learner_id"],
                    "display_name": learner["display_name"],
                    "alias": f"Azubi {learner['learner_id'][-4:]}",
                    "cohort_code": learner["cohort_code"],
                    "readiness_percent": readiness,
                    "wrong_answers": wrong,
                    "mastered_questions": mastered,
                    "risk": level,
                }
            )
        rows.sort(key=lambda item: item["readiness_percent"])
        return rows

    def suggest_training_report(self, learner_id: str) -> dict[str, Any]:
        """Build a rule-based Berichtsheft draft from recent learning activity."""
        if self.progress_service is None:
            raise ValueError("Fortschrittsservice fehlt.")
        journey = self.progress_service.learning_journey(learner_id)
        focus = next(
            (
                month
                for month in journey
                if not month["locked"]
                and int(month["completed_categories"])
                < int(month["total_categories"] or 1)
            ),
            journey[0] if journey else {"month": 1, "title": "Einstieg"},
        )
        dashboard = self.progress_service.dashboard_summary(learner_id)
        weak = list(dashboard.get("weak_categories") or [])
        weak_text = (
            f"Wiederholung zu {weak[0]['category_slug']}."
            if weak
            else "Wiederholung der aktuellen Fachkunde."
        )
        activities = (
            f"Betriebliche Taetigkeiten im Schwerpunkt Metall-/Kunststofftechnik. "
            f"Lerncampus: Monat {focus['month']} ({focus['title']}). {weak_text} "
            "Messwerte dokumentiert, Sicherheit beachtet, Berichtsheft gefuehrt."
        )
        return {
            "report_date": None,
            "hours": 8.0,
            "activities": activities,
            "source": "rule_based",
        }

    def dashboard_extras(self, learner_id: str) -> dict[str, Any]:
        """Return daily-goal and unit-completion extras for the dashboard."""
        daily = self.repository.get_daily_goal(learner_id)
        completed = self.repository.list_completed_unit_slugs(learner_id)
        return {
            "units_completed": len(completed),
            "daily_lessons_done": daily["lessons_completed"],
            "daily_lessons_goal": daily["lessons_goal"],
            "daily_questions_done": daily["questions_answered"],
            "study_minutes_today": daily["minutes_studied"],
            "study_minutes_week": daily["minutes_studied_week"],
            "week_minutes": self.repository.list_week_minutes(learner_id),
            "completed_unit_slugs": completed,
        }
