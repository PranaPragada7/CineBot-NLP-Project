import hashlib
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from sqlalchemy import inspect, select, update

from src.conversation import ConversationManager
from src.persistence import Database, VisitorSession
from src.services.tmdb import TMDbClient


def infrastructure_database() -> Database:
    database_url = os.getenv("DATABASE_URL")
    return Database(database_url, create_schema=False) if database_url else Database.memory()


def test_required_tables_exist_and_database_is_ready():
    database = infrastructure_database()

    assert database.health()["status"] == "ok"
    assert {
        "conversation_turns",
        "movie_ratings",
        "recommendation_events",
    }.issubset(inspect(database.engine).get_table_names())


def test_history_context_and_rating_survive_manager_restart(tmp_path):
    database_url = os.getenv("DATABASE_URL") or (
        f"sqlite+pysqlite:///{(tmp_path / 'restart.db').as_posix()}"
    )
    create_schema = not bool(os.getenv("DATABASE_URL"))
    first_database = Database(database_url, create_schema=create_schema)
    identity = uuid4().hex
    session_id = f"restart-{identity}"
    user_id = f"user-{identity}"
    first_manager = ConversationManager(TMDbClient(api_key=""), database=first_database)

    first_manager.handle_message(session_id, "Tell me about Spirited Away")
    first_manager.record_movie_rating(user_id, movie_id=6, rating=5)

    restarted_database = Database(database_url, create_schema=create_schema)
    restarted_manager = ConversationManager(TMDbClient(api_key=""), database=restarted_database)
    follow_up = restarted_manager.handle_message(session_id, "Who directed that movie?")
    recommendations = restarted_manager.recommendations(user_id=user_id, limit=5)

    assert "Hayao Miyazaki" in follow_up["reply"]
    assert len(restarted_manager.history(session_id)) == 2
    assert all(movie["id"] != 6 for movie in recommendations)
    assert restarted_manager.model_info["interaction_count"] == 145


def test_visitor_tokens_are_hashed_persistent_and_expire(tmp_path):
    database_url = os.getenv("DATABASE_URL") or (
        f"sqlite+pysqlite:///{(tmp_path / 'sessions.db').as_posix()}"
    )
    database = Database(database_url, create_schema=not bool(os.getenv("DATABASE_URL")))
    credentials = database.issue_session()
    token = credentials["access_token"]
    with database.session() as session:
        stored = session.scalar(
            select(VisitorSession).where(VisitorSession.session_id == credentials["session_id"])
        )
        assert stored.token_hash == hashlib.sha256(token.encode()).hexdigest()
        assert stored.token_hash != token
    restarted = Database(database_url, create_schema=False)
    assert restarted.authenticate_session(token) == credentials["session_id"]
    assert restarted.authenticate_session("wrong-token") is None
    assert restarted.authenticate_session("x" * 129) is None
    with database.session() as session:
        session.execute(
            update(VisitorSession)
            .where(VisitorSession.session_id == credentials["session_id"])
            .values(expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )
    assert restarted.authenticate_session(token) is None


def test_movie_context_survives_non_movie_turns():
    from sqlalchemy import null

    from src.persistence import ConversationTurn

    database = infrastructure_database()
    manager = ConversationManager(TMDbClient(api_key=""), database=database)
    identity = uuid4().hex
    try:
        manager.handle_message(identity, "Tell me about Spirited Away")
        manager.handle_message(identity, "Hello")
        assert database.last_movie(identity)["title"] == "Spirited Away"
        # Existing SQL NULL rows must be skipped along with JSON null rows.
        with database.session() as session:
            session.add(
                ConversationTurn(
                    message_id=uuid4().hex,
                    session_id=identity,
                    user_message="hello",
                    assistant_reply="hi",
                    intent="greeting",
                    sentiment={},
                    movie=null(),
                )
            )
        follow_up = manager.handle_message(identity, "Who directed that movie?")
        assert "Hayao Miyazaki" in follow_up["reply"]
    finally:
        database.clear_session(identity)
