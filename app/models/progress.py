"""Learner progress dataclasses."""

from dataclasses import dataclass


@dataclass
class QuestionProgress:
    """Mutable progress state for one learner question."""

    question_id: str
    answered_count: int = 0
    wrong_count: int = 0
    correct_streak: int = 0
    mastered: bool = False
    last_selected_option_index: int | None = None
