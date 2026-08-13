"""Alembic migration for organisations (tenants) and class cohorts."""

from __future__ import annotations

from pathlib import Path

from alembic import op

revision = "004_tenants"
down_revision = "003_platform_features"
branch_labels = None
depends_on = None

_SCHEMA_PATH = Path(__file__).resolve().parents[2] / "app" / "db" / "tenant_schema.sql"


def upgrade() -> None:
    """Create tenant tables and learner isolation columns."""
    raw = _SCHEMA_PATH.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in raw.split(";")
        if statement.strip() and not statement.strip().upper().startswith("PRAGMA ")
    ]
    for statement in statements:
        op.execute(statement)
    op.execute("ALTER TABLE learners ADD COLUMN IF NOT EXISTS tenant_id TEXT")
    op.execute(
        "ALTER TABLE learners "
        "ADD COLUMN IF NOT EXISTS is_platform_admin INTEGER NOT NULL DEFAULT 0"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_learners_tenant ON learners (tenant_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_learners_cohort ON learners (cohort_code)"
    )


def downgrade() -> None:
    """Drop tenant tables. Learner columns stay in place."""
    op.execute("DROP TABLE IF EXISTS cohorts")
    op.execute("DROP TABLE IF EXISTS tenants")
