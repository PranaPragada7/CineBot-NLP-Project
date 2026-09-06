from pathlib import Path

import requests
from streamlit.testing.v1 import AppTest


class HealthResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, str]:
        return {"status": "ok", "data_source": "built-in offline catalog"}


def test_streamlit_app_loads(monkeypatch):
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: HealthResponse())
    app_path = Path(__file__).resolve().parents[1] / "src" / "frontend" / "streamlit_app.py"

    app = AppTest.from_file(str(app_path)).run(timeout=10)

    assert not app.exception
    assert any("Find the next film worth your time" in item.value for item in app.markdown)
    assert [tab.label for tab in app.tabs] == [
        "✦ Movie assistant",
        "◎ Recommendation lab",
    ]
    assert any(button.label == "Clear conversation" for button in app.button)
    assert app.chat_input[0].placeholder == "Ask about a movie, director, genre, or mood…"


def test_chat_uses_server_identity_and_clear_sends_bearer_token(monkeypatch):
    calls = []

    class Reply(HealthResponse):
        status_code = 200

        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    def issue(url, **kwargs):
        assert url.endswith("/sessions")
        return Reply({"session_id": "server-id", "access_token": "private-token"})

    def request(method, url, **kwargs):
        calls.append((method, url, kwargs))
        assert kwargs["headers"] == {"Authorization": "Bearer private-token"}
        if method == "POST":
            assert kwargs["json"]["session_id"] == "server-id"
            return Reply({"reply": "Hello, movie fan!", "suggestions": []})
        assert url.endswith("/history/server-id")
        return Reply({"ok": True})

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: HealthResponse())
    monkeypatch.setattr(requests, "post", issue)
    monkeypatch.setattr(requests, "request", request)
    path = Path(__file__).resolve().parents[1] / "src/frontend/streamlit_app.py"
    app = AppTest.from_file(str(path)).run(timeout=10)
    app.chat_input[0].set_value("Hello").run(timeout=10)
    assert not app.exception
    assert any("Hello, movie fan!" in item.value for item in app.markdown)
    assert all("private-token" not in item.value for item in app.markdown)
    next(button for button in app.button if button.label == "Clear conversation").click().run()
    assert not app.exception
    assert [call[0] for call in calls] == ["POST", "DELETE"]


def test_recommendation_and_rating_use_owned_identity(monkeypatch):
    calls = []

    class Reply(HealthResponse):
        status_code = 200

        def __init__(self, payload):
            self.payload = payload

        def json(self):
            return self.payload

    def request(method, url, **kwargs):
        calls.append(url)
        assert kwargs["headers"] == {"Authorization": "Bearer private-token"}
        assert kwargs["json"]["user_id"] == "server-id"
        if url.endswith("/recommendations"):
            return Reply({"recommendations": [{"id": 6, "title": "Arrival"}]})
        assert url.endswith("/ratings")
        return Reply({"ok": True})

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: HealthResponse())
    monkeypatch.setattr(
        requests,
        "post",
        lambda *args, **kwargs: Reply({"session_id": "server-id", "access_token": "private-token"}),
    )
    monkeypatch.setattr(requests, "request", request)
    path = Path(__file__).resolve().parents[1] / "src/frontend/streamlit_app.py"
    app = AppTest.from_file(str(path)).run(timeout=10)
    next(item for item in app.text_input if item.label == "Seed movie").set_value("Inception")
    next(item for item in app.button if item.label == "Generate recommendations").click().run()
    assert not app.exception
    next(item for item in app.button if item.label == "Add to taste profile").click().run()
    assert not app.exception
    assert len(calls) == 2


def test_expired_ui_session_is_reset_without_automatically_retrying(monkeypatch):
    class Expired(HealthResponse):
        status_code = 401

        def raise_for_status(self):
            raise requests.HTTPError("expired")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: HealthResponse())
    monkeypatch.setattr(requests, "request", lambda *args, **kwargs: Expired())
    path = Path(__file__).resolve().parents[1] / "src/frontend/streamlit_app.py"
    app = AppTest.from_file(str(path)).run(timeout=10)
    app.session_state["access_token"] = "expired-token"
    app.session_state["session_id"] = "expired-session"
    app.chat_input[0].set_value("Hello").run(timeout=10)
    assert not app.exception
    assert app.session_state["access_token"] is None
    assert app.session_state["session_id"] is None
    assert any("expired" in item.value for item in app.warning)
