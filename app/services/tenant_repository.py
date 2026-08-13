"""Persistence for organisations (tenants) and class cohorts."""

from __future__ import annotations

from typing import Any

from app.db.tenant_schema import DEFAULT_TENANT_ID
from app.services.database import Database, utc_now_iso


class TenantRepository:
    """CRUD and lookup for tenants and cohorts."""

    def __init__(self, database: Database) -> None:
        """Attach to the application database."""
        self.database = database

    def list_tenants(self, tenant_id: str | None = None) -> list[dict[str, Any]]:
        """Return organisations visible to the caller."""
        with self.database._transaction() as connection:
            if tenant_id:
                rows = connection.execute(
                    """
                    SELECT tenant_id, name, slug, status, created_at
                    FROM tenants
                    WHERE tenant_id = ?
                    """,
                    (tenant_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT tenant_id, name, slug, status, created_at
                    FROM tenants
                    ORDER BY name
                    """
                ).fetchall()
        tenants = [Database._row_dict(row) for row in rows]
        for tenant in tenants:
            tenant["learner_count"] = self._count_learners(tenant["tenant_id"])
            tenant["cohort_count"] = self._count_cohorts(tenant["tenant_id"])
        return tenants

    def get_tenant(self, tenant_id: str) -> dict[str, Any] | None:
        """Return one organisation or None."""
        rows = self.list_tenants(tenant_id)
        return rows[0] if rows else None

    def create_tenant(self, name: str, slug: str) -> dict[str, Any]:
        """Create a new organisation."""
        clean_slug = slug.strip().lower().replace(" ", "-")
        if len(clean_slug) < 3:
            raise ValueError("Mandanten-Kuerzel ist zu kurz.")
        tenant_id = clean_slug
        with self.database._transaction() as connection:
            existing = connection.execute(
                "SELECT tenant_id FROM tenants WHERE slug = ?",
                (clean_slug,),
            ).fetchone()
            if existing:
                raise ValueError("Mandant existiert bereits.")
            connection.execute(
                """
                INSERT INTO tenants (tenant_id, name, slug, status, created_at)
                VALUES (?, ?, ?, 'active', ?)
                """,
                (tenant_id, name.strip(), clean_slug, utc_now_iso()),
            )
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            raise ValueError("Mandant konnte nicht angelegt werden.")
        return tenant

    def list_cohorts(self, tenant_id: str | None = None) -> list[dict[str, Any]]:
        """Return class groups, optionally limited to one organisation."""
        with self.database._transaction() as connection:
            if tenant_id:
                rows = connection.execute(
                    """
                    SELECT cohort_id, tenant_id, code, name, created_at
                    FROM cohorts
                    WHERE tenant_id = ?
                    ORDER BY code
                    """,
                    (tenant_id,),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT cohort_id, tenant_id, code, name, created_at
                    FROM cohorts
                    ORDER BY code
                    """
                ).fetchall()
        cohorts = [Database._row_dict(row) for row in rows]
        for cohort in cohorts:
            cohort["learner_count"] = self._count_learners(
                cohort["tenant_id"],
                cohort["code"],
            )
        return cohorts

    def get_cohort_by_code(self, code: str) -> dict[str, Any] | None:
        """Return a cohort for a login/join code."""
        clean = code.strip()
        if not clean:
            return None
        with self.database._transaction() as connection:
            row = connection.execute(
                """
                SELECT cohort_id, tenant_id, code, name, created_at
                FROM cohorts
                WHERE code = ?
                """,
                (clean,),
            ).fetchone()
        return Database._row_dict(row) if row else None

    def create_cohort(self, tenant_id: str, code: str, name: str) -> dict[str, Any]:
        """Add a class group to an organisation."""
        tenant = self.get_tenant(tenant_id)
        if tenant is None:
            raise ValueError("Mandant nicht gefunden.")
        clean_code = code.strip().upper()
        if len(clean_code) < 3:
            raise ValueError("Kohortencode ist zu kurz.")
        cohort_id = clean_code.lower().replace(" ", "-")
        with self.database._transaction() as connection:
            existing = connection.execute(
                "SELECT cohort_id FROM cohorts WHERE code = ?",
                (clean_code,),
            ).fetchone()
            if existing:
                raise ValueError("Kohortencode ist bereits vergeben.")
            connection.execute(
                """
                INSERT INTO cohorts (cohort_id, tenant_id, code, name, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (cohort_id, tenant_id, clean_code, name.strip(), utc_now_iso()),
            )
        cohort = self.get_cohort_by_code(clean_code)
        if cohort is None:
            raise ValueError("Kohorte konnte nicht angelegt werden.")
        return cohort

    def resolve_tenant_id(
        self,
        cohort_code: str | None,
        *,
        platform_admin: bool,
    ) -> str | None:
        """Map a cohort code to a tenant, or the default BZE tenant."""
        if platform_admin:
            return None
        if cohort_code:
            cohort = self.get_cohort_by_code(cohort_code)
            if cohort:
                return str(cohort["tenant_id"])
        return DEFAULT_TENANT_ID

    def _count_learners(
        self,
        tenant_id: str,
        cohort_code: str | None = None,
    ) -> int:
        """Count active accounts in a tenant or cohort."""
        with self.database._transaction() as connection:
            if cohort_code:
                row = connection.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM learners
                    WHERE deleted_at IS NULL
                        AND tenant_id = ?
                        AND cohort_code = ?
                    """,
                    (tenant_id, cohort_code),
                ).fetchone()
            else:
                row = connection.execute(
                    """
                    SELECT COUNT(*) AS count
                    FROM learners
                    WHERE deleted_at IS NULL AND tenant_id = ?
                    """,
                    (tenant_id,),
                ).fetchone()
        return int(row["count"] if not isinstance(row, tuple) else row[0])

    def _count_cohorts(self, tenant_id: str) -> int:
        """Count class groups in one organisation."""
        with self.database._transaction() as connection:
            row = connection.execute(
                "SELECT COUNT(*) AS count FROM cohorts WHERE tenant_id = ?",
                (tenant_id,),
            ).fetchone()
        return int(row["count"] if not isinstance(row, tuple) else row[0])
