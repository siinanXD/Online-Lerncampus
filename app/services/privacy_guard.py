"""Privacy safeguards for prompt and learner-data handling."""

import re
from hashlib import sha256

EMAIL_PATTERN = re.compile(r"\b[\w.-]+@[\w.-]+\.\w+\b")
PHONE_PATTERN = re.compile(r"\b(?:\+\d{1,3}[\s-]?)?(?:\d[\s-]?){7,}\b")


def assert_no_personal_data(payload: str) -> None:
    """Raise an error when obvious personal data is found in a payload."""
    if EMAIL_PATTERN.search(payload):
        raise ValueError("Payload contains an email address.")
    if PHONE_PATTERN.search(payload):
        raise ValueError("Payload contains a phone number.")


def pseudonymize_learner_id(raw_user_id: str) -> str:
    """Return a stable non-identifying learner reference for prompt context."""
    normalized = raw_user_id.strip()
    if not normalized:
        raise ValueError("User id must not be empty.")
    assert_no_personal_data(normalized)
    digest = sha256(normalized.encode("utf-8")).hexdigest()
    return f"learner_{digest[:12]}"
