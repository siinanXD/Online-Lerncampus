"""Tests for privacy safeguards."""

import pytest

from app.services.privacy_guard import assert_no_personal_data, pseudonymize_learner_id


def test_rejects_email_address() -> None:
    """Ensure email addresses are not accepted in prompt payloads."""
    with pytest.raises(ValueError):
        assert_no_personal_data("Kontakt: azubi@example.com")


def test_rejects_phone_number() -> None:
    """Ensure phone numbers are not accepted in prompt payloads."""
    with pytest.raises(ValueError):
        assert_no_personal_data("Telefon: +49 2251 149107")


def test_accepts_neutral_learning_context() -> None:
    """Ensure normal learning context remains valid."""
    assert_no_personal_data("Antwort B, Kompetenz Messschieber ablesen")


def test_pseudonymization_is_stable() -> None:
    """Ensure pseudonyms remain stable across calls."""
    first_value = pseudonymize_learner_id("interne-id-42")
    second_value = pseudonymize_learner_id("interne-id-42")

    assert first_value == second_value
    assert first_value.startswith("learner_")
