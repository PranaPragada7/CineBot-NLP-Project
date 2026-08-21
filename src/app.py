from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field, field_validator, model_validator

from src.conversation import ConversationManager

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
LOGGER = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=1_500)

    @field_validator("session_id", "message")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value


class ChatResponse(BaseModel):
    reply: str
    message_id: str
    intent: str
    sentiment: dict[str, Any]
    suggestions: list[str]


class FeedbackRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=80)
    message_id: str = Field(min_length=1, max_length=80)
    rating: int = Field(ge=-1, le=1)


class RecommendationRequest(BaseModel):
    seed_title: str | None = Field(default=None, min_length=1, max_length=200)
    query: str | None = Field(default=None, min_length=1, max_length=500)
    user_id: str | None = Field(default=None, min_length=1, max_length=80)
    limit: int = Field(default=5, ge=1, le=10)

    @model_validator(mode="after")
    def require_recommendation_signal(self) -> RecommendationRequest:
        if not self.seed_title and not self.query and not self.user_id:
            raise ValueError("Provide a seed title, natural-language query, or user ID.")
        return self


class MovieRatingRequest(BaseModel):
    user_id: str = Field(min_length=1, max_length=80)
    movie_id: int = Field(gt=0)
    rating: float = Field(ge=1, le=5)


def create_app(manager: ConversationManager | None = None) -> FastAPI:
    app = FastAPI(
        title="CineBot API",
        description=(
            "Movie discovery API with FAISS retrieval, NMF/SVD recommendations, "
            "and TMDB metadata."
        ),
        version="3.0.0",
    )
    app.state.manager = manager or ConversationManager()

    @app.get("/health")
    def health_check(request: Request) -> dict[str, Any]:
        active_manager: ConversationManager = request.app.state.manager
        return {
            "status": "ok",
            "data_source": active_manager.data_source,
            "recommender": active_manager.model_info,
        }

    @app.post("/chat", response_model=ChatResponse)
    def chat_endpoint(payload: ChatRequest, request: Request) -> dict[str, Any]:
        active_manager: ConversationManager = request.app.state.manager
        try:
            return active_manager.handle_message(payload.session_id, payload.message)
        except Exception as exc:  # pragma: no cover - defensive API boundary
            LOGGER.exception("Chat request failed", exc_info=exc)
            raise HTTPException(status_code=500, detail="Unable to process the request.") from exc

    @app.post("/feedback")
    def feedback_endpoint(payload: FeedbackRequest, request: Request) -> dict[str, bool]:
        active_manager: ConversationManager = request.app.state.manager
        saved = active_manager.record_feedback(
            payload.session_id,
            payload.message_id,
            payload.rating,
        )
        if not saved:
            raise HTTPException(status_code=404, detail="Message was not found.")
        return {"ok": True}

    @app.post("/recommendations")
    def recommendations_endpoint(
        payload: RecommendationRequest, request: Request
    ) -> dict[str, Any]:
        active_manager: ConversationManager = request.app.state.manager
        recommendations = active_manager.recommendations(
            seed_title=payload.seed_title,
            query=payload.query,
            user_id=payload.user_id,
            limit=payload.limit,
        )
        if payload.seed_title and not recommendations:
            raise HTTPException(status_code=404, detail="Seed movie was not found in the catalog.")
        return {"recommendations": recommendations, "model": active_manager.model_info}

    @app.post("/ratings")
    def movie_rating_endpoint(payload: MovieRatingRequest, request: Request) -> dict[str, bool]:
        active_manager: ConversationManager = request.app.state.manager
        try:
            active_manager.record_movie_rating(payload.user_id, payload.movie_id, payload.rating)
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="Movie was not found in the catalog."
            ) from exc
        return {"ok": True}

    @app.get("/history/{session_id}")
    def history_endpoint(session_id: str, request: Request) -> dict[str, Any]:
        active_manager: ConversationManager = request.app.state.manager
        return {"history": active_manager.history(session_id)}

    @app.delete("/history/{session_id}")
    def clear_history_endpoint(session_id: str, request: Request) -> dict[str, bool]:
        active_manager: ConversationManager = request.app.state.manager
        active_manager.clear(session_id)
        return {"ok": True}

    return app


app = create_app()
