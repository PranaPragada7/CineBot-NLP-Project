from src.conversation import ConversationManager
from src.services.tmdb import TMDbClient


def make_manager() -> ConversationManager:
    return ConversationManager(TMDbClient(api_key=""))


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
