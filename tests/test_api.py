from __future__ import annotations

import os
from typing import Any

from fastapi.testclient import TestClient

import src.app as app_module


class FakePipeline:
    def run(self, text: str, ctx: dict[str, Any]) -> dict[str, Any]:
        return {
            "intent": "fallback",
            "intent_confidence": 0.99,
            "entities": {"movies": [], "people": []},
            "sentiment": {"negative": 0.01, "neutral": 0.5, "positive": 0.49},
        }


def test_chat_and_feedback():
    os.environ["TMDB_API_KEY"] = "test_key"
    app_module.pipeline = FakePipeline()
    client = TestClient(app_module.app)

    r = client.post("/chat", json={"session_id": "t1", "message": "hello"})
    assert r.status_code == 200
    data = r.json()
    assert "reply" in data and "message_id" in data

    r2 = client.post(
        "/feedback",
        json={"session_id": "t1", "message_id": data["message_id"], "rating": 1},
    )
    assert r2.status_code == 200
    assert r2.json()["ok"] is True

    r3 = client.get("/history/t1")
    assert r3.status_code == 200
    hist = r3.json()
    assert "history" in hist
