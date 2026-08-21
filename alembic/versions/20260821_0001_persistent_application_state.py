"""Create persistent CineBot application tables.

Revision ID: 20260821_0001
Revises:
Create Date: 2026-08-21
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260821_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "conversation_turns",
        sa.Column("message_id", sa.String(length=32), nullable=False),
        sa.Column("session_id", sa.String(length=80), nullable=False),
        sa.Column("user_message", sa.Text(), nullable=False),
        sa.Column("assistant_reply", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=64), nullable=False),
        sa.Column("sentiment", sa.JSON(), nullable=False),
        sa.Column("movie", sa.JSON(), nullable=True),
        sa.Column("feedback", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("message_id"),
    )
    op.create_index("ix_conversation_turns_created_at", "conversation_turns", ["created_at"])
    op.create_index("ix_conversation_turns_intent", "conversation_turns", ["intent"])
    op.create_index("ix_conversation_turns_session_id", "conversation_turns", ["session_id"])

    op.create_table(
        "movie_ratings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "movie_id", name="uq_rating_user_movie"),
    )
    op.create_index("ix_movie_ratings_movie_id", "movie_ratings", ["movie_id"])
    op.create_index("ix_movie_ratings_user_id", "movie_ratings", ["user_id"])

    op.create_table(
        "recommendation_events",
        sa.Column("event_id", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.String(length=80), nullable=True),
        sa.Column("seed_movie_id", sa.Integer(), nullable=True),
        sa.Column("query", sa.Text(), nullable=True),
        sa.Column("result_movie_ids", sa.JSON(), nullable=False),
        sa.Column("latency_ms", sa.Float(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("event_id"),
    )
    op.create_index("ix_recommendation_events_created_at", "recommendation_events", ["created_at"])
    op.create_index("ix_recommendation_events_user_id", "recommendation_events", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_recommendation_events_user_id", table_name="recommendation_events")
    op.drop_index("ix_recommendation_events_created_at", table_name="recommendation_events")
    op.drop_table("recommendation_events")
    op.drop_index("ix_movie_ratings_user_id", table_name="movie_ratings")
    op.drop_index("ix_movie_ratings_movie_id", table_name="movie_ratings")
    op.drop_table("movie_ratings")
    op.drop_index("ix_conversation_turns_session_id", table_name="conversation_turns")
    op.drop_index("ix_conversation_turns_intent", table_name="conversation_turns")
    op.drop_index("ix_conversation_turns_created_at", table_name="conversation_turns")
    op.drop_table("conversation_turns")
