from src.conversation import ConversationManager
from src.persistence import Database
from src.services.tmdb import TMDbClient


def make_manager() -> ConversationManager:
    return ConversationManager(TMDbClient(api_key=""), database=Database.memory())


def test_movie_information_uses_offline_catalog():
    manager = make_manager()

    result = manager.handle_message("session", "Tell me about Arrival")

    assert result["intent"] == "movie_info"
    assert "Denis Villeneuve" not in result["reply"]
    assert "linguist" in result["reply"]


def test_recommendations_exclude_seed_movie():
    manager = make_manager()

    result = manager.handle_message("session", "Recommend movies like Inception")

    assert "If you liked **Inception**" in result["reply"]
    assert "**Inception** (" not in result["reply"].split("try:", 1)[1]


def test_open_ended_recommendation_uses_semantic_query():
    manager = make_manager()

    result = manager.handle_message(
        "session", "Recommend a movie about artificial intelligence and consciousness"
    )

    assert result["intent"] == "recommend"
    assert "Here are matches for your description" in result["reply"]
    assert "Ex Machina" in result["reply"]


def test_follow_up_uses_last_movie_context():
    manager = make_manager()
    manager.handle_message("session", "Tell me about Spirited Away")

    result = manager.handle_message("session", "Who directed that movie?")

    assert "Hayao Miyazaki" in result["reply"]


def test_sessions_are_isolated():
    manager = make_manager()
    manager.handle_message("one", "Hello")

    assert len(manager.history("one")) == 1
    assert manager.history("two") == []


def test_live_search_fallback_does_not_fetch_details_using_a_local_fixture_id(monkeypatch):
    client = TMDbClient(api_key="configured-key")
    requested_paths = []

    def intermittent_response(path, **params):
        requested_paths.append(path)
        if path == "search/movie":
            return None
        # Local Inception is fixture 1, but TMDB movie 1 is an unrelated film.
        return {
            "id": 1,
            "title": "Unrelated remote film",
            "credits": {"crew": [{"job": "Director", "name": "Wrong director"}]},
        }

    monkeypatch.setattr(client, "_get", intermittent_response)
    manager = ConversationManager(client, database=Database.memory())

    result = manager.handle_message("session", "Who directed Inception?")

    assert "Christopher Nolan" in result["reply"]
    assert "Wrong director" not in result["reply"]
    assert requested_paths == ["search/movie"]
