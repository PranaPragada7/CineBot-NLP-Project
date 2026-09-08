"""Add bearer credentials for server-issued anonymous visitor identities."""

import sqlalchemy as sa

from alembic import op

revision = "20260906_0002"
down_revision = "20260821_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "visitor_sessions",
        sa.Column("session_id", sa.String(32), primary_key=True),
        sa.Column("token_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_visitor_sessions_expires_at", "visitor_sessions", ["expires_at"])


def downgrade() -> None:
    op.drop_table("visitor_sessions")
