from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Float,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    delete,
    select,
    text,
)
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool


class Base(DeclarativeBase):
    pass


class ConversationTurn(Base):
    __tablename__ = "conversation_turns"

    message_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    session_id: Mapped[str] = mapped_column(String(80), index=True)
    user_message: Mapped[str] = mapped_column(Text)
    assistant_reply: Mapped[str] = mapped_column(Text)
    intent: Mapped[str] = mapped_column(String(64), index=True)
    sentiment: Mapped[dict[str, Any]] = mapped_column(JSON)
    movie: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    feedback: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )


class MovieRating(Base):
    __tablename__ = "movie_ratings"
    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="uq_rating_user_movie"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(80), index=True)
    movie_id: Mapped[int] = mapped_column(Integer, index=True)
    rating: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )


class RecommendationEvent(Base):
    __tablename__ = "recommendation_events"

    event_id: Mapped[str] = mapped_column(String(32), primary_key=True, default=lambda: uuid4().hex)
    user_id: Mapped[str | None] = mapped_column(String(80), nullable=True, index=True)
    seed_movie_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    query: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_movie_ids: Mapped[list[int]] = mapped_column(JSON)
    latency_ms: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), index=True
    )


class Database:
    """Small SQLAlchemy repository used by the API and integration tests."""

    def __init__(self, url: str | None = None, *, create_schema: bool | None = None) -> None:
        self.url = self.normalize_url(
            url or os.getenv("DATABASE_URL") or "sqlite+pysqlite:///./data/cinebot.db"
        )
        engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
        parsed_url = make_url(self.url)
        if parsed_url.get_backend_name() == "sqlite":
            engine_kwargs["connect_args"] = {"check_same_thread": False}
            if ":memory:" in self.url:
                engine_kwargs["poolclass"] = StaticPool
            elif parsed_url.database:
                Path(parsed_url.database).parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(self.url, **engine_kwargs)
        self._session_factory = sessionmaker(self.engine, expire_on_commit=False)
        should_create_schema = (
            create_schema
            if create_schema is not None
            else os.getenv("AUTO_CREATE_SCHEMA", "false").casefold() == "true"
        )
        if should_create_schema:
            Base.metadata.create_all(self.engine)

    @staticmethod
    def normalize_url(url: str) -> str:
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+psycopg://", 1)
        return url

    @classmethod
    def memory(cls) -> Database:
        return cls("sqlite+pysqlite:///:memory:", create_schema=True)

    @contextmanager
    def session(self) -> Iterator[Session]:
        active_session = self._session_factory()
        try:
            yield active_session
            active_session.commit()
        except Exception:
            active_session.rollback()
            raise
        finally:
            active_session.close()

    @property
    def backend(self) -> str:
        return self.engine.url.get_backend_name()

    def health(self) -> dict[str, str]:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return {"status": "ok", "backend": self.backend}
        except Exception:
            return {"status": "unavailable", "backend": self.backend}

    def add_turn(self, turn: dict[str, Any], session_id: str, movie: dict[str, Any] | None) -> None:
        created_at = datetime.fromisoformat(turn["created_at"])
        with self.session() as active_session:
            active_session.add(
                ConversationTurn(
                    message_id=turn["message_id"],
                    session_id=session_id,
                    user_message=turn["user"],
                    assistant_reply=turn["assistant"],
                    intent=turn["intent"],
                    sentiment=turn["sentiment"],
                    movie=movie,
                    created_at=created_at,
                )
            )

    def history(self, session_id: str) -> list[dict[str, Any]]:
        with self.session() as active_session:
            turns = active_session.scalars(
                select(ConversationTurn)
                .where(ConversationTurn.session_id == session_id)
                .order_by(ConversationTurn.created_at, ConversationTurn.message_id)
            ).all()
            return [
                {
                    "message_id": turn.message_id,
                    "user": turn.user_message,
                    "assistant": turn.assistant_reply,
                    "intent": turn.intent,
                    "sentiment": turn.sentiment,
                    "created_at": turn.created_at.isoformat(),
                }
                for turn in turns
            ]

    def last_movie(self, session_id: str) -> dict[str, Any] | None:
        with self.session() as active_session:
            turn = active_session.scalar(
                select(ConversationTurn)
                .where(
                    ConversationTurn.session_id == session_id,
                    ConversationTurn.movie.is_not(None),
                )
                .order_by(ConversationTurn.created_at.desc(), ConversationTurn.message_id.desc())
                .limit(1)
            )
            return dict(turn.movie) if turn and turn.movie else None

    def record_feedback(self, session_id: str, message_id: str, rating: int) -> bool:
        with self.session() as active_session:
            turn = active_session.scalar(
                select(ConversationTurn).where(
                    ConversationTurn.session_id == session_id,
                    ConversationTurn.message_id == message_id,
                )
            )
            if turn is None:
                return False
            turn.feedback = rating
            return True

    def clear_session(self, session_id: str) -> None:
        with self.session() as active_session:
            active_session.execute(
                delete(ConversationTurn).where(ConversationTurn.session_id == session_id)
            )

    def all_ratings(self) -> dict[str, dict[int, float]]:
        with self.session() as active_session:
            ratings: dict[str, dict[int, float]] = {}
            for row in active_session.scalars(select(MovieRating)).all():
                ratings.setdefault(row.user_id, {})[row.movie_id] = row.rating
            return ratings

    def upsert_rating(self, user_id: str, movie_id: int, rating: float) -> None:
        with self.session() as active_session:
            values = {
                "user_id": user_id,
                "movie_id": movie_id,
                "rating": rating,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
            }
            if self.backend == "postgresql":
                statement = postgresql_insert(MovieRating).values(**values)
                active_session.execute(
                    statement.on_conflict_do_update(
                        constraint="uq_rating_user_movie",
                        set_={"rating": rating, "updated_at": datetime.now(UTC)},
                    )
                )
                return
            if self.backend == "sqlite":
                statement = sqlite_insert(MovieRating).values(**values)
                active_session.execute(
                    statement.on_conflict_do_update(
                        index_elements=["user_id", "movie_id"],
                        set_={"rating": rating, "updated_at": datetime.now(UTC)},
                    )
                )
                return
            row = active_session.scalar(
                select(MovieRating).where(
                    MovieRating.user_id == user_id,
                    MovieRating.movie_id == movie_id,
                )
            )
            if row is None:
                active_session.add(MovieRating(user_id=user_id, movie_id=movie_id, rating=rating))
            else:
                row.rating = rating
                row.updated_at = datetime.now(UTC)

    def add_recommendation_event(
        self,
        *,
        user_id: str | None,
        seed_movie_id: int | None,
        query: str | None,
        results: list[dict[str, Any]],
        latency_ms: float,
    ) -> None:
        with self.session() as active_session:
            active_session.add(
                RecommendationEvent(
                    user_id=user_id,
                    seed_movie_id=seed_movie_id,
                    query=query,
                    result_movie_ids=[int(movie["id"]) for movie in results],
                    latency_ms=latency_ms,
                )
            )
