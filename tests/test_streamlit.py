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
