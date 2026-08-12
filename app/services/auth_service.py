"""Pseudonymous authentication service for the MVP."""

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from hmac import new as hmac_new
from secrets import token_urlsafe
from typing import Any

import bcrypt


@dataclass(frozen=True)
class LearnerSession:
    """Authenticated learner session without clear-text personal data."""

    token: str
    learner_id: str
    display_name: str
    cohort_code: str | None
    role: str = "learner"


class AuthService:
    """Create and validate pseudonymous demo sessions."""

    def __init__(
        self,
        database: Any,
        app_secret: str,
        session_ttl_hours: int,
    ) -> None:
        """Initialize persistent session handling."""
        if len(app_secret.strip()) < 8:
            raise ValueError("APP_SECRET must contain at least 8 characters.")
        if session_ttl_hours <= 0:
            raise ValueError("SESSION_TTL_HOURS must be greater than zero.")
        self.database = database
        self.app_secret = app_secret
        self.session_ttl_hours = session_ttl_hours

    def login(
        self,
        identifier: str,
        password: str,
        cohort_code: str | None = None,
    ) -> LearnerSession:
        """Create a pseudonymous learner session from login input."""
        clean_identifier = identifier.strip()
        clean_password = password.strip()
        clean_cohort = cohort_code.strip() if cohort_code else None
        if len(clean_identifier) < 3:
            raise ValueError("Benutzername oder E-Mail ist zu kurz.")
        if len(clean_password) < 4:
            raise ValueError("Passwort ist zu kurz.")
        identifier_hash = self._build_identifier_hash(clean_identifier)
        learner_id = f"learner_{identifier_hash[:16]}"
        role = "learner"
        display_name = "Azubi"
        existing = self.database.get_learner_by_identifier_hash(identifier_hash)
        if existing is None:
            password_hash = self._hash_password(clean_password)
        else:
            stored_hash = existing.get("password_hash")
            if stored_hash:
                if not self._verify_password(clean_password, stored_hash):
                    raise ValueError("Passwort ist falsch.")
                password_hash = None
            else:
                password_hash = self._hash_password(clean_password)
        self.database.upsert_learner(
            learner_id=learner_id,
            identifier_hash=identifier_hash,
            display_name=display_name,
            role=role,
            cohort_code=clean_cohort,
            password_hash=password_hash,
        )
        token = token_urlsafe(32)
        token_hash = self._hash_token(token)
        expires_at = datetime.now(tz=UTC) + timedelta(hours=self.session_ttl_hours)
        self.database.create_session(
            token_hash=token_hash,
            learner_id=learner_id,
            expires_at=expires_at,
        )
        self.database.record_audit_event(
            event_type="auth.login",
            learner_id=learner_id,
            metadata={"cohort": bool(clean_cohort)},
        )
        session = LearnerSession(
            token=token,
            learner_id=learner_id,
            display_name=display_name,
            cohort_code=clean_cohort,
            role=role,
        )
        return session

    def authenticate(self, authorization_header: str | None) -> LearnerSession:
        """Return the session for a bearer token or raise a validation error."""
        if not authorization_header:
            raise ValueError("Authorization header fehlt.")
        prefix = "Bearer "
        if not authorization_header.startswith(prefix):
            raise ValueError("Authorization header ist ungueltig.")
        token = authorization_header.removeprefix(prefix).strip()
        session_row = self.database.get_active_session(self._hash_token(token))
        if session_row is None:
            raise ValueError("Session ist unbekannt oder abgelaufen.")
        return LearnerSession(
            token=token,
            learner_id=session_row["learner_id"],
            display_name=session_row["display_name"],
            cohort_code=session_row["cohort_code"],
            role=session_row["role"],
        )

    def logout(self, authorization_header: str | None) -> None:
        """Revoke the current bearer token."""
        session = self.authenticate(authorization_header)
        self.database.revoke_session(self._hash_token(session.token))
        self.database.record_audit_event(
            event_type="auth.logout",
            learner_id=session.learner_id,
        )

    def change_password(
        self,
        authorization_header: str | None,
        current_password: str,
        new_password: str,
        repeated_password: str,
    ) -> dict[str, bool]:
        """Validate and persist a password change for the current learner."""
        session = self.authenticate(authorization_header)
        checklist = self.validate_password_change(
            current_password=current_password,
            new_password=new_password,
            repeated_password=repeated_password,
        )
        learner = self.database.get_learner(session.learner_id)
        if learner is None:
            raise ValueError("Lernkonto wurde nicht gefunden.")
        stored_hash = learner.get("password_hash")
        if stored_hash and not self._verify_password(current_password, stored_hash):
            raise ValueError("Aktuelles Passwort ist falsch.")
        self.database.update_password_hash(
            session.learner_id,
            self._hash_password(new_password),
        )
        self.database.record_audit_event(
            event_type="auth.password_changed",
            learner_id=session.learner_id,
        )
        return checklist

    def validate_password_change(
        self,
        current_password: str,
        new_password: str,
        repeated_password: str,
    ) -> dict[str, bool]:
        """Validate password-change input and return checklist state."""
        if not current_password:
            raise ValueError("Aktuelles Passwort fehlt.")
        if new_password != repeated_password:
            raise ValueError("Neue Passwoerter stimmen nicht ueberein.")
        checklist = {
            "min_length": len(new_password) >= 8,
            "mixed_case": any(char.islower() for char in new_password)
            and any(char.isupper() for char in new_password),
            "number": any(char.isdigit() for char in new_password),
            "special": any(not char.isalnum() for char in new_password),
        }
        if not all(checklist.values()):
            raise ValueError("Passwort erfuellt noch nicht alle Regeln.")
        return checklist

    def _build_identifier_hash(self, identifier: str) -> str:
        """Build a keyed login hash without storing the raw identifier."""
        return hmac_new(
            self.app_secret.encode("utf-8"),
            identifier.lower().encode("utf-8"),
            sha256,
        ).hexdigest()

    def _hash_token(self, token: str) -> str:
        """Build a non-reversible hash for a bearer token."""
        return hmac_new(
            self.app_secret.encode("utf-8"),
            token.encode("utf-8"),
            sha256,
        ).hexdigest()

    @staticmethod
    def _hash_password(password: str) -> str:
        """Return a bcrypt hash for a clear-text password."""
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        """Compare a clear-text password against a stored bcrypt hash."""
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
