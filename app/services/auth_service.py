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
    tenant_id: str | None = None
    tenant_name: str | None = None
    is_platform_admin: bool = False


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
        clean_identifier = identifier.strip().lower()
        clean_password = password.strip()
        clean_cohort = cohort_code.strip() if cohort_code else None
        if len(clean_identifier) < 3:
            raise ValueError("Benutzername oder E-Mail ist zu kurz.")
        if len(clean_password) < 4:
            raise ValueError("Passwort ist zu kurz.")
        role, display_name = self._resolve_role(clean_identifier)
        identifier_hash = self._build_identifier_hash(clean_identifier)
        learner_id = f"learner_{identifier_hash[:16]}"
        existing = self.database.get_learner_by_identifier_hash(identifier_hash)
        is_new_learner = existing is None
        is_platform_admin = (
            role == "admin" and clean_identifier.startswith("admin-")
            if is_new_learner
            else bool((existing or {}).get("is_platform_admin"))
        )
        from app.db.tenant_schema import DEFAULT_TENANT_ID
        from app.services.tenant_repository import TenantRepository

        tenants = TenantRepository(self.database)
        tenant_id = tenants.resolve_tenant_id(
            clean_cohort,
            platform_admin=is_platform_admin,
        )
        if is_platform_admin:
            tenant_id = None
        elif tenant_id is None:
            tenant_id = DEFAULT_TENANT_ID
        if is_new_learner:
            password_hash = self._hash_password(clean_password)
        else:
            stored_hash = existing.get("password_hash")
            if stored_hash:
                if not self._verify_password(clean_password, stored_hash):
                    raise ValueError("Passwort ist falsch.")
                password_hash = None
            else:
                password_hash = self._hash_password(clean_password)
            if existing.get("tenant_id") and not is_platform_admin:
                tenant_id = existing.get("tenant_id") or tenant_id
            role = str(existing.get("role") or role)
            display_name = str(existing.get("display_name") or display_name)
            if existing.get("cohort_code") and not clean_cohort:
                clean_cohort = existing.get("cohort_code")
        tenant = tenants.get_tenant(tenant_id) if tenant_id else None
        self.database.upsert_learner(
            learner_id=learner_id,
            identifier_hash=identifier_hash,
            display_name=display_name,
            role=role,
            cohort_code=clean_cohort,
            tenant_id=tenant_id,
            is_platform_admin=is_platform_admin,
            password_hash=password_hash,
        )
        if is_new_learner and self._requires_initial_password_change(clean_identifier):
            self.database.set_requires_password_change(learner_id, True)
        from app.services.platform_repository import PlatformRepository

        PlatformRepository(self.database).ensure_learner_defaults(learner_id)
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
            metadata={"cohort": bool(clean_cohort), "tenant_id": tenant_id},
        )
        return self._build_session(
            token=token,
            learner_id=learner_id,
            display_name=display_name,
            cohort_code=clean_cohort,
            role=role,
            tenant_id=tenant_id,
            is_platform_admin=is_platform_admin,
            tenant_name=str(tenant["name"]) if tenant else None,
        )

    def provision_user(
        self,
        *,
        identifier: str,
        password: str,
        role: str,
        display_name: str | None = None,
        cohort_code: str | None = None,
        tenant_id: str | None = None,
        is_platform_admin: bool = False,
    ) -> dict[str, Any]:
        """Create a staff or learner account for one organisation."""
        allowed = {"learner", "reviewer", "trainer", "admin"}
        if role not in allowed:
            raise ValueError("Ungueltige Rolle.")
        clean_identifier = identifier.strip().lower()
        clean_password = password.strip()
        if len(clean_identifier) < 3:
            raise ValueError("Benutzername oder E-Mail ist zu kurz.")
        if len(clean_password) < 4:
            raise ValueError("Passwort ist zu kurz.")
        from app.db.tenant_schema import DEFAULT_TENANT_ID
        from app.services.platform_repository import PlatformRepository
        from app.services.tenant_repository import TenantRepository

        tenants = TenantRepository(self.database)
        clean_cohort = cohort_code.strip() if cohort_code else None
        if is_platform_admin:
            role = "admin"
            resolved_tenant = None
        else:
            resolved_tenant = tenant_id or tenants.resolve_tenant_id(
                clean_cohort,
                platform_admin=False,
            )
            if resolved_tenant is None:
                resolved_tenant = DEFAULT_TENANT_ID
            if tenants.get_tenant(resolved_tenant) is None:
                raise ValueError("Mandant nicht gefunden.")
        identifier_hash = self._build_identifier_hash(clean_identifier)
        if self.database.get_learner_by_identifier_hash(identifier_hash):
            raise ValueError("Konto existiert bereits.")
        learner_id = f"learner_{identifier_hash[:16]}"
        labels = {
            "learner": "Azubi",
            "trainer": "Trainer",
            "reviewer": "Reviewer",
            "admin": "Admin",
        }
        label = (display_name or "").strip() or labels[role]
        self.database.upsert_learner(
            learner_id=learner_id,
            identifier_hash=identifier_hash,
            display_name=label,
            role=role,
            cohort_code=clean_cohort,
            tenant_id=resolved_tenant,
            is_platform_admin=is_platform_admin,
            password_hash=self._hash_password(clean_password),
        )
        PlatformRepository(self.database).ensure_learner_defaults(learner_id)
        self.database.record_audit_event(
            event_type="admin.user_created",
            learner_id=learner_id,
            metadata={"role": role, "tenant_id": resolved_tenant},
        )
        row = self.database.get_learner(learner_id)
        if row is None:
            raise ValueError("Konto konnte nicht angelegt werden.")
        return row

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
        return self._session_from_row(token, session_row)

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

    def _session_from_row(
        self,
        token: str,
        session_row: dict[str, Any],
    ) -> LearnerSession:
        """Hydrate a session including tenant metadata."""
        tenant_id = session_row.get("tenant_id")
        is_platform_admin = bool(session_row.get("is_platform_admin"))
        tenant_name = None
        if tenant_id:
            from app.services.tenant_repository import TenantRepository

            tenant = TenantRepository(self.database).get_tenant(str(tenant_id))
            tenant_name = str(tenant["name"]) if tenant else None
        return self._build_session(
            token=token,
            learner_id=str(session_row["learner_id"]),
            display_name=str(session_row["display_name"]),
            cohort_code=session_row.get("cohort_code"),
            role=str(session_row.get("role") or "learner"),
            tenant_id=str(tenant_id) if tenant_id else None,
            is_platform_admin=is_platform_admin,
            tenant_name=tenant_name,
        )

    @staticmethod
    def _build_session(
        *,
        token: str,
        learner_id: str,
        display_name: str,
        cohort_code: str | None,
        role: str,
        tenant_id: str | None,
        is_platform_admin: bool,
        tenant_name: str | None,
    ) -> LearnerSession:
        """Build the public session dataclass."""
        return LearnerSession(
            token=token,
            learner_id=learner_id,
            display_name=display_name,
            cohort_code=cohort_code,
            role=role,
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            is_platform_admin=is_platform_admin,
        )

    def _build_identifier_hash(self, identifier: str) -> str:
        """Build a keyed login hash without storing the raw identifier."""
        return hmac_new(
            self.app_secret.encode("utf-8"),
            identifier.lower().encode("utf-8"),
            sha256,
        ).hexdigest()

    @staticmethod
    def _resolve_role(identifier: str) -> tuple[str, str]:
        """Map demo login prefixes to staff roles."""
        if identifier.startswith("admin-"):
            return "admin", "Admin"
        if identifier.startswith("reviewer-"):
            return "reviewer", "Reviewer"
        if identifier.startswith("trainer-"):
            return "trainer", "Trainer"
        return "learner", "Azubi"

    @staticmethod
    def _requires_initial_password_change(identifier: str) -> bool:
        """Return True when a fresh learner must visit the password screen first."""
        if identifier in {"demo-azubi", "admin-demo", "trainer-demo", "reviewer-demo"}:
            return False
        if identifier.startswith(("admin-", "trainer-", "reviewer-")):
            return False
        return True

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
