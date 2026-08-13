"""Learner progress tracking for questions, exams, and dashboard metrics."""

from typing import Any

from app.models.domain import QuizQuestion
from app.models.progress import QuestionProgress
from app.services.question_repository import QuestionRepository


class ProgressService:
    """Track question attempts and derive dashboard summaries."""

    def __init__(
        self,
        question_repository: QuestionRepository,
        database: Any,
    ) -> None:
        """Initialize progress storage for learners."""
        self.question_repository = question_repository
        self.database = database

    def record_attempt(
        self,
        learner_id: str,
        question_id: str,
        selected_option_index: int,
    ) -> tuple[QuestionProgress, QuizQuestion, bool]:
        """Record one answer attempt and update mastery state."""
        question = self.question_repository.get_question(question_id)
        if question is None:
            raise ValueError("Frage wurde nicht gefunden.")
        if selected_option_index < 0 or selected_option_index >= len(question.options):
            raise ValueError("Antwortindex ist ungueltig.")
        progress = self.database.get_question_progress(
            learner_id=learner_id,
            question_id=question_id,
        ) or QuestionProgress(question_id=question_id)
        is_correct = selected_option_index == question.correct_option_index
        if progress.mastered and not is_correct:
            progress.mastered = False
            progress.correct_streak = 0
        progress.answered_count += 1
        progress.last_selected_option_index = selected_option_index
        if is_correct:
            progress.correct_streak += 1
        else:
            progress.wrong_count += 1
            progress.correct_streak = 0
        progress.mastered = (
            progress.answered_count >= 1 and progress.correct_streak >= 2
        )
        self.database.save_question_progress(
            learner_id=learner_id,
            progress=progress,
        )
        self._sync_category_progress(learner_id, question.category_slug)
        self.database.record_audit_event(
            event_type="progress.attempt",
            learner_id=learner_id,
            metadata={
                "question_id": question_id,
                "is_correct": is_correct,
                "mastered": progress.mastered,
            },
        )
        return progress, question, is_correct

    def get_question_progress(
        self,
        learner_id: str,
        question_id: str,
    ) -> QuestionProgress:
        """Return progress for a question, creating an empty state when needed."""
        return self.database.get_question_progress(
            learner_id=learner_id,
            question_id=question_id,
        ) or QuestionProgress(question_id=question_id)

    def dashboard_summary(self, learner_id: str) -> dict[str, object]:
        """Return dashboard metrics for one learner."""
        gamification = self.gamification_summary(learner_id)
        learner_progress = self.database.list_question_progress(learner_id)
        questions = self.question_repository.list_questions()
        total_questions = len(questions)
        wrong = sum(item.wrong_count for item in learner_progress.values())
        buckets = self._question_buckets(questions, learner_progress)
        weak_categories = self._weak_categories(learner_progress)
        return {
            "learner_id": learner_id,
            "answered_questions": gamification["answered_questions"],
            "mastered_questions": gamification["mastered_questions"],
            "total_questions": total_questions,
            "wrong_answers": wrong,
            "open_questions": buckets["open"],
            "correct_once_questions": buckets["once"],
            "wrong_questions": buckets["wrong"],
            "xp": gamification["xp"],
            "level": gamification["level"],
            "streak_days": gamification["streak_days"],
            "badges": gamification["badges"],
            "mastery_rule": "1x beantworten und 2x hintereinander richtig loesen",
            "weak_categories": weak_categories,
        }

    def gamification_summary(self, learner_id: str) -> dict[str, object]:
        """Derive XP, level, streak, and badges from stored progress activity."""
        learner_progress = self.database.list_question_progress(learner_id)
        answered = sum(
            1 for item in learner_progress.values() if item.answered_count > 0
        )
        mastered = sum(1 for item in learner_progress.values() if item.mastered)
        wrong = sum(item.wrong_count for item in learner_progress.values())
        xp = max(0, answered * 10 + mastered * 25 - wrong * 3)
        xp_per_level = 120
        level = 1 + xp // xp_per_level
        streak_days, longest_streak = self._streak_stats(learner_id)
        badges = self._derive_badges(
            answered=answered,
            mastered=mastered,
            streak_days=streak_days,
            longest_streak=longest_streak,
        )
        return {
            "learner_id": learner_id,
            "xp": xp,
            "level": level,
            "xp_into_level": xp % xp_per_level,
            "xp_per_level": xp_per_level,
            "streak_days": streak_days,
            "longest_streak_days": longest_streak,
            "badges": badges,
            "answered_questions": answered,
            "mastered_questions": mastered,
        }

    def coach_plan(self, learner_id: str) -> dict[str, object]:
        """Build a simple coaching plan from weak categories and journey state."""
        dashboard = self.dashboard_summary(learner_id)
        journey = self.learning_journey(learner_id)
        total = int(dashboard["total_questions"] or 1)
        mastered = int(dashboard["mastered_questions"])
        readiness = round((mastered / total) * 100) if total else 0
        weak = list(dashboard["weak_categories"])
        focus_month = next(
            (
                int(month["month"])
                for month in journey
                if not month["locked"]
                and int(month["completed_categories"])
                < int(month["total_categories"] or 1)
            ),
            1,
        )
        tips: list[dict[str, object]] = []
        if weak:
            top = weak[0]
            slug = str(top["category_slug"])
            tips.append(
                {
                    "title": f"Schwaeche: {slug}",
                    "body": (
                        f"Du hast {top['wrong_count']} Fehler in diesem Themenfeld. "
                        "Wiederhole 5 Fragen und schaue danach in die Lerneinheit."
                    ),
                    "category_slug": slug,
                    "action_href": "/lernen/fragen/fehler",
                }
            )
        tips.append(
            {
                "title": f"Fokus Monat {focus_month}",
                "body": (
                    "Arbeite die offenen Kategorien des aktuellen Ausbildungsmonats ab, "
                    "bevor du zur naechsten Pruefungssession gehst."
                ),
                "category_slug": None,
                "action_href": f"/lernen?month={focus_month}",
            }
        )
        if readiness < 60:
            tips.append(
                {
                    "title": "Pruefungsreife steigern",
                    "body": (
                        f"Aktuelle Reife: {readiness}%. Meistere zusaetzliche Fragen "
                        "(2x hintereinander richtig), um auf 60%+ zu kommen."
                    ),
                    "category_slug": None,
                    "action_href": "/fortschritt/pruefungsreife",
                }
            )
        else:
            tips.append(
                {
                    "title": "Checkpoint-Pruefung",
                    "body": (
                        f"Mit {readiness}% Reife bist du bereit fuer eine Checkpoint-Session "
                        "mit offenen Aufgaben."
                    ),
                    "category_slug": None,
                    "action_href": "/pruefungen",
                }
            )
        return {
            "greeting": (
                f"Hallo! Level {dashboard['level']} · {dashboard['xp']} XP · "
                f"{dashboard['streak_days']} Tage Streak."
            ),
            "readiness_percent": readiness,
            "focus_month": focus_month,
            "tips": tips,
            "weak_categories": weak,
        }

    def coach_chat(self, learner_id: str, message: str) -> dict[str, object]:
        """Answer a learner message from the current coaching plan (no LLM)."""
        plan = self.coach_plan(learner_id)
        tips = list(plan["tips"] or [])
        lowered = (message or "").strip().lower()
        href: str | None = None
        if any(token in lowered for token in ("formel", "kolben", "kraft", "berechn")):
            reply = (
                "Die Kolbenkraft ist F = p × A. Faustformel: p in bar und A in cm² "
                "ergibt F in N (Beispiel 6 bar × 20 cm² = 120 N). "
                "Im Formeltrainer kannst du das direkt üben."
            )
            href = "/lernen/formeltrainer"
        elif any(token in lowered for token in ("plan", "woche", "lernplan", "fokus")):
            tip = tips[1] if len(tips) > 1 else (tips[0] if tips else None)
            reply = (
                f"{plan['greeting']} Fokus Monat {plan['focus_month']}. "
                f"{tip['body'] if tip else 'Arbeite die offene Lerneinheit ab.'}"
            )
            href = str((tip or {}).get("action_href") or "/mehr/lernplan")
        elif any(token in lowered for token in ("fehler", "schwach", "wiederhol")):
            tip = tips[0] if tips else None
            reply = str((tip or {}).get("body") or "Wiederhole zuerst deine Fehlerfragen.")
            href = str((tip or {}).get("action_href") or "/lernen/fragen/fehler")
        elif any(token in lowered for token in ("prüfung", "pruefung", "reife", "exam")):
            tip = tips[-1] if tips else None
            reply = (
                f"Aktuelle Prüfungsreife: {plan['readiness_percent']}%. "
                f"{(tip or {}).get('body') or 'Mache als Nächstes eine Checkpoint-Session.'}"
            )
            href = str((tip or {}).get("action_href") or "/pruefungen")
        elif any(token in lowered for token in ("danke", "alles klar", "ok")):
            reply = "Gern. Als Nächstes: Lernplan öffnen oder fünf Fragen üben."
            href = "/mehr/lernplan"
        elif any(token in lowered for token in ("übung", "uebung", "fragen")):
            reply = "Starten wir mit Fragen üben — zuerst offene, dann Fehlerfragen."
            href = "/lernen/fragen"
        else:
            tip = tips[0] if tips else None
            reply = (
                f"{plan['greeting']} Fokus Monat {plan['focus_month']}. "
                f"{(tip or {}).get('body') or 'Setze die aktuelle Lerneinheit fort.'}"
            )
            href = str((tip or {}).get("action_href") or "/lernen")
        return {"reply": reply, "href": href}

    def learning_journey(self, learner_id: str) -> list[dict[str, object]]:
        """Return month-by-month journey state for one learner."""
        learner_progress = self.database.list_question_progress(learner_id)
        categories = self.question_repository.list_categories()
        questions = self.question_repository.list_questions()
        category_to_questions: dict[str, list[str]] = {}
        for question in questions:
            category_to_questions.setdefault(question.category_slug, []).append(
                question.question_id
            )
        months: list[dict[str, object]] = []
        previous_complete = True
        for month_number in range(1, 25):
            month_categories = [
                category for category in categories if category.month == month_number
            ]
            completed_categories = 0
            for category in month_categories:
                question_ids = category_to_questions.get(category.slug, [])
                if question_ids and all(
                    learner_progress.get(question_id) is not None
                    and learner_progress[question_id].mastered
                    for question_id in question_ids
                ):
                    completed_categories += 1
            total = len(month_categories)
            months.append(
                {
                    "month": month_number,
                    "title": month_categories[0].chapter_title if month_categories else f"Monat {month_number}",
                    "completed_categories": completed_categories,
                    "total_categories": total,
                    "locked": month_number > 1 and not previous_complete,
                    "checkpoint": month_number in (12, 24),
                }
            )
            previous_complete = total == 0 or completed_categories >= total
        return months

    def reset(self, learner_id: str) -> None:
        """Delete all progress for one learner."""
        self.database.reset_progress(learner_id)
        self.database.record_audit_event(
            event_type="progress.reset",
            learner_id=learner_id,
        )

    def export_learner_data(self, learner_id: str) -> dict[str, object]:
        """Return learner data with derived dashboard and journey state."""
        export = self.database.export_learner_data(learner_id)
        export["dashboard"] = self.dashboard_summary(learner_id)
        export["learning_journey"] = self.learning_journey(learner_id)
        return export

    def delete_learner_data(self, learner_id: str) -> None:
        """Delete learner-owned data from persistence."""
        self.database.record_audit_event(
            event_type="privacy.delete_requested",
            learner_id=learner_id,
        )
        self.database.delete_learner_data(learner_id)

    def _sync_category_progress(self, learner_id: str, category_slug: str) -> None:
        """Update aggregate category mastery when content tables are populated."""
        category_id = self.database.get_category_id_by_slug(category_slug)
        if category_id is None:
            return
        questions = self.question_repository.list_questions(category_slug=category_slug)
        if not questions:
            return
        learner_progress = self.database.list_question_progress(learner_id)
        mastered = sum(
            1
            for question in questions
            if learner_progress.get(question.question_id) is not None
            and learner_progress[question.question_id].mastered
        )
        self.database.upsert_category_progress(
            learner_id=learner_id,
            category_id=category_id,
            questions_mastered=mastered,
            questions_total=len(questions),
        )

    def list_question_progress_items(self, learner_id: str) -> list[dict[str, object]]:
        """Return compact progress rows for every attempted question."""
        return [
            {
                "question_id": item.question_id,
                "answered_count": item.answered_count,
                "wrong_count": item.wrong_count,
                "correct_streak": item.correct_streak,
                "mastered": item.mastered,
            }
            for item in self.database.list_question_progress(learner_id).values()
        ]

    @staticmethod
    def _question_buckets(questions, learner_progress: dict[str, QuestionProgress]) -> dict[str, int]:
        """Split questions into open / once-correct / wrong / mastered buckets."""
        open_count = 0
        once = 0
        wrong = 0
        done = 0
        for question in questions:
            item = learner_progress.get(question.question_id)
            if item is None or item.answered_count <= 0:
                open_count += 1
            elif item.mastered:
                done += 1
            elif item.correct_streak >= 1:
                once += 1
            else:
                wrong += 1
        return {"open": open_count, "once": once, "wrong": wrong, "done": done}

    def _weak_categories(
        self,
        learner_progress: dict[str, QuestionProgress],
    ) -> list[dict[str, object]]:
        """Return categories with the highest wrong-answer count."""
        questions = {
            question.question_id: question
            for question in self.question_repository.list_questions()
        }
        category_totals: dict[str, int] = {}
        for question in questions.values():
            category_totals[question.category_slug] = (
                category_totals.get(question.category_slug, 0) + 1
            )
        category_counts: dict[str, int] = {}
        for question_id, progress in learner_progress.items():
            if progress.wrong_count <= 0:
                continue
            question = questions.get(question_id)
            if question is None:
                continue
            category_counts[question.category_slug] = (
                category_counts.get(question.category_slug, 0) + progress.wrong_count
            )
        rows: list[dict[str, object]] = []
        for category_slug, wrong_count in sorted(
            category_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:5]:
            total = category_totals.get(category_slug, wrong_count)
            correct = max(total - wrong_count, 0)
            percent = round((correct / total) * 100) if total else 0
            rows.append(
                {
                    "category_slug": category_slug,
                    "wrong_count": wrong_count,
                    "total_count": total,
                    "correct_count": correct,
                    "percent": percent,
                }
            )
        return rows

    def _streak_stats(self, learner_id: str) -> tuple[int, int]:
        """Compute current and longest consecutive activity-day streaks."""
        from datetime import date, timedelta

        days = self.database.list_activity_dates(learner_id)
        if not days:
            return 0, 0
        parsed = sorted({date.fromisoformat(day) for day in days}, reverse=True)
        today = date.today()
        current = 0
        if parsed[0] in {today, today - timedelta(days=1)}:
            expected = parsed[0]
            for day in parsed:
                if day == expected:
                    current += 1
                    expected = day - timedelta(days=1)
                elif day < expected:
                    break
        longest = 1
        run = 1
        chronological = list(reversed(parsed))
        for index in range(1, len(chronological)):
            if chronological[index] == chronological[index - 1] + timedelta(days=1):
                run += 1
                longest = max(longest, run)
            else:
                run = 1
        longest = max(longest, current)
        return current, longest

    @staticmethod
    def _derive_badges(
        *,
        answered: int,
        mastered: int,
        streak_days: int,
        longest_streak: int,
    ) -> list[str]:
        """Return unlocked badge labels for the learner."""
        badges: list[str] = []
        if answered >= 1:
            badges.append("Erster Schritt")
        if mastered >= 5:
            badges.append("5x gemeistert")
        if mastered >= 20:
            badges.append("Fachkunde-Starter")
        if streak_days >= 3:
            badges.append("3-Tage-Streak")
        if longest_streak >= 7:
            badges.append("Wochen-Streak")
        if answered >= 50:
            badges.append("Fleissig")
        return badges
