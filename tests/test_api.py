from fastapi.testclient import TestClient

from src.app import create_app
from src.conversation import ConversationManager
from src.services.tmdb import TMDbClient


def make_client() -> TestClient:
    manager = ConversationManager(TMDbClient(api_key=""))
    return TestClient(create_app(manager))


def test_health_reports_offline_data_source(monkeypatch):
    monkeypatch.delenv("TMDB_API_KEY", raising=False)
    client = make_client()

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["data_source"] == "built-in offline catalog"
    assert payload["recommender"]["retrieval_index"] in {
        "FAISS IndexFlatIP",
        "NumPy exact fallback (FAISS unavailable)",
    }
    assert payload["recommender"]["collaborative_models"] == ["NMF", "TruncatedSVD"]


def test_chat_history_feedback_and_clear():
    client = make_client()

    chat = client.post(
        "/chat",
        json={"session_id": "session-1", "message": "Who directed Inception?"},
    )
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["intent"] == "who_directed"
    assert "Christopher Nolan" in payload["reply"]

    feedback = client.post(
        "/feedback",
        json={
            "session_id": "session-1",
            "message_id": payload["message_id"],
            "rating": 1,
        },
    )
    assert feedback.status_code == 200
    assert feedback.json() == {"ok": True}

    history = client.get("/history/session-1")
    assert history.status_code == 200
    assert len(history.json()["history"]) == 1

    cleared = client.delete("/history/session-1")
    assert cleared.status_code == 200
    assert client.get("/history/session-1").json() == {"history": []}


def test_feedback_rejects_unknown_message():
    client = make_client()

    response = client.post(
        "/feedback",
        json={"session_id": "missing", "message_id": "unknown", "rating": -1},
    )

    assert response.status_code == 404


def test_chat_validates_blank_messages():
    client = make_client()

    response = client.post(
        "/chat",
        json={"session_id": "session-1", "message": "   "},
    )

    assert response.status_code == 422


def test_recommendation_endpoint_returns_model_signals():
    client = make_client()

    response = client.post(
        "/recommendations",
        json={
            "seed_title": "Arrival",
            "query": "thoughtful science fiction",
            "user_id": "api-user",
            "limit": 3,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["recommendations"]) == 3
    assert "Arrival" not in [movie["title"] for movie in payload["recommendations"]]
    assert set(payload["recommendations"][0]["signals"]) == {
        "semantic",
        "nmf",
        "svd",
        "quality",
    }


def test_rating_endpoint_updates_personalization_model():
    client = make_client()

    saved = client.post("/ratings", json={"user_id": "new-user", "movie_id": 6, "rating": 5})
    recommendations = client.post("/recommendations", json={"user_id": "new-user", "limit": 5})

    assert saved.status_code == 200
    assert saved.json() == {"ok": True}
    assert recommendations.status_code == 200
    assert all(movie["id"] != 6 for movie in recommendations.json()["recommendations"])


def test_recommendation_endpoint_validates_request_and_unknown_movie():
    client = make_client()

    assert client.post("/recommendations", json={}).status_code == 422
    assert (
        client.post("/recommendations", json={"seed_title": "Not A Real Film"}).status_code == 404
    )
    assert (
        client.post("/ratings", json={"user_id": "user", "movie_id": 999, "rating": 4}).status_code
        == 404
    )
