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
    assert response.json() == {
        "status": "ok",
        "data_source": "built-in offline catalog",
    }


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
