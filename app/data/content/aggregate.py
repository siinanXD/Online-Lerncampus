"""Aggregate all curriculum content exports."""

from app.data.content.questions import ALL_QUESTIONS
from app.data.content.units import ALL_OPEN, ALL_UNITS

ALL_LEARNING_UNITS = ALL_UNITS
ALL_OPEN_QUESTIONS = ALL_OPEN
ALL_LEARNING_UNITS_BY_SLUG = {unit.slug: unit for unit in ALL_LEARNING_UNITS}
ALL_OPEN_QUESTIONS_BY_ID = {question.question_id: question for question in ALL_OPEN_QUESTIONS}
