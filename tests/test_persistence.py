import os
from uuid import uuid4

from sqlalchemy import inspect

from src.conversation import ConversationManager
from src.persistence import Database
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
