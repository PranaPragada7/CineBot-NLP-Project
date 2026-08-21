from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from typing import Any
from uuid import uuid4

from src.nlp.pipeline import NLPPipeline
from src.recommendation import HybridRecommender
from src.response_generator import ResponseGenerator
from src.services.tmdb import TMDbClient


class ConversationManager:
    """Coordinates intent detection, movie retrieval, and session history."""

    def __init__(
        self,
        tmdb_client: TMDbClient | None = None,
        recommender: HybridRecommender | None = None,
    ) -> None:
        self.tmdb_client = tmdb_client or TMDbClient()
        self.recommender = recommender or HybridRecommender()
        self.pipeline = NLPPipeline(self.tmdb_client.known_titles)
        self.responses = ResponseGenerator()
        self._sessions: dict[str, dict[str, Any]] = {}
        self._lock = RLock()

    @property
    def data_source(self) -> str:
        return self.tmdb_client.source_label

    @property
    def model_info(self) -> dict[str, Any]:
        return self.recommender.model_info

    def _session(self, session_id: str) -> dict[str, Any]:
        with self._lock:
            return self._sessions.setdefault(
                session_id,
                {"last_movie": None, "history": [], "feedback": {}},
            )

    def _resolve_movie(self, title: str | None) -> dict[str, Any] | None:
        return self.tmdb_client.search_movie(title) if title else None

    def _reply(
        self,
        intent: str,
        title: str | None,
        session_id: str,
        user_message: str,
    ) -> tuple[str, dict[str, Any] | None, list[str]]:
        movie = self._resolve_movie(title)
        default_suggestions = [
            "What is trending?",
            "Who directed Inception?",
            "Recommend movies like Arrival",
        ]

        if intent == "greet":
            return self.responses.welcome(), None, default_suggestions
        if intent == "help":
            return self.responses.help_text(), None, default_suggestions
        if intent == "upcoming_releases":
            heading = (
                "Here are upcoming releases from TMDB:"
                if self.tmdb_client.is_live
                else "Live release data needs a TMDB key. Here are offline catalog picks:"
            )
            return (
                self.responses.movie_list(heading, self.tmdb_client.upcoming_movies()),
                None,
                default_suggestions,
            )
        if intent == "trending":
            heading = (
                "Trending on TMDB this week:"
                if self.tmdb_client.is_live
                else "Top-rated titles in the offline catalog:"
            )
            return (
                self.responses.movie_list(heading, self.tmdb_client.trending_movies()),
                None,
                default_suggestions,
            )
        if intent == "recommend" and not title:
            recommendations = self.recommender.recommend(
                query=user_message,
                user_id=session_id,
            )
            if recommendations and recommendations[0]["signals"]["semantic"] > 0:
                return (
                    self.responses.movie_list(
                        "Here are matches for your description:", recommendations
                    ),
                    None,
                    default_suggestions,
                )
            return self.responses.missing_title("find similar titles"), None, default_suggestions
        if intent in {"movie_info", "who_directed"} and not title:
            action = {
                "movie_info": "look it up",
                "who_directed": "find its director",
            }[intent]
            return self.responses.missing_title(action), None, default_suggestions
        if intent in {"movie_info", "who_directed", "recommend"} and not movie:
            return self.responses.not_found(title or "that title"), None, default_suggestions
        if intent == "movie_info" and movie:
            details = self.tmdb_client.movie_details(movie["id"]) or movie
            suggestions = [
                f"Who directed {details['title']}?",
                f"Recommend movies like {details['title']}",
                "What is trending?",
            ]
            return self.responses.movie_info(details), details, suggestions
        if intent == "who_directed" and movie:
            details = self.tmdb_client.movie_details(movie["id"]) or movie
            return self.responses.director(details), details, default_suggestions
        if intent == "recommend" and movie:
            recommendations = self.recommender.recommend_by_title(
                movie["title"], user_id=session_id
            )
            if not recommendations:
                recommendations = self.tmdb_client.similar_movies(movie["id"])
            return (
                self.responses.movie_list(
                    f"If you liked **{movie['title']}**, try:", recommendations
                ),
                movie,
                default_suggestions,
            )
        return self.responses.fallback(), None, default_suggestions

    def handle_message(self, session_id: str, user_message: str) -> dict[str, Any]:
        state = self._session(session_id)
        nlp_result = self.pipeline.run(user_message)
        title = nlp_result.get("movie_title")
        if not title and nlp_result["intent"] in {"movie_info", "who_directed", "recommend"}:
            last_movie = state.get("last_movie")
            if last_movie and any(
                pronoun in user_message.casefold() for pronoun in ("it", "that movie", "that one")
            ):
                title = last_movie["title"]

        reply, movie, suggestions = self._reply(
            nlp_result["intent"], title, session_id, user_message
        )
        message_id = uuid4().hex
        turn = {
            "message_id": message_id,
            "user": user_message,
            "assistant": reply,
            "intent": nlp_result["intent"],
            "sentiment": nlp_result["sentiment"],
            "created_at": datetime.now(UTC).isoformat(),
        }
        with self._lock:
            state["history"].append(turn)
            if movie:
                state["last_movie"] = movie
        return {**turn, "reply": reply, "suggestions": suggestions}

    def history(self, session_id: str) -> list[dict[str, Any]]:
        with self._lock:
            state = self._sessions.get(session_id)
            return [dict(turn) for turn in state["history"]] if state else []

    def record_feedback(self, session_id: str, message_id: str, rating: int) -> bool:
        with self._lock:
            state = self._sessions.get(session_id)
            if not state or not any(turn["message_id"] == message_id for turn in state["history"]):
                return False
            state["feedback"][message_id] = rating
            return True

    def recommendations(
        self,
        *,
        seed_title: str | None = None,
        query: str | None = None,
        user_id: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        seed_movie = self.tmdb_client.search_movie(seed_title) if seed_title else None
        if seed_title and not seed_movie:
            return []
        seed_movie_id = (
            self.recommender.movie_id_for_title(seed_movie["title"]) if seed_movie else None
        )
        if seed_title and seed_movie_id is None:
            return []
        return self.recommender.recommend(
            seed_movie_id=seed_movie_id,
            query=query,
            user_id=user_id,
            limit=limit,
        )

    def record_movie_rating(self, user_id: str, movie_id: int, rating: float) -> None:
        self.recommender.record_rating(user_id, movie_id, rating)

    def clear(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
