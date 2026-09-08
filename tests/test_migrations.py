"""Check session schema upgrades without discarding legacy conversation data."""

from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from alembic import command
from src.persistence import Database


def test_session_migration_preserves_existing_data(tmp_path, monkeypatch):
    url = f"sqlite+pysqlite:///{(tmp_path / 'migrate.db').as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "20260821_0001")
    engine = create_engine(url)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO movie_ratings (user_id, movie_id, rating, created_at, updated_at) "
                "VALUES ('legacy', 6, 5, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            )
        )
    command.upgrade(config, "head")
    command.check(config)
    database = Database(url, create_schema=False)
    credentials = database.issue_session()
    assert database.authenticate_session(credentials["access_token"]) == credentials["session_id"]
    assert database.all_ratings() == {"legacy": {6: 5.0}}
    database.engine.dispose()
    command.downgrade(config, "20260821_0001")
    assert "visitor_sessions" not in inspect(engine).get_table_names()
    command.upgrade(config, "head")
    assert "visitor_sessions" in inspect(engine).get_table_names()
    engine.dispose()
