"""Alembic migration for Berichtsheft entries."""

from __future__ import annotations

from alembic import op

revision = "002_training_reports"
down_revision = "001_content_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add training_reports table for Berichtsheft entries."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS training_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            learner_id TEXT NOT NULL,
            report_date TEXT NOT NULL,
            activities TEXT NOT NULL,
            hours REAL NOT NULL DEFAULT 8.0,
            status TEXT NOT NULL DEFAULT 'draft',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (learner_id) REFERENCES learners (learner_id)
                ON DELETE CASCADE
        )
        """
    )


def downgrade() -> None:
    """Drop Berichtsheft table."""
    op.execute("DROP TABLE IF EXISTS training_reports")
