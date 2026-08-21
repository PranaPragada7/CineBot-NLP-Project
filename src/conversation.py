from __future__ import annotations

from copy import deepcopy
from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

from src.catalog import DEMO_RATINGS
from src.nlp.pipeline import NLPPipeline
from src.observability import RECOMMENDATION_DURATION
from src.persistence import Database
from src.recommendation import HybridRecommender
from src.response_generator import ResponseGenerator
from src.services.tmdb import TMDbClient


class ConversationManager:
    """Coordinates intent detection, movie retrieval, and session history."""

    def __init__(
        self,
        tmdb_client: TMDbClient | None = None,
        recommender: HybridRecommender | None = None,
        database: Database | None = None,
    ) -> None:
        self.tmdb_client = tmdb_client or TMDbClient()
        self.database = database or Database()
        if recommender is None:
            ratings = deepcopy(DEMO_RATINGS)
            for user_id, user_ratings in self.database.all_ratings().items():
                ratings.setdefault(user_id, {}).update(user_ratings)
            recommender = HybridRecommender(ratings=ratings)
        self.recommender = recommender
        self.pipeline = NLPPipeline(self.tmdb_client.known_titles)
        self.responses = ResponseGenerator()

    @property
    def data_source(self) -> str:
        return self.tmdb_client.source_label

    @property
    def model_info(self) -> dict[str, Any]:
        return self.recommender.model_info

    @property
    def database_status(self) -> dict[str, str]:
        return self.database.health()

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
            recommendations = self.recommendations(
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
            recommendations = self.recommendations(seed_title=movie["title"], user_id=session_id)
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
        nlp_result = self.pipeline.run(user_message)
        title = nlp_result.get("movie_title")
        if not title and nlp_result["intent"] in {"movie_info", "who_directed", "recommend"}:
            last_movie = self.database.last_movie(session_id)
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
        self.database.add_turn(turn, session_id, movie)
        return {**turn, "reply": reply, "suggestions": suggestions}

    def history(self, session_id: str) -> list[dict[str, Any]]:
        return self.database.history(session_id)

    def record_feedback(self, session_id: str, message_id: str, rating: int) -> bool:
        return self.database.record_feedback(session_id, message_id, rating)

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
        started_at = perf_counter()
        with RECOMMENDATION_DURATION.time():
            results = self.recommender.recommend(
                seed_movie_id=seed_movie_id,
                query=query,
                user_id=user_id,
                limit=limit,
            )
        self.database.add_recommendation_event(
            user_id=user_id,
            seed_movie_id=seed_movie_id,
            query=query,
            results=results,
            latency_ms=(perf_counter() - started_at) * 1_000,
        )
        return results

    def record_movie_rating(self, user_id: str, movie_id: int, rating: float) -> None:
        if movie_id not in {int(movie["id"]) for movie in self.recommender.movies}:
            raise KeyError(movie_id)
        if not 1 <= rating <= 5:
            raise ValueError("Ratings must be between 1 and 5.")
        self.database.upsert_rating(user_id, movie_id, rating)
        self.recommender.record_rating(user_id, movie_id, rating)

    def clear(self, session_id: str) -> None:
        self.database.clear_session(session_id)
