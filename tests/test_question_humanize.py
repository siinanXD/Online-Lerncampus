"""Tests for templated question prompt cleanup."""

from app.data.content.helpers import humanize_question_options, humanize_question_prompt


TITLE = "Willkommen in der Produktion: Fachsprache"


def test_humanize_prompt_removes_trailing_topic_reference() -> None:
    prompt = f"Welche Aussage passt am besten zu '{TITLE}'?"
    assert humanize_question_prompt(prompt, TITLE) == "Welche Aussage passt am besten?"


def test_humanize_prompt_removes_leading_bei_topic_reference() -> None:
    prompt = f"Bei '{TITLE}' tritt eine Abweichung auf."
    assert humanize_question_prompt(prompt, TITLE) == "Tritt eine Abweichung auf."


def test_humanize_options_remove_topic_prefix() -> None:
    options = [
        f"Zum Thema '{TITLE}' zuerst Unterlagen prüfen.",
        "Ohne Zeichnung starten.",
    ]
    cleaned = humanize_question_options(options, TITLE)
    assert cleaned[0] == "Zuerst Unterlagen prüfen."
    assert cleaned[1] == "Ohne Zeichnung starten."


def test_humanize_leaves_unrelated_prompts_unchanged() -> None:
    prompt = "Welche Aussage zu Sicherheit ist pruefungsrelevant?"
    assert humanize_question_prompt(prompt, TITLE) == prompt
